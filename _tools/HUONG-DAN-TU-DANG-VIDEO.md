# Quy trình TỰ ĐỘNG đăng video (chạy theo lịch, không cần duyệt – bản NHANH, dùng Sonnet)

Người dùng (03/11/2026) cho phép: video đã edit xong (tab "DS video" trạng thái "Chờ đăng") thì tự đăng lên TikTok + YouTube Shorts + Facebook Reels, không chờ duyệt. Mỗi lần chạy đăng TỐI ĐA 1 video. Báo cáo tiếng Việt, ngắn gọn. Gộp lệnh shell, ít lượt gọi công cụ.

Thao tác với web/Sheet qua GitHub Actions: ghi `web-jobs/<ten>.json` → commit + push → chờ → `git pull` → đọc `web-results/<ten>.json` (định dạng lệnh: đầu file `_tools/web_runner.py`). Lệnh chờ:
```bash
cho(){ sleep 12; for i in $(seq 1 30); do git pull -q --rebase origin video 2>/dev/null; [ -f web-results/$1.json ] && break; sleep 6; done; cat web-results/$1.json; }
```
Commit kèm dòng Co-Authored-By/Claude-Session theo hướng dẫn hệ thống.

## Bước 0 – Kiểm tra nhanh tại chỗ (KHÔNG gọi Sheet nếu không cần)
```bash
cd /home/claude/kho-video-dt
ls video/*/*.mp4 2>/dev/null; cat danh-sach/tiktok-cho.json 2>/dev/null
```
- Không có file mp4 nào trong `video/*/` VÀ `danh-sach/tiktok-cho.json` trống/không có → KẾT THÚC NGAY, báo 1 dòng "Không có video mới để đăng". (Video chờ đăng = thư mục còn file mp4; đăng xong thì file mp4 bị xoá.)
- `tiktok-cho.json` có mục `{"<STT>": "<buffer post id>"}`: gọi `mcp__Buffer__get_post` từng id; có `externalLink` → ghi vào Sheet (gộp vào lệnh Bước 4, hoặc lệnh riêng nếu không có video mới) `"Link TikTok":[{"text":"Xem TikTok","url":"<link>"}]` rồi xoá mục đó khỏi file; `error` → ghi Ghi chú "TikTok lỗi: <nguyên văn>" và xoá mục; vẫn "sending" quá 1 ngày → xoá mục, bỏ qua.

## Bước 1 – Một lệnh: đọc Sheet + tìm bài sản phẩm, rồi chọn video theo STT NHỎ NHẤT
KHÔNG chọn theo thời gian file (`ls -t` vô nghĩa vì kho vừa tải về, mọi file cùng giờ – lỗi 04/11/2026 đã đăng STT 2 trước STT 1).
Lệnh `web-jobs/doc-video.json`: bước đọc tab + 1 bước tìm bài sản phẩm cho MỖI thư mục còn mp4 (lấy `web.tu_khoa[0]` trong `video/<thu>/caption.json`; có `web.product_id` thì bỏ bước tìm của thư mục đó):
```json
{"steps":[{"sheet":{"tab":"DS video"}},
 {"id":"tim_<thu>","method":"GET","path":"/wc/v3/products?search=<tu_khoa đã URL-encode>&status=publish&_fields=id,name,permalink","pick":["id","name","permalink"]}]}
```
Chọn video: trong dữ liệu Sheet, dòng có Trạng thái "Chờ đăng" và Link video chứa tên một thư mục còn mp4 → lấy dòng có **STT nhỏ nhất**. Các trường hợp khác:
- Thư mục còn mp4 nhưng dòng Sheet là "Huỷ" hoặc "Đã đăng" → `git rm video/<thu>/<thu>.mp4` (dọn, không đăng).
- Thư mục còn mp4 mà không thấy dòng Sheet nào → đăng SAU tất cả các dòng "Chờ đăng" (ghi chú trong báo cáo).
Bài sản phẩm: chỉ nhận khi khớp RÕ 1 bài cùng loại máy (cùng mã máy nếu có); không chắc → không gắn.

## Bước 1b – Nội dung bài đăng (ưu tiên Sheet)
Cột **Bài YouTube / Bài Facebook / Bài TikTok** (người dùng có thể đã sửa) – ô có chữ thì dùng, trống thì lấy caption.json. YouTube/TikTok: dòng đầu `Tiêu đề: <title>`, dòng trống, rồi phần text. Facebook: cả ô là caption. Người dùng sửa trái quy tắc → vẫn đăng đúng ý họ, ghi nhắc trong báo cáo. Ô trống phải tự viết → theo `_tools/CHUAN-SEO.md`. Caption cũ thiếu chuẩn SEO (vd không có từ khoá ở đầu, sai số hashtag) VÀ ô Sheet giống hệt caption.json (tức người dùng chưa sửa) → được chỉnh lại cho đúng `_tools/CHUAN-SEO.md` (giữ ý, chỉ sửa cho chuẩn) và ghi Bài mới vào Sheet ở Bước 3.

## Bước 2 – Đăng 3 kênh qua Buffer (gọi 3 create_post liền nhau)
Org `6ae460e02880bef151572737`, `schedulingType: automatic`, `mode: shareNow`, `assets: [{"video":{"url": "<Link video raw>"}}]` (MẢNG):
- TikTok `6ae4617f2f1f5ed6481dad80`: text, `metadata.tiktok.title`.
- YouTube `6ae4616a2f1f5ed6481dacd4`: text, `metadata.youtube = {title, categoryId:"28", privacy:"public", madeForKids:false}`.
- Facebook `6ae461382f1f5ed6481dab31`: text, `metadata.facebook.type = "reel"`.
Rồi `get_post` 3 bài (gọi song song). YouTube/Facebook thường `sent` ngay; chưa có `externalLink` thì gọi lại 1–2 lần. TikTok "sending" → ghi id vào `danh-sach/tiktok-cho.json`, lần chạy sau xử lý (Bước 0). Bài `error` → ghi lỗi nguyên văn vào Ghi chú, không đăng lại lung tung.

## Bước 3 – Một lệnh: gắn video vào web + nạp cache + ghi Sheet (và dọn kho cùng lần push)
`web-jobs/xong-<thu>.json` (bỏ bước `chen`/`warm` nếu không có bài sản phẩm; bỏ "Link TikTok" nếu chưa có):
```json
{"steps":[
 {"id":"chen","chen_video":{"product_id":<id>,"youtube":"<link YouTube watch?v=…>","ten":"<tên máy>"}},
 {"warm":["/","{{chen.permalink}}"]},
 {"tab":"DS video","sheet_update":[{"stt":"<STT>","fields":{
   "Trạng thái":"Đã đăng","Thời gian đăng":"{{now.vn}}",
   "Link YouTube":[{"text":"Xem YouTube","url":"<link>"}],
   "Link Facebook":[{"text":"Xem Facebook","url":"<link>"}],
   "Link TikTok":[{"text":"Xem TikTok","url":"<link>"}],
   "Link video":"<link YouTube>",
   "Link bài web":[{"text":"Xem bài web","url":"{{chen.permalink}}"}],
   "Ghi chú":"<TikTok đang xử lý / lỗi nếu có; để trống nếu không>"}}]}]}
```
Không có bài sản phẩm → "Link bài web":"Chưa có bài". Cùng commit đó: `git rm video/<thu>/<thu>.mp4` (giữ caption.json; chỉ khi YouTube + Facebook đã `sent`) và cập nhật `danh-sach/tiktok-cho.json`. Push → `cho xong-<thu>` → kiểm tra `ok: true`. Sửa bài web đã đăng nên plugin KHÔNG đăng lại Facebook. KHÔNG xoá toàn bộ cache.

## Báo cáo (SendUserMessage)
"Đã đăng video STT <số> – <tên máy>: YouTube <link> | Facebook <link> | TikTok <link hoặc đang xử lý> | Web: <đã gắn vào bài … / chưa có bài>". Không có video → "Không có video mới để đăng".

## Quy tắc
- Không link URL trong caption; không số điện thoại/web trong video; YouTube mô tả không có liên hệ; Facebook dùng 2 số 0974 708 603 – 0989 139 855; không #quangcao; không icon đầu caption.
- Không đăng lại video "Đã đăng". Không xoá bài, không sửa nội dung khác của bài web ngoài việc chèn mục video.
