#!/usr/bin/env python3
"""Khuon anh san pham Duc Thanh – theo mau _tools/mau-anh/mau-2-may-dan-nhan.png

Vi du:
  python _tools/lam_anh_may.py --may may.png --minh-hoa sp.png --out anh/1/1.png \
     --ten "MÁY DÁN NHÃN|CHAI LỌ TỰ ĐỘNG" --model "ZS-TB500" \
     --o "chai:Dán được|*các loại chai, lọ|(Ø ≤ 100mm)" \
     --o "banh-rang:Bán tự động|- Vận hành ổn định" \
     --o "chinh-xac:Chính xác|- Thẩm mỹ cao"

--may       anh may PNG nen trong suot (tot nhat; nen trang thi tu tach nen)
--ten       ten may, | de xuong dong (2 dong la dep nhat)
--model     (tuy chon) ma may, ghi trong khung trang bo tron
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


def build(a):
    # ---------- nen trang, giua sang hon ----------
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).ellipse([80, 60, 1180, 1060], fill=255)
    g = g.filter(ImageFilter.GaussianBlur(200))
    img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), Image.new("RGB", (W, H), (240, 243, 247)), g).convert("RGBA")

    # ---------- may: to, dat sat tren dai xanh ----------
    may = trim(cut_background(Image.open(a.may)))
    may = fit(may, 1150, TOP_R - 250)
    mx = (W - may.width) // 2 + 20
    my = TOP_R + 4 - may.height
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse([mx + may.width * 0.06, my + may.height - 26, mx + may.width * 0.94, my + may.height + 18], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    img = Image.composite(Image.new("RGBA", (W, H), (110, 118, 130, 255)), img, sh.point(lambda v: int(v * 0.5)))
    img.alpha_composite(may, (mx, my))

    # ---------- dai xanh (ve to S lan) ----------
    big = img.resize((W * S, H * S), Image.LANCZOS)
    # do dung theo anh mau: phang toi x=360, cong xuong (420,1060), cheo toi (468,1165), cong vao day (560,1238)
    curve = bezier((360, TOP_L), (398, TOP_L), (410, 1036), (420, 1060))
    curve2 = [(420, 1060)] + [(420 + (468 - 420) * k / 20, 1060 + (1165 - 1060) * k / 20) for k in range(1, 21)]
    curve2 = curve2 + bezier((468, 1165), (478, 1200), (500, 1236), (560, 1238))[1:]
    left = [(0, TOP_L)] + curve + curve2[1:] + [(0, BOT)]
    right = [(0, TOP_R), (W, TOP_R), (W, BOT), (0, BOT)]

    shd = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(shd).polygon(sc(left), fill=255)
    ImageDraw.Draw(shd).polygon(sc(right), fill=255)
    shd = shd.filter(ImageFilter.GaussianBlur(10 * S)).point(lambda v: v // 5)
    big = Image.composite(Image.new("RGBA", big.size, (60, 80, 120, 255)), big, shd)

    big.paste(grad(W * S, H * S, R_LEFT, R_RIGHT, True), (0, 0), mask(right))
    big.paste(grad(W * S, H * S, L_TOP, L_BOT, False), (0, 0), mask(left))
    st = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(st).polygon(sc([(170, TOP_L), (290, TOP_L), (420, BOT), (300, BOT)]), fill=70)
    st = ImageChops.multiply(st.filter(ImageFilter.GaussianBlur(40 * S)), mask(left))
    big = Image.composite(Image.new("RGBA", big.size, (90, 175, 255, 255)), big, st)

    glow_line(big, [(424, TOP_R), (W, TOP_R)], CYAN, 4, 5)
    glow_line(big, [(0, BOT - 5), (W, BOT - 5)], CYAN, 5, 6)
    glow_line(big, [(0, TOP_L)] + curve + curve2[1:], CYAN, 4, 5)

    d = ImageDraw.Draw(big)
    # ---------- ten may ----------
    lines = [x.strip() for x in a.ten.split("|") if x.strip()]
    has_model = bool(a.model)
    name_h = (BOT - TOP_L) - (95 if has_model else 40)
    size = 64
    while size > 30:
        f = font("black", size)
        if max(tw(f, t) for t in lines) <= 385 and size * 1.08 * len(lines) <= name_h:
            break
        size -= 1
    lh = size * 1.1
    cx_name = 226
    y0 = TOP_L + 14 + (name_h - lh * len(lines)) / 2 + lh / 2
    tsh = Image.new("RGBA", big.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tsh)
    for i, t in enumerate(lines):
        td.text((cx_name * S, (y0 + i * lh + 3) * S), t, font=font("black", size * S), fill=(0, 30, 90, 150), anchor="mm")
    big.alpha_composite(tsh.filter(ImageFilter.GaussianBlur(4 * S)))
    for i, t in enumerate(lines):
        d.text((cx_name * S, (y0 + i * lh) * S), t, font=font("black", size * S), fill=WHITE, anchor="mm")

    # ---------- khung ma may ----------
    if has_model:
        py1, py2 = BOT - 82, BOT - 24
        px1, px2 = 38, 412
        d.rounded_rectangle(sc([(px1, py1), (px2, py2)]), radius=(py2 - py1) / 2 * S, fill=WHITE)
        ms = 46
        while ms > 24 and tw(font("black", ms), a.model) > (px2 - px1 - 40):
            ms -= 1
        d.text((((px1 + px2) / 2) * S, ((py1 + py2) / 2 + 1) * S), a.model, font=font("black", ms * S), fill=MODEL_BLUE, anchor="mm")

    # ---------- 3 o thong so ----------
    specs = []
    for s in a.o[:3]:
        k, txt = s.split(":", 1)
        specs.append((k.strip(), [x for x in txt.split("|") if x.strip()]))
    starts = [473, 738, 1003]          # vi tri 3 o theo anh mau
    r = 39
    gap = 12
    def fw(t, size):
        return tw(font("bold" if t.startswith("*") else "med", size), t.lstrip("*").strip()) * CX
    avail = [ (starts[1] - starts[0]) - 17 - 2 * r - gap - 4,
              (starts[2] - starts[1]) - 17 - 2 * r - gap - 4,
              (W - starts[2]) - 17 - 2 * r - gap - 4 ]
    cy = (TOP_R + BOT) / 2 + 1
    ts = 25
    while ts > 17:
        if all(fw(t, ts) <= avail[i] for i, (_, tl) in enumerate(specs) for t in tl) and \
           all(ts * 1.3 * len(tl) <= (BOT - TOP_R) - 34 for _, tl in specs):
            break
        ts -= 1
    lh2 = ts * 1.3
    for i, (kind, tl) in enumerate(specs):
        icx = starts[i] + 17 + r
        icon(d, kind, icx * S, cy * S, r * S)
        ty0 = cy - lh2 * len(tl) / 2 + lh2 / 2
        for j, t in enumerate(tl):
            text_narrow(big, ((icx + r + gap) * S, (ty0 + j * lh2) * S), t.lstrip("*").strip(),
                        font("bold" if t.startswith("*") else "med", ts * S), WHITE)
        if i > 0:
            d.line(sc([(starts[i], TOP_R + 36), (starts[i], BOT - 36)]), fill=(200, 225, 255), width=int(2 * S))

    img = big.resize((W, H), Image.LANCZOS)

    # ---------- minh hoa goc phai ----------
    if a.minh_hoa:
        mh = trim(cut_background(Image.open(a.minh_hoa)))
        mh = fit(mh, 290, 270)
        img.alpha_composite(mh, (W - 36 - mh.width, 36))

    # ---------- logo ----------
    logo = trim(cut_background(Image.open(os.path.join(HERE, "mau-anh", "logo-duc-thanh-lon.png"))))
    logo = fit(logo, 280, 225)
    img.alpha_composite(logo, (60, 50))

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
