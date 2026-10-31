# Huong dan cho Codex – kho anh/video Duc Thanh

Kho nay dung de chuyen anh va video cho viec dang web mayducthanh.vn va mang xa hoi.
Nhanh lam viec: `video` (luon lam tren nhanh nay).

## Khi duoc yeu cau tao anh cho mot may

Nguoi dung co the dua: so STT ("tao anh may so 3"), ten may ("may vien nap"), link mau, hoac ca dong copy tu Google Sheet. Nguoi dung KHONG lam theo thu tu, nen phai xac dinh dung STT cua chinh may do.

STT la so o cot A cua Google Sheet "DS mau may". Anh luon cat theo STT, khong theo thu tu lam.

### Buoc 0 – Tim dung STT (bat buoc truoc khi luu anh)
- Neu nguoi dung da noi ro so STT: dung so do, nhung van doi chieu voi bang ben duoi cho chac.
- Neu chua co so: tai bang ve va tra:
  ```bash
  curl -sL "https://docs.google.com/spreadsheets/d/1Zwy4QBWBwFZ-wzkURH7--dRxB_BRhgOw_Tzt-1zzDVg/export?format=csv&gid=0" -o /tmp/ds-may.csv
  ```
  Cot A = STT, B = Ten may, C = Link mau, D = Link anh. (Dong 1 la tieu de lon, dong 2 la ten cot.)
  - Uu tien khop theo Link mau (cot C) neu nguoi dung dua link (so phan duong dan, bo qua phan sau dau `?`).
  - Khong co link thi khop theo Ten may (cot B), khong phan biet hoa thuong/dau.
- Chi tim thay DUNG 1 dong thi dung STT do. Khong thay hoac thay nhieu dong: DUNG LAI va hoi nguoi dung "may nay la STT so may?". Khong doan.
- Tai bang that bai (bang chua chia se cong khai): hoi nguoi dung so STT.
- Khi bao lai, luon ghi ro: "Da luu anh cho STT <so> – <ten may>".

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
