# Quy trình TỰ ĐỘNG đăng sản phẩm mayducthanh.vn (chạy theo lịch, không cần duyệt)

Người dùng (31/10/2026) cho phép: có bài là tự viết chuẩn SEO và TỰ ĐĂNG luôn, không chờ duyệt. Mỗi lần chạy đăng TỐI ĐA 1 máy. Không có máy nào đủ điều kiện thì dừng, không làm gì thêm. Trả lời/báo cáo bằng tiếng Việt, ngắn, dễ hiểu.

Mọi thao tác với web đi qua **GitHub Actions** (máy chủ đám mây không vào thẳng được mayducthanh.vn): ghi file lệnh `web-jobs/<ten>.json` → commit + push nhánh `video` → chờ workflow "Dang web mayducthanh.vn" chạy xong → `git pull` → đọc `web-results/<ten>.json`. Định dạng lệnh xem đầu file `_tools/web_runner.py`.

```bash
# chờ workflow chạy xong sau khi push
sleep 15; for i in $(seq 1 25); do s=$(gh api repos/Cao1511/kho-video-dt/actions/runs --jq '.workflow_runs[0]|.status+" "+(.conclusion//"")'); [[ $s == completed* ]] && break; sleep 8; done; echo $s
git pull -q --rebase origin video
```
Commit kèm dòng Co-Authored-By/Claude-Session theo hướng dẫn hệ thống. Không xoá `_tools/`, `.github/`, `AGENTS.md`, `anh/`.

## Bước 1 – Chọn máy
1. Đọc bảng: lệnh `{"steps":[{"sheet":true}]}` → danh sách `{stt, ten, link}`.
2. Đọc `danh-sach/da-dang.json` (các STT đã đăng).
3. Chọn STT **nhỏ nhất** thoả cả 3: có link (tên máy có thể TRỐNG – khi đó tự đặt tên từ trang link); CHƯA có trong `da-dang.json` và cột Trạng thái khác "Đã đăng"; ĐÃ có ảnh `anh/<STT>/1.png` trong kho (ảnh do Codex làm theo khung chuẩn). Máy chưa có ảnh → bỏ qua, ghi trong báo cáo "STT x chưa có ảnh" và cập nhật Sheet Trạng thái "Chưa có ảnh" (gộp vào lệnh ở Bước 6).
4. Không còn máy nào → kết thúc, báo 1 dòng "Không có máy mới để đăng".
5. Chống đăng trùng: lệnh GET `/wc/v3/products?search=<mã máy hoặc tên>&status=any&_fields=id,name,status,permalink` (pick id,name,status,permalink). Đã có bài cùng máy → ghi STT đó vào `da-dang.json` (kèm `"ghi_chu":"da co san tren web"`), chọn máy khác.

## Bước 2 – Lấy thông số
- WebFetch link ở cột "Link mẫu" (lấy nguyên link từ kết quả WebFetch bảng: https://docs.google.com/spreadsheets/d/1Zwy4QBWBwFZ-wzkURH7--dRxB_BRhgOw_Tzt-1zzDVg/edit?usp=sharing). Link quá dài/bị từ chối → WebSearch "<mã máy> <tên tiếng Anh>" rồi WebFetch kết quả đúng mã máy.
- Chỉ dùng thông số có thật trong trang. Không bịa. Thiếu thì bỏ dòng đó.
- Đối chiếu ảnh `anh/<STT>/1.png` (tên máy, mã, 3 thông số trên ảnh) để bài viết khớp ảnh.

## Bước 3 – Viết bài chuẩn SEO (kiểu bài mẫu id 272, 356)
- `name`: tên máy tiếng Việt + mã máy nếu có (vd "Máy viền nắp lọ tự động ZS-YG100"). `slug`: ngắn, không dấu, chứa từ khoá (vd `may-vien-nap-lo-tu-dong`).
- `short_description`: `<ul class="dt-short">` 4–5 dòng, in đậm số liệu chính.
- `description` (HTML): h2 Giới thiệu (2 đoạn, in đậm năng suất/điểm chính) → h2 Ứng dụng (ul) → h2 Thông số kỹ thuật (`<table class="dt-spec">`, hàng `<tr><th>…</th><td>…</td></tr>`) → h2 Cấu tạo (ul) → h2 Nguyên lý hoạt động (ol) → h2 Ưu điểm nổi bật (h3 + p) → h2 Lưu ý khi sử dụng (ul) → h2 Câu hỏi thường gặp (h3 + p; câu cuối về giá: `<a href="tel:0974708603">0974 708 603</a>` + `<a href="/lien-he/">trang liên hệ</a>`) → h2 Liên hệ tư vấn và báo giá (CÔNG TY CP SX MÁY ĐỨC THÀNH, hotline `0974 708 603 – 0989 139 855`, 2–3 link nội bộ tới danh mục/sản phẩm liên quan lấy từ Store API).
- Danh mục (id): 20 Máy đóng gói, 21 Máy đóng gói dạng bột, 22 dạng hạt, 23 dạng lỏng/dịch sệt, 24 Máy chiết rót, 25 Máy chiết rót chất lỏng, 26 Máy chiết rót dịch sệt/kem, 27 Máy dược & mỹ phẩm, 28 Máy trộn nguyên liệu, 29 Thiết bị phụ trợ, 30 Máy dán nhãn, 31 Máy in date, 32 Máy seal màng, 33 Máy viền mí lon. Chọn 1–2 danh mục đúng nhất.
- Rank Math: `rank_math_title` ≤ 60 ký tự, kết thúc "| Đức Thành"; `rank_math_description` ≤ 160 ký tự, có số liệu chính + "0974 708 603"; `rank_math_focus_keyword` = tên loại máy (vd "máy viền nắp").
- **Bài Facebook** (`dtfb_message`, plugin tự đăng ảnh bìa + nội dung lên Fanpage khi publish):
  1. Dòng đầu bắt đầu NGAY bằng từ khoá (tên máy) + công dụng; KHÔNG icon/emoji đầu dòng.
  2. 1–2 câu vấn đề/lợi ích, lặp từ khoá tự nhiên + 1–2 tên gọi khác.
  3. 4–6 dòng ✅ thông số → "🎯 Phù hợp: …".
  4. "🏭 Đức Thành – tư vấn, lắp đặt & bảo hành tận nơi" → "📞 Hotline/Zalo: 0974 708 603 – 0989 139 855".
  5. 1 câu hỏi mở mời nhắn tin (không "like/share/tag nếu…").
  6. 3–5 hashtag (tên máy không dấu, nhóm máy, #ducthanh). KHÔNG link/URL, KHÔNG #quangcao, không "nhất/số 1".

## Bước 4 – Ảnh bìa
```bash
python3 - <<'E'
from PIL import Image
im=Image.open('anh/<STT>/1.png').convert('RGB'); im.thumbnail((1000,1000),Image.LANCZOS)
im.save('<slug>-duc-thanh.webp','WEBP',quality=80,method=6)
E
```

## Bước 5 – Một lệnh: tạo + đăng + kiểm tra + nạp cache
File `web-jobs/dang-stt-<STT>.json` (commit cùng file webp):
```json
{"steps":[
 {"id":"anh","method":"POST","path":"/wp/v2/media","file":"<slug>-duc-thanh.webp","filename":"<slug>-duc-thanh.webp","pick":["id","source_url"]},
 {"id":"alt","method":"POST","path":"/wp/v2/media/{{anh.id}}","body":{"alt_text":"<Tên máy> – Đức Thành","title":"<Tên máy>"},"pick":["id"]},
 {"id":"sp","method":"POST","path":"/wc/v3/products","body":{"name":"…","slug":"…","status":"draft","type":"simple","description":"…","short_description":"…","categories":[{"id":27}],"catalog_visibility":"visible","images":[{"id":"{{anh.id}}"}],"meta_data":[{"key":"dtfb_message","value":"…"}]},"pick":["id","slug","status","permalink"]},
 {"id":"seo","method":"POST","path":"/rankmath/v1/updateMeta","body":{"objectID":"{{sp.id}}","objectType":"post","meta":{"rank_math_title":"…","rank_math_description":"…","rank_math_focus_keyword":"…"}},"pick":[]},
 {"id":"pub","method":"PUT","path":"/wc/v3/products/{{sp.id}}","body":{"status":"publish"},"pick":["id","status","permalink"]},
 {"wait":12},
 {"id":"kt","method":"GET","path":"/wc/v3/products/{{sp.id}}?_fields=id,status,permalink,meta_data","pick":["id","status","permalink","meta_data"]},
 {"warm":["/","{{pub.permalink}}","/<slug-danh-muc>/"]},
 {"warm":["/","{{pub.permalink}}","/<slug-danh-muc>/"]}
]}
```
- Tạo file JSON bằng Python (`json.dump(..., ensure_ascii=False)`) để không lỗi dấu ngoặc kép trong HTML.
- KHÔNG xoá toàn bộ cache web. Chỉ nạp lại như trên.
- Đọc kết quả: `ok: true`; bước `kt` có `status: publish`; trong `meta_data` tìm `dtfb_status` = "Đã đăng … (ID pageid_postid)" → link Facebook `https://www.facebook.com/<ID>`. Nếu là "Lỗi …" → ghi nguyên văn vào báo cáo (lỗi code 190/200 = mã Fanpage hết hạn, người dùng phải lấy mã mới).
- Bước nào lỗi (ok false): KHÔNG thử đăng lại lung tung. Nếu sản phẩm đã tạo nhưng chưa publish thì để nguyên bản nháp, báo lỗi nguyên văn.

## Bước 6 – Dọn dẹp, ghi vào Google Sheet và ghi nhận
1. Lệnh cập nhật Sheet `web-jobs/sheet-stt-<STT>.json` (giờ Việt Nam, dạng `31/10/2026 16:41`):
   ```json
   {"steps":[{"sheet_update":[{"stt":"<STT>","fields":{"Tên máy":"<tên máy>","Trạng thái":"Đã đăng","Thời gian đăng":"<dd/mm/yyyy HH:MM>","Link web":"<link web>","Link Facebook":"https://www.facebook.com/<ID>"}}]}]}
   ```
   Đăng lỗi → "Trạng thái":"Lỗi – <tóm tắt>". Máy bị bỏ qua vì chưa có ảnh → thêm phần tử `{"stt":"x","fields":{"Trạng thái":"Chưa có ảnh"}}` (chỉ khi ô Trạng thái đang trống/khác). Kết quả lỗi "chưa cài SHEET_URL/SHEET_KEY" → ghi vào báo cáo, không coi là lỗi đăng bài.
2. `git rm` file webp; thêm vào `danh-sach/da-dang.json`: `"<STT>": {"ten","product_id","link","facebook","ngay"}`; commit + push.
2. Báo cáo (gửi bằng SendUserMessage): "Đã đăng STT <số> – <tên máy>: <link web> | Facebook: <link>" + mục thông số trang nguồn không có (nếu có) + máy bị bỏ qua vì chưa có ảnh (nếu có).
