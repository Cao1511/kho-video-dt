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
