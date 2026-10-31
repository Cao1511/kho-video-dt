# Huong dan cho Codex – kho anh/video Duc Thanh

Kho nay dung de chuyen anh va video cho viec dang web mayducthanh.vn va mang xa hoi.
Nhanh lam viec: `video` (luon lam tren nhanh nay).

## Khi duoc yeu cau tao anh cho mot may

Nguoi dung se noi kieu: "tao anh may so 3" hoac "tao anh may vien nap (STT 3)".
STT la so thu tu cua may trong Google Sheet "DS mau may".

1. Tao anh theo yeu cau. Anh phai dung voi may that (dua theo anh/link mau nguoi dung dua), khong ve them chi tiet khong co that, khong chen chu, logo, so dien thoai, website.
2. Luu anh vao thu muc `anh/<STT>/`, dat ten theo thu tu: `1.png`, `2.png`, `3.png`...
   - `1.png` la anh chinh (anh dai dien san pham).
   - Dinh dang PNG, canh dai toi thieu 1200 px, moi file duoi 3 MB.
   - Neu thu muc da co anh: them tiep so moi, KHONG ghi de anh cu tru khi nguoi dung bao "lam lai".
3. Day len GitHub:
   ```bash
   git checkout video
   git pull --rebase origin video
   git add anh/<STT>/
   git commit -m "Anh may so <STT>"
   git push origin video
   ```
   Neu push bi tu choi thi `git pull --rebase origin video` roi push lai.
4. Bao lai cho nguoi dung danh sach link anh dang:
   `https://raw.githubusercontent.com/Cao1511/kho-video-dt/video/anh/<STT>/1.png`

## Khong duoc lam
- KHONG sua hay xoa thu muc `_tools/`, `.github/`, `web-jobs/`, `web-results/`, file `AGENTS.md`.
- KHONG xoa anh cua may khac.
- KHONG dua mat khau, token hay thong tin bi mat vao kho (kho cong khai).
