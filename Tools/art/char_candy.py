"""'사탕맛' 유닛 전신 아트. TFT 인게임 유닛처럼 반실사 비율 + 금속 플레이트 아머."""
from __future__ import annotations

import math
import os
from PIL import ImageFilter
from artlib import Canvas, mix, shade

W, H = 768, 1152
CX = W / 2

# ── 팔레트 ────────────────────────────────────────────────
NAVY_D = (12, 16, 30, 255)
NAVY = (30, 38, 60, 255)
NAVY_L = (72, 88, 122, 255)
TEAL_D = (8, 52, 66, 255)
TEAL = (20, 176, 176, 255)
TEAL_L = (168, 246, 232, 255)
GOLD_D = (104, 58, 6, 255)
GOLD = (246, 178, 34, 255)
GOLD_L = (255, 240, 158, 255)
STEEL_D = (34, 42, 58, 255)
STEEL = (118, 138, 162, 255)
STEEL_L = (214, 228, 242, 255)
SKIN_D = (138, 92, 76, 255)
SKIN = (208, 158, 132, 255)
SKIN_L = (246, 214, 190, 255)
HAIR_D = (92, 76, 58, 255)
HAIR = (182, 160, 126, 255)
HAIR_L = (244, 232, 202, 255)
BLADE = (206, 244, 128, 255)
BLADE_C = (250, 255, 216, 255)
EDGE = (6, 10, 20, 205)


def mirror(pts, axis=CX):
    return [(2 * axis - x, y) for x, y in pts]


def plate(c, pts, dark, light, r=8, ao=True, edge=True, smooth=False):
    """각진 금속판: 면 그라디언트 + 베벨 + 접촉 그림자 + 또렷한 외곽선."""
    c.gradient_poly(pts, light, dark, smooth=smooth)
    c.edge_light(pts, shade(light, .5), shade(dark, -.3), r=r, strength=235, smooth=smooth)
    if ao:
        c.inner_shadow(pts, (3, 5, 14, 255), offset=(0, 12), r=13, strength=140, smooth=smooth)
    if edge:
        c.poly(pts, ink=EDGE, w=2.6, smooth=smooth)


def tube(c, path, dark, light, w0, w1=None):
    w1 = w0 * .84 if w1 is None else w1
    n = len(path) - 1
    left, right = [], []
    for i, (x, y) in enumerate(path):
        w = w0 + (w1 - w0) * (i / max(1, n))
        left.append((x - w / 2, y))
        right.append((x + w / 2, y))
    pts = left + right[::-1]
    c.gradient_poly(pts, light, dark, horizontal=True, smooth=False)
    c.edge_light(pts, shade(light, .3), shade(dark, -.2), r=6, strength=185, smooth=False)
    c.poly(pts, ink=EDGE, w=2.2, smooth=False)
    return pts


def build():
    c = Canvas(W, H, ss=int(os.environ.get("ART_SS", 3)), out=(1024, 1536))

    # ── 뒤쪽 망토 ────────────────────────────────────────
    cape = [(CX, 250), (334, 262), (296, 392), (272, 590), (258, 780), (252, 892),
            (298, 866), (334, 918), (CX, 886), (434, 918), (470, 866), (516, 892),
            (510, 780), (496, 590), (472, 392), (434, 262)]
    c.gradient_poly(cape, TEAL_D, (6, 20, 34, 255))
    c.edge_light(cape, TEAL, (4, 12, 22, 255), r=12, strength=155)
    for i in (-1, -.35, .35, 1):
        c.spec([(CX + i * 60, 312), (CX + i * 94, 570), (CX + i * 110, 830)],
               (10, 52, 68, 165), 9, blur=4)

    # ── 어깨 뒤 날개 블레이드 ────────────────────────────
    for side in (-1, 1):
        for wing in (
            [(292, 238), (248, 170), (200, 92), (226, 172), (230, 230), (266, 248)],
            [(270, 270), (216, 220), (170, 162), (208, 234), (220, 280)],
        ):
            pts = wing if side < 0 else mirror(wing)
            plate(c, pts, GOLD_D, GOLD_L, r=6, ao=False)
            c.spec([pts[1], pts[2]], (255, 250, 214, 150), 3, blur=2, smooth=False)

    # ── 다리 (약간 벌린 스탠스) ──────────────────────────
    for side in (-1, 1):
        hip = CX + side * 30
        knee = CX + side * 44
        ankle = CX + side * 54
        tube(c, [(hip, 528), (hip + side * 8, 664), (knee, 800)], NAVY_D, NAVY_L, 66, 50)
        tube(c, [(knee, 800), (knee + side * 6, 920), (ankle, 1040)], NAVY_D, NAVY, 48, 38)
        c.drop([(330, 540), (CX, 578), (438, 540), (434, 570), (CX, 606), (334, 570)],
               (0, 0, 0, 150), offset=(0, 14), blur=8)
        thigh = [(320, 526), (306, 600), (312, 676), (346, 700), (382, 674), (386, 596), (378, 522)]
        plate(c, thigh if side < 0 else mirror(thigh), TEAL_D, TEAL_L, r=9)
        kn = [(322, 744), (312, 790), (328, 828), (368, 830), (382, 786), (374, 742)]
        plate(c, kn if side < 0 else mirror(kn), GOLD_D, GOLD_L, r=6)
        greave = [(330, 838), (318, 906), (322, 972), (330, 1018), (372, 1020),
                  (382, 962), (382, 900), (376, 834)]
        plate(c, greave if side < 0 else mirror(greave), TEAL_D, TEAL, r=9)
        foot = [(330, 1010), (312, 1046), (314, 1086), (352, 1098), (386, 1082), (384, 1014)]
        plate(c, foot if side < 0 else mirror(foot), STEEL_D, STEEL, r=6)
        for k in range(3):
            claw = [(320 + k * 22, 1078), (314 + k * 22, 1100), (338 + k * 22, 1094)]
            c.poly(claw if side < 0 else mirror(claw), fill=GOLD, ink=EDGE, w=2, smooth=False)

    # ── 골반 / 파울드 ────────────────────────────────────
    hips = [(336, 430), (326, 486), (CX, 522), (442, 486), (432, 430)]
    c.gradient_poly(hips, NAVY_L, NAVY_D)
    fauld = [(326, 460), (306, 524), (326, 566), (CX, 586), (442, 566), (462, 524), (442, 460)]
    plate(c, fauld, TEAL_D, TEAL_L, r=9)
    c.drop([(334, 398), (CX, 424), (434, 398), (430, 430), (CX, 452), (338, 430)],
           (0, 0, 0, 140), offset=(0, 14), blur=8)
    belt = [(330, 440), (326, 474), (442, 474), (438, 440)]
    plate(c, belt, GOLD_D, GOLD_L, r=5, ao=False)

    # ── 몸통 ─────────────────────────────────────────────
    torso = [(CX, 226), (342, 240), (314, 296), (310, 360), (326, 414),
             (CX, 440), (442, 414), (458, 360), (454, 296), (426, 240)]
    c.gradient_poly(torso, NAVY_L, NAVY_D)
    c.edge_light(torso, STEEL_L, NAVY_D, r=10, strength=165)
    breast = [(CX, 244), (350, 262), (334, 316), (350, 378), (CX, 402),
              (418, 378), (434, 316), (418, 262)]
    plate(c, breast, TEAL_D, TEAL_L, r=10)
    crest = [(CX, 260), (362, 290), (358, 342), (CX, 370), (410, 342), (406, 290)]
    plate(c, crest, GOLD_D, GOLD_L, r=6, ao=False)
    c.ellipse(CX, 318, 17, 21, fill=TEAL_D)
    c.ellipse(CX, 318, 12, 15, fill=TEAL_L)
    c.ellipse(CX - 3, 311, 4, 5, fill=(255, 255, 255, 225))
    c.spec([(354, 268), (342, 320), (354, 374)], (214, 250, 246, 120), 7, blur=3)

    # ── 팔 (오른팔은 검, 왼팔은 자연스럽게 내림) ──────────
    # 왼팔 (관객 왼쪽)
    tube(c, [(310, 262), (288, 336), (292, 404)], NAVY_D, NAVY, 42, 36)
    tube(c, [(292, 404), (300, 460), (316, 508)], NAVY_D, NAVY_L, 34, 28)
    plate(c, [(276, 396), (268, 442), (292, 470), (318, 456), (318, 412), (304, 388)],
          GOLD_D, GOLD_L, r=6)
    plate(c, [(300, 496), (292, 528), (312, 550), (338, 540), (340, 508), (326, 490)],
          STEEL_D, STEEL_L, r=5, ao=False)
    # 오른팔
    tube(c, [(458, 262), (482, 338), (492, 408)], NAVY_D, NAVY, 42, 36)
    tube(c, [(492, 408), (506, 464), (516, 516)], NAVY_D, NAVY_L, 34, 28)
    plate(c, [(472, 398), (466, 444), (490, 472), (516, 458), (518, 414), (502, 390)],
          GOLD_D, GOLD_L, r=6)

    # 몸통에 드리우는 어깨 그림자
    for side in (-1, 1):
        sh = [(348, 236), (300, 250), (306, 320), (352, 336)]
        c.drop(sh if side < 0 else mirror(sh), (0, 0, 0, 150), offset=(side * 4, 16), blur=9)

    # ── 어깨 갑옷 ────────────────────────────────────────
    for side in (-1, 1):
        pauld = [(344, 234), (298, 220), (250, 244), (234, 292), (260, 334),
                 (314, 340), (348, 298)]
        pts = pauld if side < 0 else mirror(pauld)
        plate(c, pts, TEAL_D, TEAL_L, r=11)
        # 위에서 내려다본 상단면 (카메라가 위에서 비스듬히 보는 각도)
        top = [(300, 222), (258, 244), (248, 264), (298, 246), (342, 240), (346, 228)]
        c.gradient_poly(top if side < 0 else mirror(top), (214, 255, 248, 210), (44, 158, 164, 40))
        rim = [(240, 302), (264, 340), (316, 344), (344, 302), (336, 288),
               (310, 324), (266, 320), (248, 288)]
        c.poly(rim if side < 0 else mirror(rim), fill=GOLD, ink=EDGE, w=2.2, smooth=False)
        for rv in ((266, 262), (256, 296), (272, 326), (312, 332)):
            rp = rv if side < 0 else (2 * CX - rv[0], rv[1])
            c.ellipse(rp[0], rp[1], 5, 5, fill=GOLD_D)
            c.ellipse(rp[0] - 1, rp[1] - 1, 3.4, 3.4, fill=GOLD_L)
        spike = [(298, 220), (272, 180), (258, 148), (278, 188), (284, 224)]
        plate(c, spike if side < 0 else mirror(spike), GOLD_D, GOLD_L, r=5, ao=False)

    # ── 대검 (오른손, 아래로 비스듬히) ───────────────────
    hx, hy = 520, 524
    tx, ty = 604, 1046
    c.drop([(hx - 16, hy), (hx + 16, hy), (tx + 8, ty), (tx - 8, ty)],
           (0, 0, 0, 115), offset=(20, 12), blur=8, smooth=False)
    blade = [(hx - 20, hy - 44), (tx - 13, ty - 120), (tx + 1, ty),
             (tx + 15, ty - 120), (hx + 12, hy - 44)]
    c.glow(lambda l: c.poly(blade, fill=BLADE, smooth=False, target=l), (168, 240, 96, 255), 6,
           strength=.9, passes=2)
    c.gradient_poly(blade, BLADE_C, (96, 138, 62, 255), smooth=False)
    c.edge_light(blade, (255, 255, 250, 255), (74, 106, 46, 255), r=4, strength=235, smooth=False)
    c.spec([(hx - 4, hy - 30), (tx - 7, ty - 60)], (255, 255, 244, 210), 5, blur=2, smooth=False)
    guard = [(468, 462), (452, 490), (492, 502), (524, 508), (560, 500), (588, 484), (570, 458),
             (536, 478), (504, 478), (492, 470)]
    plate(c, guard, GOLD_D, GOLD_L, r=6, ao=False)
    for side in (-1, 1):
        wing = [(482, 466), (448, 440), (426, 410), (456, 444), (472, 472)]
        pts = wing if side < 0 else mirror(wing, axis=hx)
        plate(c, pts, GOLD_D, GOLD_L, r=4, ao=False)
    plate(c, [(498, 486), (490, 534), (516, 560), (548, 548), (550, 500), (532, 480)],
          STEEL_D, STEEL_L, r=5, ao=False)
    for i in range(3):
        fy = 500 + i * 18
        plate(c, [(500, fy), (496, fy + 13), (542, fy + 16), (546, fy + 2)],
              STEEL_D, STEEL_L, r=3, ao=False)

    # ── 머리 ─────────────────────────────────────────────
    back = [(CX, 62), (338, 80), (316, 142), (320, 204), (342, 232),
            (CX, 242), (426, 232), (448, 204), (452, 142), (430, 80)]
    c.gradient_poly(back, HAIR, HAIR_D)
    neck = [(364, 178), (362, 230), (406, 230), (404, 178)]
    c.gradient_poly(neck, SKIN, SKIN_D)
    c.inner_shadow(neck, (48, 24, 18, 255), offset=(0, -18), r=12, strength=205)
    face = [(CX, 78), (352, 88), (338, 126), (344, 162), (362, 192),
            (CX, 206), (406, 192), (424, 162), (430, 126), (416, 88)]
    c.gradient_poly(face, SKIN_L, SKIN)
    c.edge_light(face, shade(SKIN_L, .28), SKIN_D, r=7, strength=130)
    for side in (-1, 1):
        ex = CX + side * 19
        c.ellipse(ex, 136, 11, 6, fill=(50, 36, 32, 240), rot=side * .12)
        c.ellipse(ex, 135, 4, 4, fill=(132, 200, 194, 255))
        c.ellipse(ex - 1, 133, 1.6, 1.6, fill=(255, 255, 255, 235))
        c.line([(ex - 12, 122), (ex, 118), (ex + 11, 122)], (88, 68, 54, 200), 3)
        c.line([(ex - 11, 130), (ex, 127), (ex + 10, 131)], (40, 30, 26, 195), 2.4)
    c.line([(CX + 1, 142), (CX + 3, 158), (CX - 5, 161)], shade(SKIN_D, .05), 2.4)
    c.line([(376, 176), (CX, 180), (392, 176)], (124, 70, 62, 195), 3)
    c.inner_shadow(face, (74, 40, 32, 255), offset=(0, 18), r=13, strength=118)
    bangs = [(CX, 62), (340, 76), (326, 114), (334, 144), (346, 114),
             (360, 142), (376, 110), (394, 140), (412, 110), (426, 142),
             (436, 114), (442, 144), (446, 112), (428, 76)]
    c.gradient_poly(bangs, HAIR_L, HAIR)
    c.edge_light(bangs, (255, 252, 240, 255), HAIR_D, r=6, strength=170)
    crown = [(CX, 46), (340, 60), (322, 94), (330, 116), (354, 92),
             (CX, 82), (414, 92), (438, 116), (446, 94), (428, 60)]
    plate(c, crown, TEAL_D, TEAL_L, r=6, ao=False)
    band = [(328, 94), (332, 114), (436, 114), (440, 94)]
    plate(c, band, GOLD_D, GOLD_L, r=4, ao=False)
    for side in (-1, 1):
        horn = [(334, 64), (306, 22), (282, -6), (312, 36), (322, 74)]
        plate(c, horn if side < 0 else mirror(horn), GOLD_D, GOLD_L, r=4, ao=False)
        ear = [(330, 106), (316, 90), (310, 116), (322, 132)]
        plate(c, ear if side < 0 else mirror(ear), TEAL_D, TEAL_L, r=3, ao=False)

    # ── 전체 광원 / 질감 ─────────────────────────────────
    c.global_light((255, 248, 232, 34), (6, 10, 26, 86))
    rim = c.layer()
    c.line([(330, 86), (310, 196), (292, 268)], (160, 246, 244, 155), 5, target=rim)
    c.line([(440, 90), (464, 206), (474, 280)], (160, 246, 244, 135), 4, target=rim)
    c.line([(322, 852), (316, 984)], (160, 246, 244, 110), 4, target=rim)
    c.paste(rim.filter(ImageFilter.GaussianBlur(2.2 * c.ss)))
    c.punch(1.34, 1.12)
    c.grain(2)
    return c


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "candy_fiora.png"
    print(build().save(out))
