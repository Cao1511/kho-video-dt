#!/usr/bin/env python3
"""Chay cac lenh dang web mayducthanh.vn tu GitHub Actions.

Doc moi file web-jobs/*.json chua co ket qua, goi WordPress REST API bang
Mat khau ung dung (lay tu GitHub Secrets WP_USER / WP_APP_PASSWORD),
ghi ket qua vao web-results/<ten>.json roi xoa file lenh.

Dinh dang file lenh:
{
  "steps": [
    {"id": "anh1", "method": "POST", "path": "/wp/v2/media",
     "file": "anh/may-vien-nap/1.webp", "filename": "may-vien-nap.webp",
     "pick": ["id", "source_url"]},
    {"id": "sp", "method": "POST", "path": "/wc/v3/products",
     "body": {"name": "...", "status": "draft", "images": [{"id": "{{anh1.id}}"}]},
     "pick": ["id", "permalink", "status"]},
    {"warm": ["/", "{{sp.permalink}}"]}
  ]
}
- "path" la duong dan sau /wp-json.
- "{{buoc.truong}}" duoc thay bang ket qua cua buoc truoc.
- "pick" chi giu cac truong can (kho cong khai, khong ghi het du lieu).
- "sheet": true -> doc Google Sheet DS mau may (STT, ten, link, trang thai...).
- "sheet_update": [{"stt":"3","fields":{"Tên máy":"...","Trạng thái":"Đã đăng","Thời gian đăng":"...","Link web":"https://...","Link Facebook":"https://..."}}]
  -> ghi vao Sheet (khong ghi de Tên máy nguoi dung da dien, tru khi "ghi_de_ten": true).
- "wait": so giay cho (toi da 60).
- "warm": mo trang nhu khach (khong dang nhap) 2 lan de nap cache.
"""
import base64, glob, json, mimetypes, os, re, sys, time
import urllib.request, urllib.error

SITE = "https://mayducthanh.vn"
UA = "DucThanh-GitHub-Runner/1.0"
AUTH = "Basic " + base64.b64encode(
    f"{os.environ.get('WP_USER','')}:{os.environ.get('WP_APP_PASSWORD','').replace(' ', '')}".encode()
).decode()


def call(method, url, data=None, headers=None, auth=True, timeout=120):
    h = {"User-Agent": UA}
    if auth:
        h["Authorization"] = AUTH
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def subst(obj, ctx):
    if isinstance(obj, str):
        m = re.fullmatch(r"\{\{(\w+)\.(\w+)\}\}", obj)
        if m:
            return ctx.get(m[1], {}).get(m[2])
        return re.sub(r"\{\{(\w+)\.(\w+)\}\}",
                      lambda m: str(ctx.get(m[1], {}).get(m[2], "")), obj)
    if isinstance(obj, list):
        return [subst(x, ctx) for x in obj]
    if isinstance(obj, dict):
        return {k: subst(v, ctx) for k, v in obj.items()}
    return obj


def pick(data, fields):
    if fields is None:
        return None
    if isinstance(data, list):
        return [pick(x, fields) for x in data]
    if isinstance(data, dict):
        return {f: data.get(f) for f in fields}
    return data


def run_step(step, ctx):
    step = subst(step, ctx)
    if "sheet" in step:
        # tai Google Sheet "DS mau may" (cong khai) dang CSV
        import csv, io
        url = "https://docs.google.com/spreadsheets/d/1Zwy4QBWBwFZ-wzkURH7--dRxB_BRhgOw_Tzt-1zzDVg/export?format=csv&gid=0"
        st, body, _ = call("GET", url, auth=False)
        rows = list(csv.reader(io.StringIO(body.decode("utf-8", "replace"))))
        head = [h.strip() for h in rows[1]] if len(rows) > 1 else []
        def col(r, name, i):
            j = head.index(name) if name in head else i
            return r[j].strip() if j < len(r) else ""
        out = [{"stt": r[0].strip(), "ten": col(r, "Tên máy", 1), "link": col(r, "Link mẫu/thông số", 2),
                "trang_thai": col(r, "Trạng thái", 4), "thoi_gian": col(r, "Thời gian đăng", 5)}
               for r in rows[2:] if len(r) >= 3 and r[0].strip() and (r[1].strip() or r[2].strip())]
        return {"ok": st == 200, "status": st, "data": out, "head": [[h, h.encode("unicode_escape").decode()] for h in head]}
    if "sheet_update" in step:
        # ghi vao Google Sheet qua Apps Script (secret SHEET_URL, SHEET_KEY)
        url, key = os.environ.get("SHEET_URL", ""), os.environ.get("SHEET_KEY", "")
        if not url or not key:
            return {"ok": False, "error": "chua cai SHEET_URL/SHEET_KEY tren GitHub"}
        # do ten cot that trong Sheet (co the co dau cach thua / go kieu to hop) va giu ten may nguoi dung da dien
        import csv, io, unicodedata
        norm = lambda t: unicodedata.normalize("NFC", str(t)).strip().lower()
        surl = "https://docs.google.com/spreadsheets/d/1Zwy4QBWBwFZ-wzkURH7--dRxB_BRhgOw_Tzt-1zzDVg/export?format=csv&gid=0"
        _, sb, _ = call("GET", surl, auth=False)
        rows = list(csv.reader(io.StringIO(sb.decode("utf-8", "replace"))))
        raw_head = rows[1] if len(rows) > 1 else []
        hmap = {norm(h): h for h in raw_head}
        cur = {r[0].strip(): r for r in rows[2:] if r and r[0].strip()}
        updates = []
        for u in step["sheet_update"]:
            fields = {}
            for k, v in u.get("fields", {}).items():
                real = hmap.get(norm(k), k)
                if norm(k) == norm("Tên máy") and not u.get("ghi_de_ten"):
                    j = raw_head.index(real) if real in raw_head else 1
                    r = cur.get(str(u.get("stt")).strip(), [])
                    if j < len(r) and r[j].strip():
                        continue          # nguoi dung da dien ten -> giu nguyen
                fields[real] = v
            updates.append({**u, "fields": fields, "ghi_de_ten": True})
        data = json.dumps({"key": key, "updates": updates}).encode()
        st, body, _ = call("POST", url, data, {"Content-Type": "application/json"}, auth=False)
        try:
            res = json.loads(body)
        except Exception:
            res = {"ok": False, "error": body[:200].decode("utf-8", "replace")}
        return {"ok": bool(res.get("ok")), "status": st, "data": res}
    if "wait" in step:
        time.sleep(min(60, float(step["wait"])))
        return {"wait": step["wait"]}
    if "warm" in step:
        out = []
        for u in step["warm"]:
            if not u:
                continue
            full = u if u.startswith("http") else SITE + u
            res = []
            for _ in range(2):
                st, _, hd = call("GET", full, auth=False)
                res.append(hd.get("x-litespeed-cache") or hd.get("X-LiteSpeed-Cache") or str(st))
                time.sleep(1)
            out.append([u, res])
        return {"warm": out}
    url = SITE + "/wp-json" + step["path"]
    method = step.get("method", "GET").upper()
    if "file" in step:
        with open(step["file"], "rb") as f:
            data = f.read()
        name = step.get("filename") or os.path.basename(step["file"])
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        st, body, _ = call(method, url, data, {
            "Content-Type": ctype,
            "Content-Disposition": f'attachment; filename="{name}"'})
    elif "body" in step:
        st, body, _ = call(method, url, json.dumps(step["body"]).encode(),
                           {"Content-Type": "application/json"})
    else:
        st, body, _ = call(method, url)
    try:
        data = json.loads(body)
    except Exception:
        data = body[:300].decode("utf-8", "replace")
    ok = 200 <= st < 300
    res = {"status": st, "ok": ok}
    if ok:
        res["data"] = pick(data, step.get("pick", []))
        if isinstance(data, dict):
            ctx[step.get("id", "_")] = data
    else:
        res["error"] = data if isinstance(data, str) else {
            k: data.get(k) for k in ("code", "message") if isinstance(data, dict)}
    return res


def main():
    os.makedirs("web-results", exist_ok=True)
    jobs = sorted(glob.glob("web-jobs/*.json"))
    if not jobs:
        print("Khong co lenh nao.")
        return
    for job in jobs:
        name = os.path.basename(job)
        print("== Lenh", name)
        try:
            spec = json.load(open(job, encoding="utf-8"))
        except Exception as e:
            result = {"ok": False, "error": f"file lenh loi: {e}"}
        else:
            ctx, steps, all_ok = {}, [], True
            for i, step in enumerate(spec.get("steps", [])):
                try:
                    r = run_step(step, ctx)
                except Exception as e:
                    r = {"ok": False, "error": repr(e)}
                r["step"] = step.get("id", i)
                steps.append(r)
                print(" ", r["step"], r.get("status", ""), "OK" if r.get("ok", True) else "LOI")
                if r.get("ok") is False:
                    all_ok = False
                    break
            result = {"ok": all_ok, "steps": steps,
                      "time": time.strftime("%Y-%m-%d %H:%M:%S")}
        with open(f"web-results/{name}", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
        os.remove(job)
        print("   =>", "XONG" if result["ok"] else "CO LOI")


if __name__ == "__main__":
    main()
