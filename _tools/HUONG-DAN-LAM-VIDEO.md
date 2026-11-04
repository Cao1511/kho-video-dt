# Làm video Đức Thành → lưu "Chờ đăng" (bản NHANH, dùng Sonnet)

Trả lời tiếng Việt, ngắn, dễ hiểu (người dùng thường dùng điện thoại). Người dùng gửi video máy (có thể kèm tên máy, "thêm nhạc", "cắt còn 15s"). **KHÔNG đăng lên mạng xã hội** – lịch tự đăng (8:21, 11:21, 14:21, 17:21, 20:21) sẽ đăng.

**Nguyên tắc tiết kiệm:** phiên này CHỈ xem video, viết chữ + caption, đẩy lên GitHub. Việc nặng (dựng hình, tách tiếng người, nén, ghi Sheet) do GitHub Actions làm (workflow "Lam video Duc Thanh", ~1–3 phút). KHÔNG cài audio-separator, KHÔNG chạy edit_video.py trong phiên. Gộp lệnh shell, ít lượt gọi công cụ, không đọc lại file không cần.

## 1. Chuẩn bị (1 lệnh)
```bash
[ -d /home/claude/kho-video-dt ] || git clone -q --depth 1 --single-branch -b video https://github.com/Cao1511/kho-video-dt /home/claude/kho-video-dt
cd /home/claude/kho-video-dt && git pull -q --rebase origin video
```
Lỗi quyền/không clone được → gọi `add_repo` (owner Cao1511, repo kho-video-dt, access push) rồi chạy lại. Không sửa/xoá `_tools/`, `.github/`.

## 2. Xem video (1 lệnh)
```bash
cd /home/claude/kho-video-dt && python3 _tools/gui_video.py xem "<đường dẫn video người dùng gửi>"
```
In ra độ dài + **số câu thuyết minh tối đa** (video ngắn chỉ đủ 1–2 câu – đừng viết thừa). Xem `/tmp/khung.jpg` (6 khung đầu→cuối). Chưa chắc là máy gì → hỏi 1 câu ngắn (gợi ý 2–3 tên), không đoán.

## 3. GỬI VIDEO ĐI DỰNG NGAY (chưa cần caption) – để máy dựng chạy song song lúc viết caption
Ghi `/tmp/hinh.json` (dùng công cụ Write) rồi gửi:
```json
{"ten":"Máy đóng gói đậu tự động","slug":"may-dong-goi-dau-tu-dong","line1":"MÁY ĐÓNG GÓI","line2":"ĐẬU TỰ ĐỘNG",
 "notes":["Định lượng chính xác","Hàn kín túi"],"am_thanh":"tach"}
```
```bash
cd /home/claude/kho-video-dt && python3 _tools/gui_video.py gui "<đường dẫn video>" /tmp/hinh.json
```
- Chọn từ khoá chính trước (`_tools/CHUAN-SEO.md` mục 0) để `ten`, `slug`, `line1`/`line2` đúng từ khoá. `line1`/`line2`: IN HOA, mỗi dòng ≤ 16–17 ký tự, BẮT BUỘC chứa từ khoá chính.
- `notes`: không quá số câu tối đa ở bước 2, mỗi câu ≤ 4–5 từ, đúng điều thấy trong video, không bịa thông số.
- `am_thanh`: `"tach"` (mặc định) | `"nhac"` (người dùng nói "thêm nhạc") | `"tat"`. Thêm `"cat":{"bat_dau":0,"giay":15}` khi cần cắt ngắn / 3 giây đầu chưa thấy máy chạy; `"note_pos":"auto"` khi giữa màn hình nền trắng/sáng.
In ra `THU_MUC=…`. Báo người dùng 1 câu: "Đã gửi lên máy dựng, em viết bài đăng song song, khoảng 2 phút nữa xong."

## 4. Viết caption TRONG LÚC máy dựng chạy, rồi gửi (máy dựng chờ tối đa 4 phút)
Ghi `/tmp/nd.json` theo **`_tools/CHUAN-SEO.md`** (mục 1–4, tự kiểm mục 6):
```json
{"ten":"Máy đóng gói đậu tự động","tu_khoa":"máy đóng gói đậu tự động",
 "tiktok":{"title":"…","text":"…"},"youtube":{"title":"…","text":"…"},"facebook":{"text":"…"},
 "web":{"tu_khoa":["đóng gói đậu","đóng gói hạt"],"product_id":null}}
```
```bash
cd /home/claude/kho-video-dt && python3 _tools/gui_video.py caption <THU_MUC> /tmp/nd.json
```
Tóm tắt (KHÔNG link, KHÔNG icon đầu caption, không "nhất/số 1", không #quangcao; chỉ điều thấy trong video):
- TikTok: `title` = từ khoá + " | Đức Thành"; `text` 150–300 ký tự: câu đầu bắt đầu bằng từ khoá; tên gọi khác + ngành; "💬 Nhắn tin cho kênh để được tư vấn & báo giá"; 3–5 hashtag (#ducthanh), không #fyp. Không số điện thoại.
- YouTube: `title` 60–80 ký tự, từ khoá trong 50 ký tự đầu, kết thúc "| Đức Thành"; `text` ≤200 ký tự, KHÔNG số điện thoại/Zalo/web, cuối `#shorts` + 3–5 hashtag.
- Facebook: dòng đầu bắt đầu bằng từ khoá + công dụng; 1–2 câu mô tả; "🏭 Đức Thành – tư vấn, lắp đặt & bảo hành tận nơi"; "📞 Hotline/Zalo: 0974 708 603 – 0989 139 855"; 1 câu hỏi mở; 3–5 hashtag.

## 5. Chờ kết quả (1 lệnh) + gửi bản xem trước
```bash
cd /home/claude/kho-video-dt && python3 _tools/gui_video.py cho <THU_MUC>
```
- `ok: true` → gửi `file_xem_truoc` bằng SendUserFile (display render). Báo: "Đã lưu video STT <stt> – <tên máy>, Chờ đăng. Nội dung 3 bài đăng nằm ở cột Bài YouTube/Facebook/TikTok trong Sheet – muốn sửa thì sửa thẳng trong Sheet trước giờ đăng." Nhắc nghe lại âm thanh; `am_thanh` báo "tách tiếng lỗi" → nói rõ video đang tắt tiếng. `log` có "het gio cho caption" → gửi lại caption bằng lệnh sheet_update (tab DS video, stt vừa nhận).
- `ok: false` → báo lỗi ngắn gọn (trường `error`). Lỗi "bước cài đặt" → chạy lại: `gh workflow run lam-video.yml --repo Cao1511/kho-video-dt --ref video` (lệnh vẫn còn), hoặc gửi lại.
- `CHUA_XONG` → báo "máy dựng đang chậm, lát nữa xem trong Sheet", kết thúc.

## Sửa / làm lại / huỷ
- Sửa chữ trên video hoặc làm lại: (có thể gửi 1 lần, caption đủ trong cùng file) thêm vào `/tmp/nd.json` `"thu_muc":"<thư mục cũ>"` và `"stt":"<STT cũ>"` rồi chạy lại bước 4–5 (sửa đúng dòng cũ, không thêm dòng mới). Video gốc đã bị xoá sau khi dựng → dùng video người dùng gửi lại (hoặc `git show <commit>:video-goc/<thu>.mp4 > /tmp/goc.mp4`).
- Sửa chữ bài đăng: người dùng sửa thẳng trong Sheet.
- Huỷ: lệnh `web-jobs/huy-<thu>.json` = `{"steps":[{"tab":"DS video","sheet_update":[{"stt":"<STT>","fields":{"Trạng thái":"Huỷ"}}]}]}` + `git rm video/<thu>/<thu>.mp4`, commit, push.

## Quy tắc
- Không số điện thoại/web/Zalo trong video; không link trong caption; YouTube không ghi liên hệ; Facebook dùng 2 số 0974 708 603 – 0989 139 855. Không lật hình. Video nhà cung cấp phải có chữ thuyết minh tiếng Việt. Không đăng video người dùng nói là nội bộ.
