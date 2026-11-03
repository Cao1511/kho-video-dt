# Làm video Đức Thành → lưu "Chờ đăng" (bản NHANH, dùng Sonnet)

Trả lời tiếng Việt, ngắn, dễ hiểu (người dùng thường dùng điện thoại). Người dùng gửi video máy (có thể kèm tên máy, "thêm nhạc", "cắt còn 15s"). **KHÔNG đăng lên mạng xã hội** – lịch tự đăng (8:21, 11:21, 14:21, 17:21, 20:21) sẽ đăng.

**Nguyên tắc tiết kiệm:** phiên này CHỈ xem video, viết chữ + caption, đẩy lên GitHub. Việc nặng (dựng hình, tách tiếng người, nén, ghi Sheet) do GitHub Actions làm (workflow "Lam video Duc Thanh", ~1–3 phút). KHÔNG cài audio-separator, KHÔNG chạy edit_video.py trong phiên. Gộp lệnh shell, ít lượt gọi công cụ, không đọc lại file không cần.

## 1. Chuẩn bị (1 lệnh)
```bash
[ -d /home/claude/kho-video-dt ] || git clone -q --depth 1 --single-branch -b video https://github.com/Cao1511/kho-video-dt /home/claude/kho-video-dt
cd /home/claude/kho-video-dt && git pull -q --rebase origin video
```
Lỗi quyền/không clone được → gọi `add_repo` (owner Cao1511, repo kho-video-dt, access push) rồi chạy lại. Không sửa/xoá `_tools/`, `.github/`.

## 2. Xem video (1 lệnh, 1 ảnh)
```bash
SRC=<đường dẫn video người dùng gửi>; ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC"
ffmpeg -v error -y -i "$SRC" -vf "fps=6/$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC" | cut -d. -f1),scale=240:-1,tile=6x1" -frames:v 1 /tmp/khung.jpg
```
Xem `/tmp/khung.jpg` (6 khung từ đầu đến cuối). Chưa chắc là máy gì → hỏi 1 câu ngắn (gợi ý 2–3 tên), không đoán.

## 3. Viết chữ trên video + caption
- `line1`/`line2`: tên máy IN HOA, mỗi dòng ≤ 16–17 ký tự, chứa từ khoá (vd "MÁY XẾP CHAI" / "TỰ ĐỘNG").
- `notes`: 3–4 câu (video ≤15 giây: 2–3 câu), mỗi câu ≤ 4–5 từ, đúng điều thấy trong video, không bịa thông số.
- `am_thanh`: `"tach"` (mặc định – tách tiếng người, giữ tiếng máy) | `"nhac"` (khi người dùng nói "thêm nhạc" – chỉ nhạc nhà) | `"tat"`.
- `cat`: `{"bat_dau":0,"giay":15}` khi người dùng bảo cắt ngắn.
- `note_pos`: `"bottom"` (mặc định) hoặc `"auto"` khi nền giữa màn hình trắng/sáng.
- Caption (KHÔNG link, KHÔNG icon đầu caption, không "nhất/số 1", không #quangcao; chỉ điều thấy trong video):
  - TikTok: `title` = từ khoá + " | Đức Thành"; `text`: câu đầu bắt đầu bằng từ khoá; 1–2 câu tên gọi khác + ngành; "💬 Nhắn tin cho kênh để được tư vấn & báo giá"; 3–5 hashtag cụ thể (#ducthanh), không #fyp. Không số điện thoại.
  - YouTube: `title` 60–80 ký tự, từ khoá trong 50 ký tự đầu, kết thúc "| Đức Thành"; `text` ≤200 ký tự, KHÔNG số điện thoại/Zalo/web, cuối `#shorts` + 3–5 hashtag.
  - Facebook: dòng đầu bắt đầu bằng từ khoá + công dụng; 1–2 câu mô tả; "🏭 Đức Thành – tư vấn, lắp đặt & bảo hành tận nơi"; "📞 Hotline/Zalo: 0974 708 603 – 0989 139 855"; 1 câu hỏi mở; 3–5 hashtag.
  - `web.tu_khoa`: 2–3 từ khoá tìm bài sản phẩm trên web (vd ["xếp chai","ZS-TB500"]); `web.product_id`: null (lịch tự đăng tự tìm).

## 4. Đẩy lên (1 lệnh Python + git)
Tên thư mục `<tu-khoa-khong-dau>-<8 hex>` (vd `may-xep-chai-tu-dong-a1b2c3d4`).
```bash
cd /home/claude/kho-video-dt && python3 - <<'E'
import json, os, secrets, shutil, subprocess
SRC = "<đường dẫn video gốc>"
thu = "<tu-khoa-khong-dau>-" + secrets.token_hex(4)
cap = {"ten": "<Tên máy>", "tu_khoa": "<từ khoá chính>",
       "tiktok": {"title": "…", "text": "…"}, "youtube": {"title": "…", "text": "…"},
       "facebook": {"text": "…"}, "web": {"tu_khoa": ["…", "…"], "product_id": None}}
os.makedirs("video-goc", exist_ok=True); os.makedirs("video-jobs", exist_ok=True)
dst = f"video-goc/{thu}.mp4"
if os.path.getsize(SRC) > 95 * 2**20:   # GitHub giới hạn 100 MB/file
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", dst], check=True)
else:
    shutil.copy(SRC, dst)
job = {"thu_muc": thu, "goc": dst, "pill": "XEM MÁY CHẠY THỰC TẾ", "line1": "…", "line2": "…",
       "notes": ["…", "…", "…"], "am_thanh": "tach", "caption": cap,
       "sheet": {"stt": "moi", "fields": {"Tên máy": cap["ten"], "Trạng thái": "Chờ đăng",
           "Bài YouTube": f"Tiêu đề: {cap['youtube']['title']}\n\n{cap['youtube']['text']}",
           "Bài Facebook": cap["facebook"]["text"],
           "Bài TikTok": f"Tiêu đề: {cap['tiktok']['title']}\n\n{cap['tiktok']['text']}"}}}
json.dump(job, open(f"video-jobs/{thu}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(thu)
E
git add video-goc video-jobs && git commit -qm "Video moi" && git pull -q --rebase origin video && git push -q origin video
```
(Commit kèm dòng Co-Authored-By/Claude-Session theo hướng dẫn hệ thống.)

Báo ngay cho người dùng 1 câu: "Đã gửi video lên máy dựng, khoảng 2–3 phút nữa xong, sẽ tự vào Sheet trạng thái Chờ đăng."

## 5. Chờ kết quả + gửi bản xem trước (1 lệnh)
```bash
cd /home/claude/kho-video-dt; T=<thu_muc>; for i in $(seq 1 50); do git pull -q --rebase origin video 2>/dev/null; [ -f video-results/$T.json ] && break; sleep 10; done; cat video-results/$T.json | head -20
```
- `ok: true` → chép `video/<T>/<T>.mp4` sang `/mnt/user-data/outputs/<T>.mp4`, gửi bằng SendUserFile (display render). Báo: "Đã lưu video STT <stt> – <tên máy>, Chờ đăng. Nội dung 3 bài đăng nằm ở cột Bài YouTube/Facebook/TikTok trong Sheet – muốn sửa thì sửa thẳng trong Sheet trước giờ đăng." Nhắc nghe lại âm thanh. Nếu `am_thanh` báo "tách tiếng lỗi" → nói rõ video đang tắt tiếng.
- `ok: false` → báo lỗi ngắn gọn (trường `error`), sửa lệnh và gửi lại.
- Sau 8 phút chưa có kết quả → báo người dùng "máy dựng đang chậm, lát nữa xem trong Sheet", kết thúc.

## Sửa / làm lại / huỷ
- Sửa chữ trên video hoặc làm lại: giữ nguyên `thu_muc` cũ; nếu video gốc đã bị xoá thì cần người dùng gửi lại video (hoặc dùng `git show` lịch sử `video-goc/<thu>.mp4`). Trong lệnh đặt `"sheet": {"stt": "<STT cũ>", "fields": {...}}` để sửa đúng dòng cũ, không thêm dòng mới.
- Sửa chữ bài đăng: người dùng sửa thẳng trong Sheet.
- Huỷ: lệnh `web-jobs/huy-<thu>.json` = `{"steps":[{"tab":"DS video","sheet_update":[{"stt":"<STT>","fields":{"Trạng thái":"Huỷ"}}]}]}` + `git rm video/<thu>/<thu>.mp4`, commit, push.

## Quy tắc
- Không số điện thoại/web/Zalo trong video; không link trong caption; YouTube không ghi liên hệ; Facebook dùng 2 số 0974 708 603 – 0989 139 855. Không lật hình. Video nhà cung cấp phải có chữ thuyết minh tiếng Việt. Không đăng video người dùng nói là nội bộ.
