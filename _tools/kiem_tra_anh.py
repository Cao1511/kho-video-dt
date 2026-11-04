#!/usr/bin/env python3
"""Kiem tra anh may: KICH THUOC anh may da tach nen (bat buoc DAT) + diem net tham khao.

  python _tools/kiem_tra_anh.py may.png            -> kiem tra anh may da tach nen (truoc khi ghep khung)
  python _tools/kiem_tra_anh.py anh/<STT>/1.png    -> kiem tra anh thanh pham

In ra DAT / CHUA DAT. CHUA DAT thi phai lam lai buoc "lam net bang AI" (xem AGENTS.md).
Moc chuan: anh may so 8 (lam lai 03/11/2026, nguoi dung khen dep) ~3470 diem.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

NGUONG_THANH_PHAM = 2500
NGUONG_RONG_MAY = 1400


def diem_net(gray):
    a = np.asarray(gray.filter(ImageFilter.FIND_EDGES), dtype=float)
    return float(a.var())


def main(f):
    im = Image.open(f)
    ok = True
    if im.mode == "RGBA" and "anh/" not in f.replace("\\", "/"):
        bbox = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        if not bbox:
            print("CHUA DAT: anh khong co may (nen trong suot het)"); return 1
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        print(f"Kich thuoc may: {w}x{h}px (can rong >= {NGUONG_RONG_MAY}px hoac cao >= {NGUONG_RONG_MAY}px)")
        if max(w, h) < NGUONG_RONG_MAY:
            ok = False
            print("  -> may qua nho, phong to se mo: phai lam net bang AI o do phan giai cao")
        crop = im.crop(bbox).convert("RGB")
        bg = Image.new("RGB", crop.size, "white"); bg.paste(crop, mask=im.crop(bbox).getchannel("A"))
        s = diem_net(bg.convert("L").resize((1000, max(1, int(1000 * h / w)))))
        print(f"Diem net (may, chuan hoa 1000px): {s:.0f}")
    else:
        w, h = im.size
        g = im.convert("L").crop((int(w * .05), int(h * .3), int(w * .95), int(h * .75)))
        s = diem_net(g)
        print(f"Diem net tham khao: {s:.0f} (CHI DE THAM KHAO, khong dung de chan: may cao/manh nhieu nen trang"
              " thi diem thap du anh net). Danh gia bang mat: so voi anh/8/1.png o muc phong 100%.")
    print("DAT" if ok else "CHUA DAT – lam lai buoc lam net bang AI (AGENTS.md, Buoc 3.1)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
