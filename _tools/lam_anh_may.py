#!/usr/bin/env python3
"""Khuon anh san pham Duc Thanh (co dinh, giong mau mau-1-may-tron-ibc.png).

Vi du:
  python _tools/lam_anh_may.py --may may.png --out anh/1/1.png \
     --ten "MÁY VIỀN NẮP|TỰ ĐỘNG" \
     --o "toc-do:10.000–13.000|chai/giờ" --o "cong-suat:Công suất|2 kW" --o "man-hinh:Màn hình|cảm ứng" \
     --minh-hoa lo-thuoc.png

--may       anh may: PNG nen trong suot (tot nhat) hoac nen trang (tu tach nen).
--ten       ten may, dung | de xuong dong (2-3 dong).
--o         3 lan, dang "icon:dong 1|dong 2". Icon: toc-do, cong-suat, man-hinh, plc,
            kg, the-tich, inox, thung, voi, chai, nhiet-do, tui
--minh-hoa  (tuy chon) anh san pham may xu ly, dat goc tren phai.
Chay: pip install pillow  (chi can Pillow).
"""
import argparse, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
W = H = 1254
S = 4  # ve to gap 4 lan roi thu nho -> net muot, khong rang cua

# Mau lay tu anh mau
BLUE_L1, BLUE_L2 = (0, 98, 204), (0, 76, 186)       # o ten may (tren -> duoi)
BLUE_R1, BLUE_R2 = (0, 62, 160), (0, 96, 214)       # dai thong so (trai -> phai)
CYAN = (0, 190, 255)
CYAN_SOFT = (0, 150, 253)

# Vi tri dai xanh (theo anh mau)
TOP_L = 990      # dinh o ten may
TOP_R = 1040     # dinh dai thong so
BOT = 1212       # day dai xanh (duoi con le trang)
DIAG_TOP_X, DIAG_BOT_X = 360, 500   # duong cheo ngan cach


def font(weight, size):
    name = {"black": "Inter-Black.otf", "xbold": "Inter-ExtraBold.otf",
            "bold": "Inter-Bold.otf", "semi": "Inter-SemiBold.otf"}[weight]
    return ImageFont.truetype(os.path.join(FONT_DIR, name), int(size))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(w, h, c1, c2, horizontal):
    g = Image.new("RGB", (w, h))
    px = g.load()
    n = w if horizontal else h
    cols = [lerp(c1, c2, i / max(1, n - 1)) for i in range(n)]
    d = ImageDraw.Draw(g)
    for i, c in enumerate(cols):
        if horizontal:
            d.line([(i, 0), (i, h)], fill=c)
        else:
            d.line([(0, i), (w, i)], fill=c)
    return g


def poly_mask(points):
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in points], fill=255)
    return m


def cut_background(im):
    """Anh khong co nen trong suot: tach nen trang lien voi mep anh."""
    im = im.convert("RGBA")
    if im.getextrema()[3][0] < 250:      # da co nen trong suot
        return im
    rgb = im.convert("RGB")
    r, g, b = rgb.split()
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    near_white = mn.point(lambda v: 255 if v >= 236 else 0)
    w, h = near_white.size
    seed = near_white.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
                 (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if seed.getpixel((x, y)) == 255:
            ImageDraw.floodfill(seed, (x, y), 128)
    bg = seed.point(lambda v: 255 if v == 128 else 0)
    alpha = ImageChops.invert(bg).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(alpha)
    return im


def trim(im):
    box = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop(box) if box else im


def fit(im, bw, bh):
    k = min(bw / im.width, bh / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


# ---------- icon (ve net trang trong vong tron) ----------
def draw_icon(d, kind, cx, cy, r, lw):
    """d: ImageDraw tren canvas to S lan; toa do da nhan S."""
    wht = (255, 255, 255)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=wht, width=lw)
    a = r * 0.52
    t = max(2, int(lw * 0.9))
    if kind == "toc-do":
        d.arc([cx - a, cy - a, cx + a, cy + a], 150, 390, fill=wht, width=t)
        ang = math.radians(-40)
        d.line([(cx, cy), (cx + a * 0.85 * math.cos(ang), cy + a * 0.85 * math.sin(ang))], fill=wht, width=t)
        d.ellipse([cx - t, cy - t, cx + t, cy + t], fill=wht)
    elif kind == "cong-suat":
        p = [(0.15, -1), (-0.55, 0.12), (-0.02, 0.12), (-0.18, 1), (0.55, -0.15), (0.03, -0.15)]
        d.polygon([(cx + x * a, cy + y * a) for x, y in p], outline=wht, width=t)
    elif kind == "man-hinh":
        d.rounded_rectangle([cx - a, cy - a * 0.75, cx + a, cy + a * 0.45], radius=t, outline=wht, width=t)
        d.line([(cx, cy + a * 0.45), (cx, cy + a * 0.8)], fill=wht, width=t)
        d.line([(cx - a * 0.45, cy + a * 0.8), (cx + a * 0.45, cy + a * 0.8)], fill=wht, width=t)
    elif kind == "plc":
        d.rounded_rectangle([cx - a * 0.6, cy - a * 0.6, cx + a * 0.6, cy + a * 0.6], radius=t, outline=wht, width=t)
        d.rectangle([cx - a * 0.22, cy - a * 0.22, cx + a * 0.22, cy + a * 0.22], fill=wht)
        for k in (-0.3, 0.3):
            for x1, y1, x2, y2 in [(k, -0.6, k, -0.95), (k, 0.6, k, 0.95), (-0.6, k, -0.95, k), (0.6, k, 0.95, k)]:
                d.line([(cx + x1 * a, cy + y1 * a), (cx + x2 * a, cy + y2 * a)], fill=wht, width=t)
    elif kind == "kg":
        d.polygon([(cx - a * 0.55, cy - a * 0.45), (cx + a * 0.55, cy - a * 0.45),
                   (cx + a * 0.85, cy + a * 0.8), (cx - a * 0.85, cy + a * 0.8)], outline=wht, width=t)
        d.ellipse([cx - a * 0.25, cy - a * 0.95, cx + a * 0.25, cy - a * 0.45], outline=wht, width=t)
        f = font("black", a * 0.62)
        d.text((cx, cy + a * 0.2), "KG", font=f, fill=wht, anchor="mm")
    elif kind == "the-tich":
        d.polygon([(cx, cy - a), (cx + a * 0.62, cy + a * 0.1), (cx - a * 0.62, cy + a * 0.1)], fill=None, outline=wht, width=t)
        d.chord([cx - a * 0.64, cy - a * 0.35, cx + a * 0.64, cy + a * 0.95], 0, 180, outline=wht, width=t)
        d.line([(cx - a * 0.5, cy + a * 0.1), (cx + a * 0.5, cy + a * 0.1)], fill=(0, 0, 0, 0), width=t)
    elif kind == "inox":
        p = [(0, -1), (0.78, -0.62), (0.7, 0.25), (0, 1), (-0.7, 0.25), (-0.78, -0.62)]
        d.polygon([(cx + x * a, cy + y * a) for x, y in p], outline=wht, width=t)
        d.line([(cx - a * 0.32, cy), (cx - a * 0.05, cy + a * 0.3), (cx + a * 0.38, cy - a * 0.3)], fill=wht, width=t)
    elif kind == "thung":
        top = [(cx, cy - a), (cx + a * 0.85, cy - a * 0.5), (cx, cy), (cx - a * 0.85, cy - a * 0.5)]
        d.polygon(top, outline=wht, width=t)
        d.line([(cx - a * 0.85, cy - a * 0.5), (cx - a * 0.85, cy + a * 0.5), (cx, cy + a), (cx + a * 0.85, cy + a * 0.5), (cx + a * 0.85, cy - a * 0.5)], fill=wht, width=t, joint="curve")
        d.line([(cx, cy), (cx, cy + a)], fill=wht, width=t)
    elif kind == "voi":
        d.rectangle([cx - a * 0.5, cy - a, cx + a * 0.5, cy - a * 0.35], outline=wht, width=t)
        d.polygon([(cx - a * 0.5, cy - a * 0.35), (cx + a * 0.5, cy - a * 0.35), (cx + a * 0.12, cy + a * 0.2), (cx - a * 0.12, cy + a * 0.2)], outline=wht, width=t)
        for k in (0.45, 0.75, 1.0):
            d.ellipse([cx - t, cy + a * k - t, cx + t, cy + a * k + t], fill=wht)
    elif kind == "chai":
        d.rounded_rectangle([cx - a * 0.45, cy - a * 0.35, cx + a * 0.45, cy + a], radius=t * 2, outline=wht, width=t)
        d.rectangle([cx - a * 0.2, cy - a, cx + a * 0.2, cy - a * 0.35], outline=wht, width=t)
    elif kind == "nhiet-do":
        d.rounded_rectangle([cx - a * 0.2, cy - a, cx + a * 0.2, cy + a * 0.3], radius=a * 0.2, outline=wht, width=t)
        d.ellipse([cx - a * 0.42, cy + a * 0.2, cx + a * 0.42, cy + a * 1.0], outline=wht, width=t)
    elif kind == "tui":
        d.polygon([(cx - a * 0.6, cy - a * 0.75), (cx + a * 0.6, cy - a * 0.75), (cx + a * 0.75, cy + a), (cx - a * 0.75, cy + a)], outline=wht, width=t)
        d.line([(cx - a * 0.6, cy - a * 0.45), (cx + a * 0.6, cy - a * 0.45)], fill=wht, width=t)
    else:
        raise SystemExit(f"Icon khong co: {kind}")


def wrap_fit(text_lines, weight, max_w, max_h, start, minimum, spacing=1.12):
    size = start
    while size >= minimum:
        f = font(weight, size)
        ws = [f.getbbox(t)[2] - f.getbbox(t)[0] for t in text_lines]
        total_h = size * spacing * len(text_lines)
        if max(ws) <= max_w and total_h <= max_h:
            return f, size
        size -= 1
    return font(weight, minimum), minimum


def build(args):
    big = Image.new("RGB", (W * S, H * S), (255, 255, 255))
    # nen trang co vung sang nhe giua anh
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([150, 120, 1100, 980], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    base = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), Image.new("RGB", (W, H), (244, 246, 249)), glow)
    big = base.resize((W * S, H * S))

    # ---------- dai xanh ----------
    left_pts = [(0, TOP_L), (DIAG_TOP_X, TOP_L), (DIAG_BOT_X, BOT), (0, BOT)]
    right_pts = [(DIAG_TOP_X + (DIAG_BOT_X - DIAG_TOP_X) * (TOP_R - TOP_L) / (BOT - TOP_L), TOP_R), (W, TOP_R), (W, BOT), (DIAG_BOT_X, BOT)]
    # bong mo phia tren dai xanh
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).polygon(left_pts + [], fill=90)
    ImageDraw.Draw(sh).polygon(right_pts, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(14)).resize((W * S, H * S))
    big = Image.composite(Image.new("RGB", big.size, (200, 210, 225)), big, sh.point(lambda v: v // 3))

    gr = gradient(W * S, H * S, BLUE_R1, BLUE_R2, True)
    big.paste(gr, (0, 0), poly_mask(right_pts))
    gl = gradient(W * S, H * S, BLUE_L1, BLUE_L2, False)
    big.paste(gl, (0, 0), poly_mask(left_pts))

    d = ImageDraw.Draw(big)
    # vien cyan: mep tren o ten may, duong cheo, mep tren dai thong so, mep duoi
    d.line([(0, TOP_L * S), (DIAG_TOP_X * S, TOP_L * S)], fill=CYAN, width=5 * S)
    d.line([(DIAG_TOP_X * S, TOP_L * S), (DIAG_BOT_X * S, BOT * S)], fill=CYAN, width=9 * S)
    d.line([(right_pts[0][0] * S, TOP_R * S), (W * S, TOP_R * S)], fill=CYAN_SOFT, width=3 * S)
    d.line([(DIAG_BOT_X * S, (BOT - 4) * S), (W * S, (BOT - 4) * S)], fill=CYAN, width=6 * S)

    # ---------- ten may ----------
    lines = [x.strip() for x in args.ten.split("|") if x.strip()]
    f, size = wrap_fit(lines, "black", 305, (BOT - TOP_L) - 46, 66, 34)
    lh = size * 1.12
    y0 = (TOP_L + BOT) / 2 - lh * len(lines) / 2 + lh / 2
    for i, t in enumerate(lines):
        d.text((42 * S, (y0 + i * lh) * S), t, font=font("black", size * S), fill=(255, 255, 255), anchor="lm")

    # ---------- 3 o thong so ----------
    x_start = DIAG_BOT_X + 30
    cell_w = (W - 20 - x_start) / 3
    cy = (TOP_R + BOT) / 2 + 2
    r = 33
    specs = []
    for spec in args.o[:3]:
        kind, txt = spec.split(":", 1)
        specs.append((kind, [x.strip() for x in txt.split("|") if x.strip()]))
    ts = min(wrap_fit(tl, "bold", cell_w - 2 * r - 44, 110, 28, 18, 1.18)[1] for _, tl in specs)
    tf = font("bold", ts)
    for i, (kind, tl) in enumerate(specs):
        cx0 = x_start + i * cell_w
        tw = max(tf.getbbox(t)[2] - tf.getbbox(t)[0] for t in tl)
        block = 2 * r + 14 + tw
        bx = cx0 + (cell_w - block) / 2
        draw_icon(d, kind.strip(), (bx + r) * S, cy * S, r * S, 4 * S)
        lh2 = ts * 1.18
        ty0 = cy - lh2 * len(tl) / 2 + lh2 / 2
        for j, t in enumerate(tl):
            d.text(((bx + 2 * r + 14) * S, (ty0 + j * lh2) * S), t, font=font("bold", ts * S), fill=(255, 255, 255), anchor="lm")
        if i > 0:
            d.line([(cx0 * S, (TOP_R + 34) * S), (cx0 * S, (BOT - 30) * S)], fill=(150, 185, 235), width=2 * S)

    img = big.resize((W, H), Image.LANCZOS).convert("RGBA")

    # ---------- may ----------
    may = trim(cut_background(Image.open(args.may)))
    box_w, box_h = 900, TOP_L - 40 - 120
    may = fit(may, box_w, box_h)
    mx = (W - may.width) // 2 + 40
    my = TOP_L - 40 - may.height
    # bong do mem duoi chan may
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse([mx + may.width * 0.08, my + may.height - 22, mx + may.width * 0.92, my + may.height + 22], fill=120)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.composite(Image.new("RGBA", (W, H), (120, 128, 140, 255)), img, shadow.point(lambda v: int(v * 0.55)))
    img.alpha_composite(may, (mx, my))

    # ---------- minh hoa goc phai ----------
    if args.minh_hoa:
        mh = trim(cut_background(Image.open(args.minh_hoa)))
        mh = fit(mh, 300, 230)
        img.alpha_composite(mh, (W - 40 - mh.width, 40))

    # ---------- logo ----------
    logo = Image.open(os.path.join(HERE, "mau-anh", "logo-duc-thanh-lon.png"))
    logo = trim(cut_background(logo))
    logo = fit(logo, 290, 230)
    img.alpha_composite(logo, (42, 40))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.convert("RGB").save(args.out, optimize=True)
    print("Da luu:", args.out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--may", required=True)
    p.add_argument("--ten", required=True)
    p.add_argument("--o", action="append", required=True)
    p.add_argument("--minh-hoa")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    if len(a.o) != 3:
        raise SystemExit("Can dung 3 --o")
    build(a)
