#!/usr/bin/env python3
"""Dung video Duc Thanh tren GitHub Actions (thay cho phien Claude, nhanh va re hon).

Phien "Lam video" chi can: day video goc vao video-goc/<thu_muc>.mp4 va ghi lenh
video-jobs/<thu_muc>.json roi push. Workflow lam-video.yml chay file nay:
  cat (neu can) -> edit_video.py (mau da duyet) -> tach tieng nguoi / nhac nha / tat tieng
  -> luu video/<thu_muc>/<thu_muc>.mp4 + caption.json -> xoa video goc
  -> ghi dong "Cho dang" vao tab DS video (hoac sua dong cu khi lam lai)
  -> ghi ket qua video-results/<thu_muc>.json

Lenh (JSON):
{
 "thu_muc": "may-xep-chai-tu-dong-a1b2c3d4",
 "goc": "video-goc/may-xep-chai-tu-dong-a1b2c3d4.mp4",
 "cat": {"bat_dau": 0, "giay": 15},            # tuy chon
 "pill": "XEM MÁY CHẠY THỰC TẾ", "line1": "MÁY XẾP CHAI", "line2": "TỰ ĐỘNG",
 "notes": ["Câu 1", "Câu 2", "Câu 3"], "note_pos": "bottom",
 "am_thanh": "tach" | "nhac" | "tat",        # mac dinh "tach"
 "caption": {... noi dung caption.json ...},
 "sheet": {"stt": "moi", "fields": {"Tên máy": "...", "Trạng thái": "Chờ đăng", ...}}   # "stt": so dong khi lam lai
}
"""
import glob, json, os, shutil, subprocess, sys, tempfile, time, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "_tools")
RAW = "https://raw.githubusercontent.com/Cao1511/kho-video-dt/video/"
UVR = os.path.expanduser("~/.cache/uvr")
MODEL = "UVR-MDX-NET-Voc_FT.onnx"


def sh(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd)[:300], flush=True)
    return subprocess.run(cmd, check=True, **kw)


def duration(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode().strip())


def lam(spec, log):
    t0 = time.time()
    thu = spec["thu_muc"]
    goc = os.path.join(ROOT, spec.get("goc") or f"video-goc/{thu}.mp4")
    if not os.path.exists(goc):
        raise RuntimeError(f"khong thay video goc {spec.get('goc')}")
    w = tempfile.mkdtemp()
    src = goc
    cat = spec.get("cat")
    if cat:
        src = os.path.join(w, "cut.mp4")
        sh(["ffmpeg", "-v", "error", "-y", "-ss", str(cat.get("bat_dau", 0)), "-i", goc, "-t", str(cat["giay"]),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", src])
    am = spec.get("am_thanh", "tach")
    out = os.path.join(w, "out.mp4")
    sep = None
    if am == "tach":  # tach tieng chay SONG SONG voi dung hinh cho nhanh
        try:
            wav = os.path.join(w, "aud44.wav")
            sh(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", "44100", wav])
            os.makedirs(UVR, exist_ok=True)
            sep = subprocess.Popen(["audio-separator", wav, "-m", MODEL, "--output_dir", os.path.join(w, "sep"),
                                    "--model_file_dir", UVR], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except Exception as e:
            log.append("khong bat dau tach tieng duoc: " + repr(e)[-300:])
    cmd = [sys.executable, os.path.join(TOOLS, "edit_video.py"), src, out,
           "--pill", spec.get("pill", "XEM MÁY CHẠY THỰC TẾ"), "--line1", spec["line1"],
           "--line2", spec.get("line2", ""), "--notes", "|".join(spec.get("notes", [])),
           "--note-pos", spec.get("note_pos", "bottom")]
    if am == "nhac":
        cmd += ["--mute", "--music", os.path.join(TOOLS, "music", "nhac-nha-duc-thanh.mp3")]
    elif am == "tat":
        cmd += ["--mute"]
    for k in ("cta",):
        if spec.get(k):
            cmd += ["--" + k, spec[k]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log.append((r.stdout + r.stderr)[-1500:])
    if r.returncode:
        raise RuntimeError("edit_video loi: " + (r.stderr or r.stdout)[-600:])
    final = out
    ghi_chu = {"tach": "tách tiếng người, giữ tiếng máy", "nhac": "nhạc nhà", "tat": "tắt tiếng"}.get(am, am)
    if am == "tach":
        try:
            if sep is None:
                raise RuntimeError("chua chay tach tieng")
            o2, _ = sep.communicate(timeout=900)
            if sep.returncode:
                raise RuntimeError("audio-separator: " + (o2 or "")[-700:])
            ins = glob.glob(os.path.join(w, "sep", "*Instrumental*"))
            if not ins:
                raise RuntimeError("khong ra file Instrumental")
            final = os.path.join(w, "out2.mp4")
            sh(["ffmpeg", "-v", "error", "-y", "-i", out, "-i", ins[0], "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", final])
        except Exception as e:  # khong tu giu tieng nguoi noi -> tat tieng
            log.append("tach tieng loi: " + repr(e)[-400:])
            final = os.path.join(w, "out2.mp4")
            sh(["ffmpeg", "-v", "error", "-y", "-i", out, "-an", "-c:v", "copy", final])
            ghi_chu = "tách tiếng lỗi → đã tắt tiếng, cần nghe lại"
    if os.path.getsize(final) > 90 * 1024 * 1024:
        small = os.path.join(w, "small.mp4")
        sh(["ffmpeg", "-v", "error", "-y", "-i", final, "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
            "-c:a", "copy", "-movflags", "+faststart", small])
        final = small
    d = os.path.join(ROOT, "video", thu)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, thu + ".mp4")
    shutil.copy(final, dst)
    cap = dict(spec.get("caption") or {})
    cap.setdefault("nhac", ghi_chu)
    with open(os.path.join(d, "caption.json"), "w", encoding="utf-8") as f:
        json.dump(cap, f, ensure_ascii=False, indent=1)
    os.remove(goc)
    link = f"{RAW}video/{thu}/{thu}.mp4"
    res = {"ok": True, "thu_muc": thu, "link": link, "giay_video": round(duration(dst), 1),
           "mb": round(os.path.getsize(dst) / 1048576, 1), "am_thanh": ghi_chu}
    sheet = spec.get("sheet")
    if sheet:
        sys.path.insert(0, TOOLS)
        import web_runner
        fields = dict(sheet.get("fields") or {})
        fields["Link video"] = link
        fields.setdefault("Ghi chú", ghi_chu)
        sr = web_runner.run_step({"tab": "DS video", "sheet_update": [{"stt": str(sheet.get("stt", "moi")),
                                                                       "fields": fields}]}, {})
        res["sheet_ok"] = sr.get("ok")
        try:
            res["stt"] = sr["data"]["results"][0]["stt"]
        except Exception:
            res["sheet"] = sr
    res["giay_xu_ly"] = round(time.time() - t0)
    shutil.rmtree(w, ignore_errors=True)
    return res


def main():
    os.chdir(ROOT)
    os.makedirs("video-results", exist_ok=True)
    jobs = sorted(glob.glob("video-jobs/*.json"))
    if not jobs:
        print("Khong co lenh nao.")
        return
    for job in jobs:
        name = os.path.basename(job)
        log = []
        try:
            spec = json.load(open(job, encoding="utf-8"))
            res = lam(spec, log)
        except Exception as e:
            res = {"ok": False, "error": repr(e)[-800:], "trace": traceback.format_exc()[-1200:]}
        res["log"] = "\n".join(log)[-2000:]
        res["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(f"video-results/{name}", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        os.remove(job)
        print("==", name, "XONG" if res.get("ok") else "LOI", res.get("error", ""))


if __name__ == "__main__":
    main()
