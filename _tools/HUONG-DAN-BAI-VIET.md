# Quy trình TỰ ĐỘNG viết + đăng 1 bài "Kiến thức máy móc" mỗi ngày (chạy theo lịch, không cần duyệt)

Người dùng (04/11/2026) yêu cầu: mỗi ngày tự đăng 1 bài viết chia sẻ (mục Tin tức / danh mục "Kiến thức máy móc", id 34) lên mayducthanh.vn, chuẩn SEO, dễ lan toả; plugin tự đăng kèm Facebook. Mỗi lần chạy đăng ĐÚNG 1 bài. Báo cáo tiếng Việt, ngắn. Gộp lệnh, ít lượt gọi công cụ.

Thao tác web qua GitHub Actions (ghi `web-jobs/<ten>.json` → commit + push → chờ → `git pull` → đọc `web-results/<ten>.json`; định dạng ở đầu `_tools/web_runner.py`). Lệnh chờ:
```bash
cho(){ sleep 12; for i in $(seq 1 30); do git pull -q --rebase origin video 2>/dev/null; [ -f web-results/$1.json ] && break; sleep 6; done; cat web-results/$1.json; }
```
Commit kèm dòng Co-Authored-By/Claude-Session theo hướng dẫn hệ thống.

## Bước 1 – Chọn chủ đề (1 lệnh đọc)
- Đọc `danh-sach/bai-viet.json` (bài đã đăng) + `_tools/chu-de-bai-viet.md` (kho chủ đề). Lấy chủ đề ĐẦU TIÊN chưa viết (so ý chính, không trùng từ khoá chính với bài cũ).
- Lệnh `web-jobs/bv-chuan-bi-<ngày>.json` lấy dữ liệu link nội bộ + ảnh:
```json
{"steps":[
 {"id":"sp","method":"GET","path":"/wc/v3/products?search=<1–2 từ của chủ đề, URL-encode>&status=publish&per_page=10&_fields=id,name,permalink,images","pick":["id","name","permalink","images"]},
 {"id":"dm","method":"GET","path":"/wc/v3/products/categories?per_page=50&_fields=id,name,slug,count","pick":["id","name","slug","count"]},
 {"id":"bv","method":"GET","path":"/wp/v2/posts?per_page=20&_fields=id,title,link","pick":["id","title","link"]}]}
```
  Danh mục có link dạng `https://mayducthanh.vn/<slug>/`. Bài viết cũ có link trong `bv`.

## Bước 2 – Tìm hiểu (chỉ khi cần số liệu)
- Bài chủ yếu là kinh nghiệm/so sánh/hướng dẫn chung → viết từ kiến thức kỹ thuật phổ thông, KHÔNG bịa số liệu cụ thể (giá, năng suất của hãng khác…). Cần số liệu → 1–2 WebSearch, chỉ dùng nguồn đáng tin, không chép nguyên văn.
- Số liệu máy của Đức Thành → chỉ lấy từ bài sản phẩm trên web (bước 1).

## Bước 3 – Viết bài chuẩn SEO (theo `_tools/CHUAN-SEO.md` mục 0 + 5b + 4 + 6)
- **Tiêu đề (H1)** 50–65 ký tự, BẮT ĐẦU bằng từ khoá chính, có lợi ích/con số rõ (vd "Máy đóng gói dạng hạt: cốc đong hay cân điện tử?", "8 lỗi thường gặp của máy đóng gói và cách khắc phục"). Không giật tít sai sự thật.
- **Slug** ngắn không dấu = từ khoá chính (≤ 6 từ), không trùng slug cũ.
- **Nội dung 1.000–1.500 chữ**, HTML dạng khối Gutenberg như bài mẫu id 339 (`<!-- wp:paragraph --><p>…</p><!-- /wp:paragraph -->`, `<!-- wp:heading --><h2>…</h2><!-- /wp:heading -->`, `<!-- wp:list --><ul><li>…</li></ul><!-- /wp:list -->`; bảng: `<!-- wp:table --><figure class="wp-block-table"><table>…</table></figure><!-- /wp:table -->`):
  1. Mở bài 2–3 câu: từ khoá chính trong câu đầu, nêu vấn đề người đọc gặp + bài này giúp gì.
  2. 4–7 mục H2 (có thể đánh số), mỗi mục có ý cụ thể, ví dụ thực tế xưởng sản xuất Việt Nam; 1 bảng so sánh nếu là bài so sánh.
  3. H2 "Câu hỏi thường gặp" – 3–5 câu H3 + trả lời ngắn (câu khách hay hỏi thật).
  4. H2 cuối: kêu gọi tư vấn – Đức Thành, hotline `<a href="tel:0974708603"><strong>0974 708 603</strong></a> – <a href="tel:0989139855"><strong>0989 139 855</strong></a>`, `<a href="https://mayducthanh.vn/lien-he/">gửi yêu cầu báo giá</a>`.
  - **3–5 link nội bộ**: 1–2 danh mục, 1–2 bài sản phẩm cụ thể, 1 bài viết cũ liên quan (anchor = tên máy/chủ đề, không "xem tại đây").
  - Viết tự nhiên, câu ngắn, xưng "bạn", không "nhất/số 1", không chê đối thủ, không bịa thông số.
- **Excerpt** 1–2 câu (≤ 160 ký tự) có từ khoá.
- **Rank Math**: `rank_math_title` ≤ 60 ký tự bắt đầu bằng từ khoá, kết thúc "| Đức Thành"; `rank_math_description` 140–160 ký tự (từ khoá + lợi ích + "0974 708 603"); `rank_math_focus_keyword` = từ khoá chính.
- **Bài Facebook (`dtfb_message`)** theo CHUAN-SEO mục 4 dạng bài kiến thức: dòng đầu chứa từ khoá (không icon) → 2–3 câu tóm ý → 4–7 ý chính 🔹 (đọc được ngay trên Facebook, không dẫn sang web) → 1 câu hỏi mở thật → "🏭 Đức Thành – tư vấn, lắp đặt & bảo hành tận nơi" + "📞 Hotline/Zalo: 0974 708 603 – 0989 139 855" → 3–5 hashtag. KHÔNG link, không #quangcao.
- **Ảnh đại diện** (`featured_media`): dùng ảnh bìa (id `images[0].id`) của bài sản phẩm liên quan nhất ở bước 1; không có thì ảnh của bài viết cũ cùng nhóm (284 máy đóng gói, 271 máy chiết rót, 267 máy trộn). KHÔNG dùng ảnh trên mạng.

## Bước 4 – Một lệnh: tạo nháp → SEO → đăng → kiểm tra → nạp cache
Tạo file JSON bằng Python (`json.dump(..., ensure_ascii=False)`), `web-jobs/bv-dang-<slug>.json`:
```json
{"steps":[
 {"id":"bv","method":"POST","path":"/wp/v2/posts","body":{"title":"…","slug":"…","content":"…","excerpt":"…","status":"draft","categories":[34],"featured_media":<id>,"meta":{"dtfb_message":"…"}},"pick":["id","link","status"]},
 {"id":"seo","method":"POST","path":"/rankmath/v1/updateMeta","body":{"objectID":"{{bv.id}}","objectType":"post","meta":{"rank_math_title":"…","rank_math_description":"…","rank_math_focus_keyword":"…"}},"pick":[]},
 {"id":"pub","method":"POST","path":"/wp/v2/posts/{{bv.id}}","body":{"status":"publish"},"pick":["id","link","status"]},
 {"wait":12},
 {"id":"kt","method":"GET","path":"/wp/v2/posts/{{bv.id}}?_fields=id,link,status,meta","pick":["id","link","status","meta"]},
 {"warm_all":true}
]}
```
Đọc kết quả: `ok: true`, `kt.status = publish`; `kt.meta.dtfb_status` "Đã đăng … (ID …)" → link Facebook `https://www.facebook.com/<dtfb_fb_id>`; "Lỗi …" → ghi nguyên văn vào báo cáo (190/200 = mã Fanpage hết hạn). Bước lỗi → KHÔNG đăng lại lung tung; bài nháp để nguyên, báo lỗi.

## Bước 5 – Ghi nhận (1 commit)
Thêm vào `danh-sach/bai-viet.json`: `"<id>": {"tieu_de","slug","tu_khoa","link","facebook","ngay"}`; chủ đề mới tự đề xuất thì thêm vào `_tools/chu-de-bai-viet.md`. Commit + push.

## Báo cáo (SendUserMessage)
"Đã đăng bài viết: <tiêu đề> – <link web> | Facebook: <link>" (1 dòng, kèm từ khoá chính).

## Quy tắc
- Không bịa số liệu; không "nhất/số 1"; không link/URL trong bài Facebook; không icon đầu bài Facebook; hotline 0974 708 603 – 0989 139 855; email liên hệ mayducthanhvn@gmail.com (nếu cần ghi).
- KHÔNG xoá toàn bộ cache web (đã có `warm_all`). Không sửa/xoá bài cũ. Không sửa cài đặt web (Rank Math, giao diện, đường dẫn).
