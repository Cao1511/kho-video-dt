# Hướng dẫn cho Codex – làm ảnh sản phẩm Đức Thành

Kho này chứa ảnh/video để đăng web mayducthanh.vn (CÔNG TY CP SX MÁY ĐỨC THÀNH) và mạng xã hội.
Luôn làm trên nhánh `video`. Trả lời người dùng bằng tiếng Việt, ngắn gọn, dễ hiểu.

Người dùng sẽ nói kiểu:
- "Làm ảnh máy số 3" → tự tra Google Sheet lấy tên máy + link thông số, tự lấy ảnh máy từ link.
- "Làm ảnh máy số 3, dùng ảnh này" (kèm ảnh) → dùng ảnh người dùng đưa làm hình máy; thông số vẫn lấy từ link trong Sheet.
- "Làm ảnh máy này" (chỉ kèm ảnh, không nói số) → đọc chữ/link/tên máy có trong ảnh để tìm đúng dòng trong Sheet (xem Bước 1).
- "Làm lại ảnh máy số 3" → được phép ghi đè `anh/3/1.png`.

---

## Bước 1 – Xác định đúng máy (STT)

Bảng "DS mẫu máy": https://docs.google.com/spreadsheets/d/1Zwy4QBWBwFZ-wzkURH7--dRxB_BRhgOw_Tzt-1zzDVg/edit?usp=sharing (đã chia sẻ công khai, chỉ đọc). Tải về dạng CSV:
```bash
curl -sL "https://docs.google.com/spreadsheets/d/1Zwy4QBWBwFZ-wzkURH7--dRxB_BRhgOw_Tzt-1zzDVg/export?format=csv&gid=0" -o /tmp/ds-may.csv
```
Cột A = STT, B = Tên máy, C = Link mẫu (link thông số), D = Link ảnh (công thức tự động, bỏ qua). Dòng 1 là tiêu đề lớn, dòng 2 là tên cột.

- Người dùng nói số STT → lấy đúng dòng đó.
- Người dùng đưa tên máy / link / ảnh → tìm dòng khớp:
  - Ưu tiên khớp Link mẫu (cột C), so phần đường dẫn, bỏ phần sau dấu `?`.
  - Không có link thì khớp Tên máy (cột B), không phân biệt hoa thường, có dấu hay không.
  - Ảnh người dùng đưa có chữ (tên máy, model như "ZS-SV6X", đường link, ảnh chụp màn hình trang web/bảng thông số): đọc chữ trong ảnh để tìm dòng khớp. Nếu ảnh có link thông số mà bảng không có thì dùng link trong ảnh làm nguồn thông số và báo người dùng.
- Chỉ dùng khi tìm thấy ĐÚNG 1 dòng. Không thấy hoặc nhiều dòng → DỪNG, hỏi "máy này là STT số mấy?". Không đoán.
- Tải bảng lỗi (bảng chưa chia sẻ) → hỏi người dùng số STT và link thông số.
- Không bao giờ đổi STT. Ảnh luôn lưu theo STT, không theo thứ tự làm.

## Bước 2 – Lấy thông số và ảnh máy thật

1. Mở link mẫu (cột C), đọc: tên/model máy, công dụng, sản phẩm phù hợp (bột, hạt, chất lỏng, kem…), và các thông số chính (công suất, tốc độ, dung tích, số vòi, điều khiển PLC/màn hình cảm ứng, vật liệu inox 304/316…). Bảng thông số đôi khi nằm trong ảnh gallery → mở ảnh gốc (bỏ đuôi kiểu `_600x`) để đọc.
2. Ảnh máy:
   - Người dùng có đưa ảnh → dùng ảnh đó làm hình máy chính.
   - Không có → tải 2–4 ảnh máy rõ nhất từ trang link mẫu (ảnh nền trắng, thấy toàn thân máy).
3. Ghi nhớ 3 thông số đáng giá nhất để đặt vào 3 ô ở dải xanh (xem Bước 3). CHỈ dùng số có thật trong trang/ảnh. Không bịa, không làm tròn lên. Không đủ 3 số thì dùng đặc điểm có thật (vd "Điều khiển PLC", "Inox 304", "Thùng trộn tháo rời").

## Bước 3 – Thiết kế ảnh đúng mẫu

**Ảnh mẫu bắt buộc phải xem trước khi làm:** `_tools/mau-anh/mau-1-may-tron-ibc.png` (máy trộn thùng IBC 1500 lít).
**Logo:** `_tools/mau-anh/logo-duc-thanh-lon.png` (dùng logo thật này, KHÔNG tự vẽ lại logo; không méo, không đổi màu).

### BẮT BUỘC dùng khuôn có sẵn `_tools/lam_anh_may.py` — KHÔNG tự vẽ dải xanh, logo, chữ, icon

Khuôn này vẽ sẵn đúng mẫu (dải xanh mịn, đúng tỉ lệ, logo thật, font Inter có dấu, icon, bóng đổ). Codex chỉ chuẩn bị 2 ảnh + chữ rồi chạy lệnh. Không sửa file khuôn; thấy cần sửa thì báo người dùng.

1. **Ảnh máy nền trong suốt** (`may.png`): lấy ảnh máy thật (ảnh người dùng đưa hoặc ảnh từ link), tách nền bằng rembg:
   ```bash
   pip install "rembg[cpu]" pillow
   rembg i anh-goc.jpg may.png
   ```
   Mở `may.png` kiểm tra: máy đủ, không mất phần inox sáng (phễu, nắp, mép trên), không còn nền/viền xám, không còn logo/chữ nhà cung cấp. Thiếu thì thử ảnh gốc khác hoặc model `rembg i -m isnet-general-use`. KHÔNG dùng AI vẽ lại máy.
2. **Ảnh minh hoạ góc phải** (`minh-hoa.png`, nên có): sản phẩm máy xử lý, nền trắng hoặc trong suốt, không chữ (vd 2 lọ nắp nhôm cho máy viền nắp, bát bột/hạt cho máy trộn, chai cho máy chiết rót, túi gói cho máy đóng gói). Được dùng AI tạo ảnh này.
3. **Chữ:**
   - `--ten`: tên máy IN HOA, 2–3 dòng ngăn bằng `|`, ngắt theo cụm nghĩa, không để 1 chữ lẻ một dòng, mỗi dòng ≤ 13 ký tự. Không ghi model. Vd `"MÁY VIỀN NẮP|TỰ ĐỘNG"`, `"MÁY TRỘN|THÙNG IBC|1500 LÍT"`.
   - 3 lần `--o "icon:dòng 1|dòng 2"`, mỗi dòng ≤ 11 ký tự (dài quá chữ sẽ bị thu nhỏ). Vd `"toc-do:10–13 nghìn|chai/giờ"`, `"cong-suat:Công suất|2 kW"`, `"man-hinh:Màn hình|cảm ứng"`.
   - Icon có sẵn: `toc-do` (tốc độ), `cong-suat` (điện/công suất), `man-hinh` (màn hình cảm ứng), `plc` (điều khiển PLC), `kg` (khối lượng), `the-tich` (dung tích/chất lỏng), `inox` (inox/an toàn), `thung` (thùng/hộp), `voi` (vòi chiết), `chai` (chai/lọ), `nhiet-do` (nhiệt), `tui` (túi gói).
4. **Chạy:**
   ```bash
   python _tools/lam_anh_may.py --may may.png --minh-hoa minh-hoa.png --out anh/<STT>/1.png \
     --ten "MÁY VIỀN NẮP|TỰ ĐỘNG" \
     --o "toc-do:10–13 nghìn|chai/giờ" --o "cong-suat:Công suất|2 kW" --o "man-hinh:Màn hình|cảm ứng"
   ```
   Không để file `may.png`, `minh-hoa.png` trong kho (để ở thư mục tạm ngoài kho).
5. Mở `anh/<STT>/1.png` kiểm tra: máy không bị cắt, không đè logo, chữ đúng dấu. Chưa ổn thì sửa ảnh đầu vào/chữ rồi chạy lại.

**Không được:**
- Vẽ thêm chi tiết máy không có thật, đổi kết cấu máy.
- Ghi số điện thoại, website, Zalo, giá, chữ "tốt nhất/số 1".
- Để lại logo/chữ/watermark của nhà cung cấp gốc (vd ZONESUN) — xoá hoặc che sạch.
- Dùng thông số không có trong link/ảnh.

## Bước 4 – Lưu và đẩy lên GitHub

1. Lưu vào `anh/<STT>/`:
   - `1.png` = ảnh chính theo mẫu ở Bước 3.
   - `2.png`, `3.png`… = ảnh phụ nếu người dùng yêu cầu (vd ảnh máy nền trắng không chữ, ảnh chi tiết).
   - PNG, cạnh tối thiểu 1200 px, mỗi file dưới 3 MB (nén lại nếu lớn hơn).
   - Thư mục đã có ảnh: thêm số tiếp theo; chỉ ghi đè khi người dùng nói "làm lại".
2. Đẩy lên:
   ```bash
   git checkout video
   git pull --rebase origin video
   git add anh/<STT>/
   git commit -m "Anh may so <STT> - <ten may khong dau>"
   git push origin video
   ```
   Push bị từ chối → `git pull --rebase origin video` rồi push lại.
3. Báo lại người dùng (HIỂN THỊ ĐÚNG ẢNH CUỐI `anh/<STT>/1.png` trong chat, không hiện ảnh trung gian như ảnh máy tách nền):
   - "Đã lưu ảnh cho STT <số> – <tên máy>"
   - Link: `https://raw.githubusercontent.com/Cao1511/kho-video-dt/video/anh/<STT>/1.png`
   - 3 thông số đã dùng và nguồn (link/ảnh) để người dùng kiểm tra.
   - Google Sheet cột D tự hiện ảnh sau vài phút (không cần sửa Sheet).

## Không được làm
- KHÔNG sửa/xoá `_tools/`, `.github/`, `web-jobs/`, `web-results/`, `AGENTS.md`.
- KHÔNG xoá ảnh của máy khác.
- KHÔNG đưa mật khẩu, token, thông tin bí mật vào kho (kho công khai).
