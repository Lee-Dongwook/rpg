"""전장 프롭 아트 - 보드, 헥사 타일, 적 유닛, UI 바, 전투 이펙트."""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFilter
from artlib import Canvas, mix, rgba, shade

SS = int(os.environ.get("ART_SS", 3))

SHELL_D = (118, 134, 162, 255)
SHELL = (226, 234, 246, 255)
SHELL_L = (255, 255, 255, 255)
TEAL_D = (8, 82, 106, 255)
TEAL = (32, 196, 208, 255)
TEAL_L = (176, 255, 250, 255)
PINK_D = (128, 12, 70, 255)
PINK = (255, 54, 140, 255)
PINK_L = (255, 168, 208, 255)
YEL_D = (168, 112, 8, 255)
YEL = (255, 214, 54, 255)
YEL_L = (255, 248, 176, 255)
SUIT_D = (14, 18, 32, 255)
SUIT = (36, 44, 68, 255)
SUIT_L = (78, 92, 128, 255)
EDGE = (8, 12, 24, 215)


def plate(c, pts, dark, light, r=8, ao=True, edge=True, ew=2.6):
    c.gradient_poly(pts, light, dark, smooth=False)
    c.edge_light(pts, shade(light, .5), shade(dark, -.3), r=r, strength=235, smooth=False)
    if ao:
        c.inner_shadow(pts, (3, 5, 14, 255), offset=(0, 12), r=13, strength=135, smooth=False)
    if edge:
        c.poly(pts, ink=EDGE, w=ew, smooth=False)


def hexagon(cx, cy, r, flat=False):
    off = 0 if flat else math.pi / 6
    return [(cx + r * math.cos(i * math.pi / 3 + off),
             cy + r * math.sin(i * math.pi / 3 + off)) for i in range(6)]


# ── 전장 바닥 ────────────────────────────────────────────
def board(size=1024):
    c = Canvas(size, size, ss=2, out=(size, size))
    s = size
    c.gradient_poly([(0, 0), (s, 0), (s, s), (0, s)], (86, 126, 158, 255), (22, 44, 76, 255),
                    smooth=False)
    # 손그림 느낌의 지면 페인팅 스트로크
    for i in range(70):
        a = i * 2.399
        rr = 40 + (i * 53) % 430
        cx, cy = s / 2 + math.cos(a) * rr, s / 2 + math.sin(a) * rr
        w = 60 + (i * 31) % 150
        col = (150, 200, 224, 30) if i % 3 == 0 else ((30, 58, 92, 46) if i % 3 == 1
                                                      else (70, 176, 190, 26))
        c.poly([(cx - w, cy), (cx, cy - w * .3), (cx + w, cy), (cx, cy + w * .3)],
               fill=col, smooth=False)
    # 헥사 그리드
    grid = c.layer()
    step = s / 6.4
    for row in range(-1, 9):
        for col in range(-1, 9):
            cx = col * step * .9 + (step * .45 if row % 2 else 0)
            cy = row * step * .78
            c.poly(hexagon(cx, cy, step * .5), ink=(176, 244, 250, 92), w=3.2,
                   smooth=False, target=grid)
            c.poly(hexagon(cx, cy, step * .5), ink=(12, 30, 52, 70), w=6,
                   smooth=False, target=grid)
    c.paste(grid.filter(ImageFilter.GaussianBlur(.6 * c.ss)))
    # 중앙 문양
    cx = cy = s / 2
    glow = c.layer()
    c.ellipse(cx, cy, s * .2, s * .2, fill=(120, 232, 240, 130), target=glow)
    c.paste(glow.filter(ImageFilter.GaussianBlur(34 * c.ss)))
    for rr, col, wd in ((s * .44, (196, 250, 252, 150), 6), (s * .40, (255, 214, 54, 130), 4),
                        (s * .23, (196, 250, 252, 170), 5)):
        c.ellipse(cx, cy, rr, rr, ink=col, w=wd)
    c.poly(hexagon(cx, cy, s * .16), ink=(226, 255, 255, 210), w=6, smooth=False)
    c.poly(hexagon(cx, cy, s * .11), ink=(255, 214, 54, 190), w=4, smooth=False)
    for i in range(6):
        a = i * math.pi / 3
        c.line([(cx + math.cos(a) * s * .17, cy + math.sin(a) * s * .17),
                (cx + math.cos(a) * s * .22, cy + math.sin(a) * s * .22)],
               (255, 214, 54, 200), 7, smooth=False)
    # 바깥 테두리
    m = s * .022
    c.poly([(m, m), (s - m, m), (s - m, s - m), (m, s - m)], ink=(226, 250, 255, 120), w=6,
           smooth=False)
    # 비네트
    vig = c.layer()
    vd = ImageDraw.Draw(vig)
    for i in range(46):
        t = i / 46
        vd.rectangle([i * 5 * c.ss, i * 5 * c.ss, (s - i * 5) * c.ss, (s - i * 5) * c.ss],
                     outline=(4, 10, 24, int(105 * (1 - t) ** 1.4)), width=int(6 * c.ss))
    c.paste(vig.filter(ImageFilter.GaussianBlur(7 * c.ss)))
    c.punch(1.2, 1.08)
    return c


def hex_tile(size=256):
    c = Canvas(size, size, ss=SS, out=(size, size))
    cx = cy = size / 2
    r = size * .46
    pts = hexagon(cx, cy, r)
    c.gradient_poly(pts, (60, 150, 176, 96), (14, 40, 66, 150), smooth=False)
    inner = hexagon(cx, cy, r * .84)
    c.poly(inner, ink=(150, 240, 246, 120), w=2.5, smooth=False)
    glow = c.layer()
    c.poly(pts, ink=(150, 246, 250, 235), w=5, smooth=False, target=glow)
    c.paste(glow.filter(ImageFilter.GaussianBlur(4 * c.ss)))
    c.poly(pts, ink=(196, 252, 255, 220), w=3, smooth=False)
    for i in range(6):
        a = i * math.pi / 3 + math.pi / 6
        c.line([(cx + math.cos(a) * r * .55, cy + math.sin(a) * r * .55),
                (cx + math.cos(a) * r * .78, cy + math.sin(a) * r * .78)],
               (255, 214, 54, 150), 3, smooth=False)
    return c


def hex_tile_active(size=256):
    c = hex_tile(size)
    cx = cy = size / 2
    r = size * .46
    glow = c.layer()
    c.poly(hexagon(cx, cy, r * .9), ink=(255, 214, 54, 235), w=7, smooth=False, target=glow)
    c.paste(glow.filter(ImageFilter.GaussianBlur(6 * c.ss)))
    c.poly(hexagon(cx, cy, r * .9), ink=(255, 240, 170, 230), w=3, smooth=False)
    return c


# ── 적 유닛 ──────────────────────────────────────────────
def target_unit():
    W, H = 640, 1024
    CX = W / 2
    c = Canvas(W, H, ss=SS, out=(W, H))
    V_D = (40, 16, 68, 255)
    V = (108, 54, 162, 255)
    V_L = (192, 148, 240, 255)
    V_SP = (216, 178, 255, 255)
    RED = (255, 62, 96, 255)
    RED_L = (255, 176, 190, 255)

    def mir(pts):
        return [(2 * CX - x, y) for x, y in pts]

    # 다리
    for side in (-1, 1):
        thigh = [(258, 612), (248, 686), (256, 748), (300, 760), (312, 700), (310, 606)]
        plate(c, thigh if side < 0 else mir(thigh), V_D, V, r=9)
        shin = [(258, 754), (250, 826), (258, 882), (300, 890), (312, 836), (308, 750)]
        plate(c, shin if side < 0 else mir(shin), V_D, V_L, r=8)
        foot = [(250, 876), (236, 918), (248, 954), (302, 960), (320, 922), (312, 872)]
        plate(c, foot if side < 0 else mir(foot), (16, 8, 30, 255), V, r=6)
    # 몸통
    torso = [(CX, 306), (250, 334), (228, 420), (238, 512), (266, 592),
             (CX, 626), (374, 592), (402, 512), (412, 420), (390, 334)]
    plate(c, torso, V_D, V_L, r=13)
    face_top = [(CX, 310), (254, 336), (268, 386), (CX, 406), (372, 386), (386, 336)]
    c.gradient_poly(face_top, V_SP, V, smooth=False)
    c.poly(face_top, ink=EDGE, w=2.2, smooth=False)
    core = [(CX, 416), (274, 470), (CX, 552), (366, 470)]
    c.glow(lambda l: c.poly(core, fill=RED_L, smooth=False, target=l), RED, 9,
           strength=1.0, passes=2)
    c.gradient_poly(core, RED_L, RED, smooth=False)
    c.poly(core, ink=EDGE, w=2.4, smooth=False)
    # 벨트
    plate(c, [(258, 588), (252, 626), (388, 626), (382, 588)], (18, 10, 34, 255), V_SP,
          r=5, ao=False)
    # 팔
    for side in (-1, 1):
        upper = [(238, 372), (206, 452), (212, 530), (262, 536), (270, 456), (280, 386)]
        plate(c, upper if side < 0 else mir(upper), (24, 12, 44, 255), V, r=8)
        fist = [(212, 520), (200, 566), (226, 592), (264, 580), (266, 534)]
        plate(c, fist if side < 0 else mir(fist), (16, 8, 30, 255), V_L, r=6, ao=False)
    # 어깨
    for side in (-1, 1):
        pa = [(288, 320), (222, 300), (168, 340), (160, 402), (206, 442), (272, 430), (300, 376)]
        plate(c, pa if side < 0 else mir(pa), V_D, V_L, r=11)
        top = [(288, 320), (224, 300), (176, 334), (216, 350), (274, 352), (298, 340)]
        c.gradient_poly(top if side < 0 else mir(top), V_SP, V, smooth=False)
        c.poly(top if side < 0 else mir(top), ink=EDGE, w=2, smooth=False)
        sp = [(222, 300), (192, 240), (176, 196), (204, 250), (214, 302)]
        plate(c, sp if side < 0 else mir(sp), (58, 22, 90, 255), V_SP, r=5, ao=False)
    # 머리
    head = [(CX, 158), (268, 186), (252, 250), (272, 302), (CX, 328), (368, 302), (388, 250), (372, 186)]
    plate(c, head, V_D, V_L, r=10)
    crest = [(CX, 160), (272, 188), (286, 228), (CX, 248), (354, 228), (368, 188)]
    c.gradient_poly(crest, V_SP, V, smooth=False)
    c.poly(crest, ink=EDGE, w=2.2, smooth=False)
    for side in (-1, 1):
        eye = [(282, 262), (312, 254), (316, 282), (284, 288)]
        pts = eye if side < 0 else mir(eye)
        c.glow(lambda l, p=pts: c.poly(p, fill=RED_L, smooth=False, target=l), RED, 6,
               strength=.95, passes=1)
        c.poly(pts, fill=RED, ink=EDGE, w=2, smooth=False)
        horn = [(284, 178), (256, 116), (242, 74), (272, 130), (296, 176)]
        plate(c, horn if side < 0 else mir(horn), (58, 22, 90, 255), V_SP, r=5, ao=False)
    c.global_light((255, 240, 240, 34), (10, 6, 26, 104))
    c.punch(1.24, 1.1)
    return c


# ── 이펙트 ───────────────────────────────────────────────
def slash(size=512):
    c = Canvas(size, size, ss=SS, out=(size, size))
    cx, cy = size * .5, size * .56
    outer, inner = size * .46, size * .3
    pts_o, pts_i = [], []
    for i in range(33):
        t = i / 32
        a = math.radians(-118 + 236 * t)
        taper = math.sin(math.pi * t) ** .55
        pts_o.append((cx + math.cos(a) * outer, cy + math.sin(a) * outer))
        pts_i.append((cx + math.cos(a) * (outer - (outer - inner) * taper),
                      cy + math.sin(a) * (outer - (outer - inner) * taper)))
    band = pts_o + pts_i[::-1]
    c.glow(lambda l: c.poly(band, fill=PINK_L, smooth=False, target=l), PINK, 11,
           strength=.75, passes=2)
    c.glow(lambda l: c.poly(band, fill=TEAL_L, smooth=False, target=l), TEAL, 5,
           strength=.9, passes=1)
    c.gradient_poly(band, (255, 255, 255, 255), TEAL_L, smooth=False)
    return c


def hit_spark(size=256):
    c = Canvas(size, size, ss=SS, out=(size, size))
    cx = cy = size / 2
    star = []
    for i in range(16):
        a = i * math.pi / 8
        r = size * (.46 if i % 2 == 0 else .13)
        star.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    c.glow(lambda l: c.poly(star, fill=PINK_L, smooth=False, target=l), PINK, 9,
           strength=.85, passes=2)
    c.gradient_poly(star, (255, 255, 255, 255), PINK_L, smooth=False)
    c.ellipse(cx, cy, size * .14, size * .14, fill=(255, 255, 255, 255))
    return c


def aura_ring(size=512):
    c = Canvas(size, size, ss=SS, out=(size, size))
    cx = cy = size / 2
    r = size * .44
    ring = c.layer()
    c.ellipse(cx, cy, r, r, ink=(150, 250, 250, 255), w=13, target=ring)
    c.paste(ring.filter(ImageFilter.GaussianBlur(9 * c.ss)))
    c.ellipse(cx, cy, r, r, ink=(210, 255, 254, 235), w=5)
    c.ellipse(cx, cy, r * .86, r * .86, ink=(150, 250, 250, 110), w=3)
    for i in range(12):
        a = i * math.tau / 12
        c.line([(cx + math.cos(a) * r * .88, cy + math.sin(a) * r * .88),
                (cx + math.cos(a) * r * .99, cy + math.sin(a) * r * .99)],
               (255, 214, 54, 190), 5, smooth=False)
    c.ellipse(cx, cy, r * .93, r * .93, fill=(80, 220, 226, 30))
    return c


def ground_shadow(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(size // 2, 0, -1):
        t = i / (size / 2)
        a = int(150 * (1 - t) ** 1.7)
        d.ellipse([size / 2 - i, size / 2 - i * .52, size / 2 + i, size / 2 + i * .52],
                  fill=(6, 10, 22, a))
    return img.filter(ImageFilter.GaussianBlur(6))


# ── 유닛 상태 바 (TFT UI) ────────────────────────────────
def unit_bar(w=512, h=192):
    c = Canvas(w, h, ss=SS, out=(w, h))
    # 별 티어 셰브런
    for i in range(3):
        x = 22 + i * 26
        chev = [(x, 16), (x + 16, 34), (x, 52), (x + 7, 34)]
        plate(c, chev, YEL_D, YEL_L, r=4, ao=False, ew=2)
    # 체력 바
    bar = [(102, 12), (496, 12), (496, 56), (102, 56)]
    plate(c, bar, (10, 14, 26, 255), (54, 66, 92, 255), r=5, ao=False, ew=3)
    fill = [(108, 18), (490, 18), (490, 50), (108, 50)]
    c.gradient_poly(fill, (146, 255, 128, 255), (36, 160, 62, 255), smooth=False)
    for i in range(1, 8):
        x = 108 + i * (382 / 8)
        c.line([(x, 18), (x, 50)], (8, 22, 16, 190), 3, smooth=False)
    c.spec([(112, 24), (486, 24)], (255, 255, 255, 120), 5, blur=2, smooth=False)
    # 마나 바
    mbar = [(102, 62), (496, 62), (496, 92), (102, 92)]
    plate(c, mbar, (10, 14, 26, 255), (54, 66, 92, 255), r=4, ao=False, ew=3)
    mfill = [(108, 67), (400, 67), (400, 87), (108, 87)]
    c.gradient_poly(mfill, (150, 232, 255, 255), (36, 122, 226, 255), smooth=False)
    # 아이템 슬롯
    for i in range(3):
        x = 106 + i * 74
        slot = [(x, 104), (x + 64, 104), (x + 64, 168), (x, 168)]
        plate(c, slot, (8, 12, 24, 255), (70, 96, 132, 255), r=5, ao=False, ew=3)
        inner = [(x + 8, 112), (x + 56, 112), (x + 56, 160), (x + 8, 160)]
        c.gradient_poly(inner, (34, 92, 138, 255), (12, 30, 58, 255), smooth=False)
        glyphs = [
            (TEAL, [(x + 32, 118), (x + 52, 136), (x + 32, 154), (x + 12, 136)]),
            (PINK, [(x + 14, 118), (x + 50, 118), (x + 50, 154), (x + 14, 154)]),
            (YEL, [(x + 32, 116), (x + 50, 152), (x + 14, 152)]),
        ]
        color, shape = glyphs[i]
        c.poly(shape, fill=color, ink=EDGE, w=2.4, smooth=False)
        c.spec([(x + 10, 116), (x + 54, 116)], (255, 255, 255, 90), 4, blur=2, smooth=False)
    return c


if __name__ == "__main__":
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out_dir, exist_ok=True)
    jobs = {
        "board_arena.png": lambda: board(),
        "hex_tile.png": lambda: hex_tile(),
        "hex_tile_active.png": lambda: hex_tile_active(),
        "unit_target.png": lambda: target_unit(),
        "slash_fx.png": lambda: slash(),
        "hit_spark.png": lambda: hit_spark(),
        "aura_ring.png": lambda: aura_ring(),
        "unit_bar.png": lambda: unit_bar(),
    }
    for name, fn in jobs.items():
        path = os.path.join(out_dir, name)
        fn().save(path)
        print(path)
    ground_shadow().save(os.path.join(out_dir, "ground_shadow.png"))
    print(os.path.join(out_dir, "ground_shadow.png"))
