# Quy trình TỰ ĐỘNG đăng video (chạy theo lịch, không cần duyệt)

Người dùng (03/11/2026) cho phép: video đã edit xong (tab "DS video" trạng thái "Chờ đăng") thì tự đăng lên TikTok + YouTube Shorts + Facebook Reels, không chờ duyệt. Mỗi lần chạy đăng TỐI ĐA 1 video. Không có video chờ thì dừng, báo 1 dòng. Báo cáo bằng tiếng Việt, ngắn gọn.

Video do phiên "Làm video" (skill `lam-video-ducthanh`) edit sẵn theo mẫu Đức Thành và đẩy lên kho này: thư mục `video/<thu-muc>/` gồm `<ten>.mp4` + `caption.json` (caption đã viết sẵn cho 3 nền tảng). Phiên tự đăng KHÔNG edit lại video, KHÔNG viết lại caption (trừ khi caption thiếu).

Thao tác với web/Sheet qua GitHub Actions như `_tools/HUONG-DAN-TU-DANG.md` (ghi `web-jobs/<ten>.json` → commit + push → chờ workflow → `git pull` → đọc `web-results/<ten>.json`). Commit kèm dòng Co-Authored-By/Claude-Session theo hướng dẫn hệ thống.

## Bước 0 – Cập nhật TikTok còn treo từ lần trước (làm nhanh; không được thì thôi, người dùng chấp nhận để trống)
Đọc tab (Bước 1). Dòng nào Trạng thái = "Đã đăng" mà cột Link TikTok trống và Ghi chú có `tiktok_post=<id>`: gọi `mcp__Buffer__get_post` id đó; có `externalLink` thì ghi vào cột Link TikTok (lệnh Bước 5), có `error` thì ghi Ghi chú "TikTok lỗi: <nguyên văn>".

## Bước 1 – Chọn video
1. Lệnh `{"steps":[{"sheet":{"tab":"DS video"}}]}` → danh sách dòng (key = tên cột theo thứ tự: STT, Tên máy, Link video, Bài YouTube, Bài Facebook, Bài TikTok, Trạng thái, Thời gian đăng, Link YouTube, Link Facebook, Link TikTok, Link bài web, Ghi chú).
2. Chọn STT **nhỏ nhất** có Trạng thái = "Chờ đăng" và có Link video. Không có → kết thúc, báo "Không có video mới để đăng".
3. Thư mục video = phần đường dẫn trong Link video sau `/video/video/` (vd `.../kho-video-dt/video/video/may-xep-chai-a1b2c3d4/may-xep-chai-a1b2c3d4.mp4` → `video/may-xep-chai-a1b2c3d4/`). Đọc `caption.json` trong thư mục đó. Kiểm tra file mp4 còn trong kho và link raw trả 200/206 (`curl -s -o /dev/null -w "%{http_code}" -r 0-100 <link>`). Mất file → ghi Trạng thái "Lỗi – mất file video", dừng.

## Bước 1b – Lấy nội dung bài đăng (ưu tiên nội dung trong Sheet)
Tab "DS video" có 3 cột nội dung bài: **Bài YouTube**, **Bài Facebook**, **Bài TikTok** (phiên làm video ghi sẵn; người dùng có thể đã SỬA trong Sheet). Luôn dùng nội dung trong Sheet nếu ô có chữ; ô trống mới lấy từ `caption.json`.
- Bài YouTube / Bài TikTok có dạng: dòng đầu `Tiêu đề: <tiêu đề>`, một dòng trống, rồi phần mô tả/caption. → title = phần sau "Tiêu đề:" ở dòng đầu; text = phần còn lại (bỏ dòng trống đầu).
- Bài Facebook: toàn bộ ô là caption.
- Kiểm tra lại quy tắc (không link, YouTube không liên hệ, không icon đầu caption…); nếu người dùng sửa sai quy tắc thì vẫn đăng đúng ý người dùng nhưng ghi nhắc trong báo cáo.

## Bước 2 – Đăng 3 kênh qua Buffer
Org `6ae460e02880bef151572737`. `mcp__Buffer__create_post`, `schedulingType: automatic`, `mode: shareNow`, `assets: [{"video":{"url": LINK_VIDEO}}]` (MẢNG):
- TikTok `6ae4617f2f1f5ed6481dad80`: text/title lấy theo Bước 1b (Bài TikTok, hoặc `caption.tiktok`).
- YouTube `6ae4616a2f1f5ed6481dacd4`: text/title theo Bước 1b (Bài YouTube, hoặc `caption.youtube`), `metadata.youtube = {title, categoryId: "28", privacy: "public", madeForKids: false}`.
- Facebook `6ae461382f1f5ed6481dab31`: text theo Bước 1b (Bài Facebook, hoặc `caption.facebook.text`), `metadata.facebook.type = "reel"`.
Rồi `mcp__Buffer__get_post` từng bài lấy `status` + `externalLink`. YouTube/Facebook thường `sent` ngay; TikTok hay "sending" vài phút → gọi lại get_post 2–3 lần cách nhau (làm việc khác xen giữa), vẫn chưa xong thì để Bước 0 lần sau xử lý. Bài `error` → ghi lỗi nguyên văn vào Ghi chú, không đăng lại lung tung.

## Bước 3 – Gắn link YouTube vào bài sản phẩm trên web
- `caption.web.product_id` có số → dùng. Không có → tìm: lệnh GET `/wc/v3/products?search=<từ khoá trong caption.web.tu_khoa>&status=publish&_fields=id,name,permalink` (thử 2–3 từ khoá). Chỉ gắn khi khớp RÕ 1 bài cùng loại máy (cùng mã máy nếu có). Không chắc / không có → bỏ qua, ghi cột Link bài web "Chưa có bài".
- Gắn: lệnh GET `/wc/v3/products/<id>?_fields=id,name,permalink,description` (pick id,name,permalink,description) → nếu description chưa chứa id video YouTube, chèn NGAY TRƯỚC `<h2>Liên hệ tư vấn và báo giá</h2>`: `<h2>Video <tên máy> chạy thực tế</h2>\n\n<link watch?v=...>\n\n` (link nằm riêng 1 dòng để WordPress tự nhúng) → lệnh PUT `/wc/v3/products/<id>` {"description": …} rồi `warm` 2 lần trang sản phẩm + `/`. Sửa bài đã đăng nên plugin KHÔNG đăng lại Facebook. KHÔNG xoá toàn bộ cache.

## Bước 4 – Dọn kho
Khi YouTube + Facebook đã `sent` (Buffer đã sao chép video): `git rm` file mp4 (giữ `caption.json`), commit + push.

## Bước 5 – Ghi vào Sheet (tab "DS video")
Lệnh:
```json
{"steps":[{"tab":"DS video","sheet_update":[{"stt":"<STT>","fields":{
  "Trạng thái":"Đã đăng","Thời gian đăng":"<dd/mm/yyyy HH:MM giờ VN>",
  "Link YouTube":[{"text":"Xem YouTube","url":"<link>"}],
  "Link Facebook":[{"text":"Xem Facebook","url":"<link>"}],
  "Link TikTok":[{"text":"Xem TikTok","url":"<link>"}]  ← chưa lấy được thì BỎ trường này (người dùng chấp nhận để trống),
  "Link video":"<link YouTube – vì file mp4 đã xoá khỏi kho>",
  "Link bài web":"<link bài sản phẩm đã gắn video, hoặc chữ Chưa có bài>",
  "Ghi chú":"<tiktok_post=<id> nếu TikTok còn đang xử lý; lỗi nếu có>"}}]}]}
```
Kết quả lỗi "chưa cài SHEET_URL/SHEET_KEY" → ghi vào báo cáo.

## Báo cáo (SendUserMessage)
"Đã đăng video STT <số> – <tên máy>: YouTube <link> | Facebook <link> | TikTok <link hoặc đang xử lý> | Web: <đã gắn vào bài … / chưa có bài>". Không có video → "Không có video mới để đăng".

## Quy tắc
- Không link URL trong caption; không số điện thoại/web trong video; YouTube mô tả không có liên hệ; Facebook dùng 2 số 0974 708 603 – 0989 139 855; không #quangcao; không icon đầu caption (caption.json đã viết theo đúng quy tắc này – chỉ kiểm tra lại).
- Không đăng lại video đã "Đã đăng". Không xoá bài, không sửa nội dung khác của bài web ngoài việc chèn mục video.
