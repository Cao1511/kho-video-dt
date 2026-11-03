#!/usr/bin/env python3
"""Cong cu cho phien "Lam video" (Sonnet) – 3 lenh ngan, it buoc.

1) Xem video:   python3 _tools/gui_video.py xem <video>
   -> in do dai, so cau thuyet minh toi da; tao /tmp/khung.jpg (6 khung tu dau den cuoi)
2) Gui di:      python3 _tools/gui_video.py gui <video> <noi-dung.json>
   noi-dung.json = {"ten","tu_khoa","slug","line1","line2","notes":[...],"am_thanh":"tach|nhac|tat",
                    "cat":{"bat_dau":0,"giay":15} (tuy chon), "note_pos":"bottom|auto" (tuy chon),
                    "tiktok":{"title","text"},"youtube":{"title","text"},"facebook":{"text"},
                    "web":{"tu_khoa":[...],"product_id":null},
                    "stt": "<STT cu khi lam lai>" (tuy chon), "thu_muc": "<thu muc cu khi lam lai>" (tuy chon)}
   -> chep video goc, ghi lenh, commit + push; in ra THU_MUC=...
3) Cho ket qua: python3 _tools/gui_video.py cho <thu_muc>
   -> cho GitHub dung xong (toi da ~8 phut), chep video ra /mnt/user-data/outputs/<thu_muc>.mp4, in ket qua
"""
import json, os, secrets, shutil, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>"


def run(*c, **kw):
    return subprocess.run(c, check=True, cwd=REPO, **kw)


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode().strip())


def xem(src):
    d = dur(src)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                    f"fps=6/{max(d, 1):.2f},scale=240:-1,tile=6x1", "-frames:v", "1", "/tmp/khung.jpg"], check=True)
    n = max(0, int((min(d, 170) - 4.1) // 3.0))
    print(f"DO_DAI={d:.1f}s  SO_CAU_TOI_DA={min(n, 4)}  (cat ngan thi tinh lai: (giay-4.1)/3)  ANH=/tmp/khung.jpg")


def gui(src, nd_path):
    nd = json.load(open(nd_path, encoding="utf-8"))
    thu = nd.get("thu_muc") or (nd["slug"].strip("-") + "-" + secrets.token_hex(4))
    os.makedirs(os.path.join(REPO, "video-goc"), exist_ok=True)
    os.makedirs(os.path.join(REPO, "video-jobs"), exist_ok=True)
    dst = os.path.join(REPO, "video-goc", thu + ".mp4")
    if os.path.getsize(src) > 95 * 2 ** 20:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "23", "-c:a", "aac", dst], check=True)
    else:
        shutil.copy(src, dst)
    cap = {k: nd[k] for k in ("ten", "tu_khoa", "tiktok", "youtube", "facebook", "web") if k in nd}
    fields = {"Tên máy": nd["ten"], "Trạng thái": "Chờ đăng",
              "Bài YouTube": f"Tiêu đề: {nd['youtube']['title']}\n\n{nd['youtube']['text']}",
              "Bài Facebook": nd["facebook"]["text"],
              "Bài TikTok": f"Tiêu đề: {nd['tiktok']['title']}\n\n{nd['tiktok']['text']}"}
    job = {"thu_muc": thu, "goc": f"video-goc/{thu}.mp4", "pill": nd.get("pill", "XEM MÁY CHẠY THỰC TẾ"),
           "line1": nd["line1"], "line2": nd.get("line2", ""), "notes": nd.get("notes", []),
           "note_pos": nd.get("note_pos", "bottom"), "am_thanh": nd.get("am_thanh", "tach"), "caption": cap,
           "sheet": None if nd.get("khong_ghi_sheet") else {"stt": str(nd.get("stt", "moi")), "fields": fields}}
    if nd.get("cat"):
        job["cat"] = nd["cat"]
    with open(os.path.join(REPO, "video-jobs", thu + ".json"), "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=1)
    run("git", "add", "video-goc", "video-jobs")
    run("git", "commit", "-qm", f"Video moi {thu}" + MSG)
    for i in range(4):
        r = subprocess.run(["git", "pull", "-q", "--rebase", "origin", "video"], cwd=REPO)
        if r.returncode == 0 and subprocess.run(["git", "push", "-q", "origin", "video"], cwd=REPO).returncode == 0:
            break
        time.sleep(3)
    else:
        sys.exit("LOI: khong push duoc len GitHub")
    print(f"THU_MUC={thu}  (da gui len may dung, khoang 2 phut)")


def cho(thu):
    res = os.path.join(REPO, "video-results", thu + ".json")
    t0 = time.time()
    time.sleep(45)
    while time.time() - t0 < 480:
        subprocess.run(["git", "pull", "-q", "--rebase", "origin", "video"], cwd=REPO,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(res):
            break
        time.sleep(8)
    else:
        print("CHUA_XONG: may dung dang cham, ket qua se tu vao Sheet."); return
    r = json.load(open(res, encoding="utf-8"))
    if r.get("ok"):
        os.makedirs("/mnt/user-data/outputs", exist_ok=True)
        out = f"/mnt/user-data/outputs/{thu}.mp4"
        shutil.copy(os.path.join(REPO, "video", thu, thu + ".mp4"), out)
        r["file_xem_truoc"] = out
    r.pop("trace", None)
    print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "xem":
        xem(sys.argv[2])
    elif cmd == "gui":
        gui(sys.argv[2], sys.argv[3])
    elif cmd == "cho":
        cho(sys.argv[2])
    else:
        print(__doc__)
