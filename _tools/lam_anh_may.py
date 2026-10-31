#!/usr/bin/env python3
"""Khuon anh san pham Duc Thanh – dung khung chuan _tools/mau-anh/khung-chuan.png (moi may dung khung nay)

Vi du:
  python _tools/lam_anh_may.py --may may.png --minh-hoa sp.png --out anh/1/1.png \
     --ten "MÁY DÁN NHÃN|CHAI LỌ TỰ ĐỘNG" --model "ZS-TB500" \
     --o "chai:Dán được|*các loại chai, lọ|(Ø ≤ 100mm)" \
     --o "banh-rang:Bán tự động|- Vận hành ổn định" \
     --o "chinh-xac:Chính xác|- Thẩm mỹ cao"

--may       anh may PNG nen trong suot (tot nhat; nen trang thi tu tach nen)
--ten       ten may, | de xuong dong (2 dong la dep nhat)
--model     (tuy chon) ma may -> ghi trong khung trang; KHONG co ma thi bo, khung trang tu bien mat
--o         dung 3 lan: "icon:dong 1|dong 2|dong 3"; dong bat dau bang * thi in dam
            icon: chai, banh-rang, chinh-xac, toc-do, cong-suat, man-hinh, plc, kg,
                  the-tich, inox, thung, voi, nhiet-do, tui
--minh-hoa  (tuy chon) anh san pham may xu ly, goc tren phai
Chi can: pip install pillow
"""
import argparse, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
W = H = 1254
S = 4                       # ve to 4 lan roi thu nho -> mep muot

# --- kich thuoc & mau lay tu anh mau ---
TOP_L, TOP_R, BOT = 1012, 1064, 1238   # dinh o ten / dinh dai thong so / day dai xanh
PANEL_R = 372                          # mep phai phan phang cua o ten
DIAG_BOT = 520                         # duong cheo cham day o x nay
L_TOP, L_BOT = (2, 108, 220), (0, 86, 180)
R_LEFT, R_RIGHT = (0, 62, 140), (0, 98, 196)
CYAN = (40, 200, 255)
WHITE = (255, 255, 255)
MODEL_BLUE = (8, 62, 160)


def font(w, size):
    f = {"black": "Inter-Black.otf", "xbold": "Inter-ExtraBold.otf", "bold": "Inter-Bold.otf",
         "semi": "Inter-SemiBold.otf", "med": "Inter-Medium.otf", "reg": "Inter-Regular.otf"}[w]
    return ImageFont.truetype(os.path.join(FONT_DIR, f), max(1, int(round(size))))


def tw(f, t):
    b = f.getbbox(t)
    return b[2] - b[0]


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def grad(w, h, c1, c2, horizontal):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    n = w if horizontal else h
    for i in range(n):
        c = lerp(c1, c2, i / max(1, n - 1))
        d.line([(i, 0), (i, h)] if horizontal else [(0, i), (w, i)], fill=c)
    return g


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def sc(pts):
    return [(x * S, y * S) for x, y in pts]


def mask(pts):
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).polygon(sc(pts), fill=255)
    return m


def cut_background(im):
    im = im.convert("RGBA")
    if im.getextrema()[3][0] < 250:
        return im
    r, g, b = im.convert("RGB").split()
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    seed = mn.point(lambda v: 255 if v >= 240 else 0)
    w, h = seed.size
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if seed.getpixel((x, y)) == 255:
            ImageDraw.floodfill(seed, (x, y), 128)
    bg = seed.point(lambda v: 255 if v == 128 else 0)
    alpha = ImageChops.invert(bg).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    im.putalpha(alpha)
    return im


def trim(im):
    box = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop(box) if box else im


def fit(im, bw, bh):
    k = min(bw / im.width, bh / im.height)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


# ---------------- icon: vong tron vien trang + hinh trang ----------------
def icon(d, kind, cx, cy, r):
    t = 3.2 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=int(t))
    a = r * 0.56
    lw = int(3 * S)
    if kind == "chai":
        d.rounded_rectangle([cx - a * 0.5, cy - a * 0.25, cx + a * 0.5, cy + a * 1.0], radius=a * 0.18, outline=WHITE, width=lw)
        d.line([(cx - a * 0.5, cy - a * 0.2), (cx - a * 0.25, cy - a * 0.55), (cx - a * 0.25, cy - a * 0.75)], fill=WHITE, width=lw, joint="curve")
        d.line([(cx + a * 0.5, cy - a * 0.2), (cx + a * 0.25, cy - a * 0.55), (cx + a * 0.25, cy - a * 0.75)], fill=WHITE, width=lw, joint="curve")
        d.rounded_rectangle([cx - a * 0.34, cy - a * 1.08, cx + a * 0.34, cy - a * 0.75], radius=a * 0.06, outline=WHITE, width=lw)
    elif kind == "banh-rang":
        n, ro, ri = 8, a * 1.0, a * 0.74
        pts = []
        for i in range(n * 4):
            ang = 2 * math.pi * i / (n * 4) - math.pi / 2
            rr = ro if (i % 4) in (0, 1) else ri
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=WHITE)
        d.ellipse([cx - a * 0.32, cy - a * 0.32, cx + a * 0.32, cy + a * 0.32], fill=(0, 76, 160))
    elif kind == "chinh-xac":
        d.ellipse([cx - a * 0.72, cy - a * 0.72, cx + a * 0.72, cy + a * 0.72], outline=WHITE, width=lw)
        for x1, y1, x2, y2 in [(0, -1.1, 0, -0.38), (0, 0.38, 0, 1.1), (-1.1, 0, -0.38, 0), (0.38, 0, 1.1, 0)]:
            d.line([(cx + x1 * a, cy + y1 * a), (cx + x2 * a, cy + y2 * a)], fill=WHITE, width=lw)
        d.ellipse([cx - a * 0.14, cy - a * 0.14, cx + a * 0.14, cy + a * 0.14], fill=WHITE)
    elif kind == "toc-do":
        d.arc([cx - a, cy - a, cx + a, cy + a], 150, 390, fill=WHITE, width=lw)
        ang = math.radians(-40)
        d.line([(cx, cy), (cx + a * 0.8 * math.cos(ang), cy + a * 0.8 * math.sin(ang))], fill=WHITE, width=lw)
        d.ellipse([cx - lw, cy - lw, cx + lw, cy + lw], fill=WHITE)
    elif kind == "cong-suat":
        p = [(0.18, -1), (-0.55, 0.12), (-0.02, 0.12), (-0.18, 1), (0.55, -0.15), (0.03, -0.15)]
        d.polygon([(cx + x * a, cy + y * a) for x, y in p], fill=WHITE)
    elif kind == "man-hinh":
        d.rounded_rectangle([cx - a, cy - a * 0.72, cx + a, cy + a * 0.45], radius=lw, outline=WHITE, width=lw)
        d.line([(cx, cy + a * 0.45), (cx, cy + a * 0.82)], fill=WHITE, width=lw)
        d.line([(cx - a * 0.45, cy + a * 0.82), (cx + a * 0.45, cy + a * 0.82)], fill=WHITE, width=lw)
    elif kind == "plc":
        d.rounded_rectangle([cx - a * 0.6, cy - a * 0.6, cx + a * 0.6, cy + a * 0.6], radius=lw, outline=WHITE, width=lw)
        d.rectangle([cx - a * 0.22, cy - a * 0.22, cx + a * 0.22, cy + a * 0.22], fill=WHITE)
        for k in (-0.3, 0.3):
            for x1, y1, x2, y2 in [(k, -0.6, k, -0.95), (k, 0.6, k, 0.95), (-0.6, k, -0.95, k), (0.6, k, 0.95, k)]:
                d.line([(cx + x1 * a, cy + y1 * a), (cx + x2 * a, cy + y2 * a)], fill=WHITE, width=lw)
    elif kind == "kg":
        d.polygon([(cx - a * 0.55, cy - a * 0.45), (cx + a * 0.55, cy - a * 0.45), (cx + a * 0.85, cy + a * 0.8), (cx - a * 0.85, cy + a * 0.8)], outline=WHITE, width=lw)
        d.ellipse([cx - a * 0.25, cy - a * 0.95, cx + a * 0.25, cy - a * 0.45], outline=WHITE, width=lw)
        d.text((cx, cy + a * 0.2), "KG", font=font("black", a * 0.62), fill=WHITE, anchor="mm")
    elif kind == "the-tich":
        pts = bezier((cx, cy - a), (cx + a * 0.3, cy - a * 0.4), (cx + a * 0.75, cy), (cx + a * 0.62, cy + a * 0.45)) + \
              bezier((cx + a * 0.62, cy + a * 0.45), (cx + a * 0.45, cy + a * 1.1), (cx - a * 0.45, cy + a * 1.1), (cx - a * 0.62, cy + a * 0.45))[1:] + \
              bezier((cx - a * 0.62, cy + a * 0.45), (cx - a * 0.75, cy), (cx - a * 0.3, cy - a * 0.4), (cx, cy - a))[1:]
        d.line(pts, fill=WHITE, width=lw, joint="curve")
    elif kind == "inox":
        p = [(0, -1), (0.78, -0.62), (0.7, 0.25), (0, 1), (-0.7, 0.25), (-0.78, -0.62)]
        d.polygon([(cx + x * a, cy + y * a) for x, y in p], outline=WHITE, width=lw)
        d.line([(cx - a * 0.32, cy), (cx - a * 0.05, cy + a * 0.3), (cx + a * 0.38, cy - a * 0.3)], fill=WHITE, width=lw)
    elif kind == "thung":
        d.polygon([(cx, cy - a), (cx + a * 0.85, cy - a * 0.5), (cx, cy), (cx - a * 0.85, cy - a * 0.5)], outline=WHITE, width=lw)
        d.line([(cx - a * 0.85, cy - a * 0.5), (cx - a * 0.85, cy + a * 0.5), (cx, cy + a), (cx + a * 0.85, cy + a * 0.5), (cx + a * 0.85, cy - a * 0.5)], fill=WHITE, width=lw, joint="curve")
        d.line([(cx, cy), (cx, cy + a)], fill=WHITE, width=lw)
    elif kind == "voi":
        d.rectangle([cx - a * 0.5, cy - a, cx + a * 0.5, cy - a * 0.35], outline=WHITE, width=lw)
        d.polygon([(cx - a * 0.5, cy - a * 0.35), (cx + a * 0.5, cy - a * 0.35), (cx + a * 0.12, cy + a * 0.2), (cx - a * 0.12, cy + a * 0.2)], outline=WHITE, width=lw)
        for k in (0.45, 0.75, 1.0):
            d.ellipse([cx - lw, cy + a * k - lw, cx + lw, cy + a * k + lw], fill=WHITE)
    elif kind == "nhiet-do":
        d.rounded_rectangle([cx - a * 0.2, cy - a, cx + a * 0.2, cy + a * 0.3], radius=a * 0.2, outline=WHITE, width=lw)
        d.ellipse([cx - a * 0.42, cy + a * 0.2, cx + a * 0.42, cy + a * 1.0], fill=WHITE)
    elif kind == "tui":
        d.polygon([(cx - a * 0.6, cy - a * 0.75), (cx + a * 0.6, cy - a * 0.75), (cx + a * 0.75, cy + a), (cx - a * 0.75, cy + a)], outline=WHITE, width=lw)
        d.line([(cx - a * 0.6, cy - a * 0.45), (cx + a * 0.6, cy - a * 0.45)], fill=WHITE, width=lw)
    else:
        raise SystemExit(f"Icon khong co: {kind}")


def glow_line(base, pts, color, width, blur):
    """Duong vien phat sang: 1 lop mo rong + 1 lop net."""
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).line(sc(pts), fill=color + (200,), width=int(width * S * 2.4), joint="curve")
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur * S)))
    lay2 = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay2).line(sc(pts), fill=color + (255,), width=int(width * S), joint="curve")
    base.alpha_composite(lay2)


CX = 0.72   # chu thong so hep lai nhu mau


def text_narrow(base, xy, t, f, fill):
    """Ve chu hep ngang (anchor trai-giua) len anh RGBA."""
    bb = f.getbbox(t)
    w, h = bb[2] + 8, int(f.size * 1.6)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((0, h / 2), t, font=f, fill=fill, anchor="lm")
    lay = lay.resize((max(1, int(w * CX)), h), Image.LANCZOS)
    base.alpha_composite(lay, (int(xy[0]), int(xy[1] - h / 2)))


KHUNG = os.path.join(HERE, "mau-anh", "khung-chuan.png")   # khung chuan cua nguoi dung
PILL = (38, 1163, 415, 1218)                               # khung trang ghi ma may
SEPS = (738, 1003)                                         # 2 vach ngan o thong so


def xoa_khung_trang(fr):
    """May khong co ma: xoa khung trang, to lai bang mau nen xanh (noi suy theo cot)."""
    x1, y1, x2, y2 = PILL
    ya, yb = y1 - 6, y2 + 5
    px = fr.load()
    for x in range(x1 - 4, x2 + 5):
        ca, cb = px[x, ya], px[x, yb]
        for y in range(ya + 1, yb):
            t = (y - ya) / (yb - ya)
            px[x, y] = tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(4))
    return fr


def build(a):
    frame = Image.open(KHUNG).convert("RGBA").resize((W, H), Image.LANCZOS)
    if not a.model:
        frame = xoa_khung_trang(frame)

    # mat na: phan khong phai nen trang (logo + dai xanh) -> luon nam tren cung, may nam phia sau
    r, g, b, _ = frame.split()
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    top_mask = mn.point(lambda v: 255 if v < 236 else 0)
    keep = Image.new("L", (W, H), 0)
    ImageDraw.Draw(keep).rectangle([0, 990, W, H], fill=255)
    ImageDraw.Draw(keep).rectangle([40, 30, 370, 290], fill=255)
    top_mask = ImageChops.multiply(top_mask, keep).filter(ImageFilter.GaussianBlur(0.8))

    img = frame.copy()
    # ---------- may ----------
    may = trim(cut_background(Image.open(a.may)))
    may = fit(may, 1150, TOP_R - 250)
    mx = (W - may.width) // 2 + 20
    my = TOP_R + 4 - may.height
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse([mx + may.width * 0.06, my + may.height - 26, mx + may.width * 0.94, my + may.height + 18], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    img = Image.composite(Image.new("RGBA", (W, H), (110, 118, 130, 255)), img, sh.point(lambda v: int(v * 0.5)))
    img.alpha_composite(may, (mx, my))
    img = Image.composite(frame, img, top_mask)          # dai xanh + logo de len tren may

    # ---------- minh hoa goc phai ----------
    if a.minh_hoa:
        mh = trim(cut_background(Image.open(a.minh_hoa)))
        mh = fit(mh, 290, 270)
        img.alpha_composite(mh, (W - 36 - mh.width, 36))

    # ---------- chu + icon: ve to S lan tren lop trong suot ----------
    big = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)

    # ten may: canh giua o xanh ben trai, tu co chu cho vua khung
    lines = [x.strip() for x in a.ten.split("|") if x.strip()]
    top_y = TOP_L + 10
    bot_y = (PILL[1] - 8) if a.model else (BOT - 14)
    max_w = 370
    size = 66
    while size > 26:
        f = font("black", size)
        if max(tw(f, t) for t in lines) <= max_w and size * 1.12 * len(lines) <= (bot_y - top_y):
            break
        size -= 1
    lh = size * 1.12
    cx_name = (PILL[0] + PILL[2]) / 2
    y0 = (top_y + bot_y) / 2 - lh * len(lines) / 2 + lh / 2
    shl = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shl)
    for i, t in enumerate(lines):
        sd.text((cx_name * S, (y0 + i * lh + 3) * S), t, font=font("black", size * S), fill=(0, 30, 90, 140), anchor="mm")
    big.alpha_composite(shl.filter(ImageFilter.GaussianBlur(4 * S)))
    for i, t in enumerate(lines):
        d.text((cx_name * S, (y0 + i * lh) * S), t, font=font("black", size * S), fill=WHITE, anchor="mm")

    # ma may trong khung trang
    if a.model:
        x1, y1, x2, y2 = PILL
        ms = 46
        while ms > 20 and tw(font("black", ms), a.model) > (x2 - x1 - 44):
            ms -= 1
        d.text((((x1 + x2) / 2) * S, ((y1 + y2) / 2 + 1) * S), a.model, font=font("black", ms * S), fill=MODEL_BLUE, anchor="mm")

    # 3 o thong so (vach ngan da co san trong khung)
    specs = []
    for sp in a.o[:3]:
        k, txt = sp.split(":", 1)
        specs.append((k.strip(), [x for x in txt.split("|") if x.strip()]))
    starts = [473, SEPS[0], SEPS[1]]
    ends = [SEPS[0], SEPS[1], W - 6]
    r_ = 39
    gap = 12
    def fw(t, size):
        return tw(font("bold" if t.startswith("*") else "med", size), t.lstrip("*").strip()) * CX
    avail = [ends[i] - starts[i] - 17 - 2 * r_ - gap - 6 for i in range(3)]
    cy = (TOP_R + BOT) / 2 + 1
    ts = 25
    while ts > 15:
        if all(fw(t, ts) <= avail[i] for i, (_, tl) in enumerate(specs) for t in tl) and \
           all(ts * 1.3 * len(tl) <= (BOT - TOP_R) - 30 for _, tl in specs):
            break
        ts -= 1
    lh2 = ts * 1.3
    for i, (kind, tl) in enumerate(specs):
        icx = starts[i] + 17 + r_
        icon(d, kind, icx * S, cy * S, r_ * S)
        ty0 = cy - lh2 * len(tl) / 2 + lh2 / 2
        for j, t in enumerate(tl):
            text_narrow(big, ((icx + r_ + gap) * S, (ty0 + j * lh2) * S), t.lstrip("*").strip(),
                        font("bold" if t.startswith("*") else "med", ts * S), WHITE)

    img.alpha_composite(big.resize((W, H), Image.LANCZOS))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    img.convert("RGB").save(a.out, optimize=True)
    print("Da luu:", a.out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--may", required=True)
    p.add_argument("--ten", required=True)
    p.add_argument("--model")
    p.add_argument("--o", action="append", required=True)
    p.add_argument("--minh-hoa")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    if len(a.o) != 3:
        raise SystemExit("Can dung 3 lan --o")
    build(a)
