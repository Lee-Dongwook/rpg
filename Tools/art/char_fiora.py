"""애니마 스쿼드 피오라 유닛 아트.

아트 디렉션:
  - LoL 인게임 3D 에셋 룩 (로우폴리 메시 + 핸드페인팅 디퓨즈에 라이팅을 구워넣음)
  - 아이소메트릭 3/4 탑다운 시점, 3성 유닛 아이들 전투 스탠스
  - 또렷한 실루엣 / 선명한 그라디언트 / 사실적 PBR 반사·노이즈 없음
"""
from __future__ import annotations

import os
from PIL import ImageFilter
from artlib import Canvas, shade

W, H = 768, 1152
CX = W / 2

# ── 애니마 스쿼드 팔레트 ──────────────────────────────────
SHELL_D = (118, 134, 162, 255)      # 흰 장갑 그림자면
SHELL = (226, 234, 246, 255)        # 흰 장갑 기본면
SHELL_L = (255, 255, 255, 255)      # 흰 장갑 상단면
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
SKIN_D = (152, 100, 82, 255)
SKIN = (214, 162, 136, 255)
SKIN_L = (250, 218, 194, 255)
HAIR_D = (14, 92, 126, 255)
HAIR = (60, 198, 230, 255)
HAIR_L = (176, 248, 255, 255)
EDGE = (8, 12, 24, 215)


def mirror(pts, axis=CX):
    return [(2 * axis - x, y) for x, y in pts]


def plate(c, pts, dark, light, r=8, ao=True, edge=True, ew=2.6):
    """로우폴리 장갑 한 면: 그라디언트 + 베벨 + 접촉 그림자 + 또렷한 외곽."""
    c.gradient_poly(pts, light, dark, smooth=False)
    c.edge_light(pts, shade(light, .5), shade(dark, -.3), r=r, strength=235, smooth=False)
    if ao:
        c.inner_shadow(pts, (3, 5, 14, 255), offset=(0, 12), r=13, strength=135, smooth=False)
    if edge:
        c.poly(pts, ink=EDGE, w=ew, smooth=False)


def face_up(c, pts, color_light, color_dark=None):
    """위를 향한 폴리곤 면 - 탑다운 시점에서 빛을 정면으로 받습니다."""
    c.gradient_poly(pts, color_light, color_dark or shade(color_light, -.22), smooth=False)
    c.poly(pts, ink=EDGE, w=2.0, smooth=False)


def tube(c, path, dark, light, w0, w1=None, edge=True):
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
    if edge:
        c.poly(pts, ink=EDGE, w=2.2, smooth=False)
    return pts


def build():
    c = Canvas(W, H, ss=int(os.environ.get("ART_SS", 3)), out=(1024, 1536))

    # ── 백팩 스러스터 & 기계 꼬리 (뒤) ───────────────────
    for side in (-1, 1):
        th = [(330, 336), (286, 318), (268, 372), (292, 428), (334, 414)]
        plate(c, th if side < 0 else mirror(th), SUIT_D, SUIT_L, r=7, ao=False)
        noz = [(288, 414), (276, 452), (300, 470), (324, 448), (320, 412)]
        pts = noz if side < 0 else mirror(noz)
        plate(c, pts, TEAL_D, TEAL, r=5, ao=False)
        c.glow(lambda l, p=pts: c.poly(p, fill=TEAL_L, smooth=False, target=l), TEAL, 6,
               strength=.7, passes=1)
    # 기계 꼬리 (엉덩이 뒤에서 아래로 흘러 다리 뒤로)
    spine = [(354, 596), (300, 640), (250, 700), (222, 776), (216, 846)]
    widths = [34, 30, 25, 19, 13]
    left, right = [], []
    for (x, y), wd in zip(spine, widths):
        left.append((x - wd, y + wd * .35))
        right.append((x + wd, y - wd * .35))
    tail = left + right[::-1]
    plate(c, tail, TEAL_D, SHELL, r=7, ao=False)
    for i in range(1, 4):
        x, y = spine[i]
        wd = widths[i]
        c.poly([(x - wd, y + wd * .35), (x + wd, y - wd * .35)],
               ink=EDGE, w=2.2, smooth=False, closed=False)
    tip = [(216, 838), (200, 890), (222, 918), (250, 900), (244, 850)]
    plate(c, tip, PINK_D, PINK_L, r=5, ao=False)
    c.glow(lambda l: c.poly(tip, fill=PINK_L, smooth=False, target=l), PINK, 5,
           strength=.6, passes=1)

    # ── 다리 (탑다운이라 짧게 압축) ──────────────────────
    for side, (hipx, kneex, footx, dy) in ((-1, (334, 316, 306, 0)), (1, (434, 456, 470, 26))):
        hipx, kneex, footx = (hipx, kneex, footx)
        tube(c, [(hipx, 610 + dy), (kneex, 720 + dy), (kneex, 782 + dy)], SUIT_D, SUIT_L, 74, 60)
        # 허벅지 장갑
        thigh = [(300, 596), (284, 664), (296, 726), (346, 742), (374, 700), (372, 606)]
        pts = thigh if side < 0 else mirror(thigh)
        pts = [(x, y + dy) for x, y in pts]
        plate(c, pts, SHELL_D, SHELL, r=9)
        face_up(c, [(x, y + dy) for x, y in
                    ([(302, 598), (286, 652), (350, 636), (372, 604)] if side < 0
                     else mirror([(302, 598), (286, 652), (350, 636), (372, 604)]))],
                SHELL_L, SHELL)
        acc = [(292, 668), (298, 706), (344, 716), (348, 676)]
        c.poly([(x, y + dy) for x, y in (acc if side < 0 else mirror(acc))],
               fill=PINK, ink=EDGE, w=2.2, smooth=False)
        # 무릎
        kn = [(300, 740), (290, 784), (312, 812), (356, 806), (368, 762), (356, 734)]
        plate(c, [(x, y + dy) for x, y in (kn if side < 0 else mirror(kn))],
              YEL_D, YEL_L, r=6)
        # 정강이
        gr = [(302, 806), (292, 866), (300, 918), (352, 926), (368, 878), (362, 802)]
        plate(c, [(x, y + dy) for x, y in (gr if side < 0 else mirror(gr))],
              SHELL_D, SHELL, r=8)
        c.poly([(x, y + dy) for x, y in
                ([(306, 828), (302, 900), (322, 904), (324, 830)] if side < 0
                 else mirror([(306, 828), (302, 900), (322, 904), (324, 830)]))],
               fill=TEAL, ink=EDGE, w=2.0, smooth=False)
        # 발 (동물 발 모티프)
        foot = [(296, 916), (280, 962), (292, 1004), (352, 1010), (378, 968), (368, 912)]
        pts = [(x, y + dy) for x, y in (foot if side < 0 else mirror(foot))]
        plate(c, pts, SHELL_D, SHELL, r=7)
        pad = [(302, 966), (296, 992), (330, 1002), (356, 988), (352, 962)]
        c.poly([(x, y + dy) for x, y in (pad if side < 0 else mirror(pad))],
               fill=PINK, ink=EDGE, w=2.0, smooth=False)
        for k in range(3):
            toe = [(300 + k * 26, 936), (292 + k * 26, 958), (318 + k * 26, 956)]
            c.poly([(x, y + dy) for x, y in (toe if side < 0 else mirror(toe))],
                   fill=YEL, ink=EDGE, w=1.8, smooth=False)

    # ── 골반 / 스커트 아머 ───────────────────────────────
    c.drop([(330, 560), (CX, 596), (438, 560), (434, 596), (CX, 636), (334, 596)],
           (0, 0, 0, 150), offset=(0, 14), blur=8)
    hips = [(334, 500), (322, 566), (CX, 600), (446, 566), (434, 500)]
    c.gradient_poly(hips, SUIT_L, SUIT_D, smooth=False)
    for side in (-1, 1):
        sk = [(330, 512), (300, 566), (316, 620), (376, 634), (392, 566), (386, 508)]
        plate(c, sk if side < 0 else mirror(sk), SHELL_D, SHELL, r=9)
        top = [(332, 514), (304, 558), (372, 552), (386, 510)]
        face_up(c, top if side < 0 else mirror(top), SHELL_L, SHELL)
        st = [(310, 574), (318, 614), (368, 622), (376, 578)]
        c.poly(st if side < 0 else mirror(st), fill=TEAL, ink=EDGE, w=2.2, smooth=False)
    belt = [(330, 486), (326, 520), (442, 520), (438, 486)]
    plate(c, belt, YEL_D, YEL_L, r=5, ao=False)
    c.ellipse(CX, 504, 20, 16, fill=PINK_D)
    c.ellipse(CX, 504, 13, 10, fill=PINK_L)

    # ── 몸통 ─────────────────────────────────────────────
    torso = [(CX, 302), (334, 320), (312, 380), (316, 448), (334, 496),
             (CX, 516), (434, 496), (452, 448), (456, 380), (434, 320)]
    c.gradient_poly(torso, SUIT_L, SUIT_D, smooth=False)
    c.edge_light(torso, (168, 192, 226, 255), SUIT_D, r=10, strength=170, smooth=False)
    chest = [(CX, 314), (346, 336), (330, 396), (350, 460), (CX, 484),
             (418, 460), (438, 396), (422, 336)]
    plate(c, chest, SHELL_D, SHELL, r=11)
    face_up(c, [(CX, 316), (348, 338), (340, 376), (CX, 396), (428, 376), (420, 338)],
            SHELL_L, SHELL)
    # 가슴 코어
    core = [(CX, 396), (356, 424), (CX, 470), (412, 424)]
    c.glow(lambda l: c.poly(core, fill=TEAL_L, smooth=False, target=l), TEAL, 8,
           strength=1.0, passes=2)
    c.gradient_poly(core, TEAL_L, TEAL, smooth=False)
    c.poly(core, ink=EDGE, w=2.2, smooth=False)
    c.ellipse(CX, 430, 14, 16, fill=(255, 255, 255, 245))
    c.glow(lambda l: c.ellipse(CX, 430, 14, 16, fill=(255, 255, 255, 255), target=l),
           (210, 255, 255, 255), 6, strength=.8, passes=1)
    for side in (-1, 1):
        stripe = [(352, 340), (338, 400), (352, 458), (366, 452), (354, 400), (366, 344)]
        c.poly(stripe if side < 0 else mirror(stripe), fill=PINK, ink=EDGE, w=2.0, smooth=False)

    # ── 팔 ───────────────────────────────────────────────
    # 왼팔: 방어 자세로 앞에 세움
    tube(c, [(322, 350), (272, 412), (262, 468)], SUIT_D, SUIT_L, 52, 44)
    tube(c, [(262, 468), (288, 512), (326, 540)], SUIT_D, SUIT, 42, 36)
    plate(c, [(240, 452), (232, 500), (262, 528), (296, 512), (296, 462), (276, 438)],
          SHELL_D, SHELL, r=7)
    c.poly([(240, 470), (238, 500), (266, 516), (272, 484)], fill=TEAL, ink=EDGE, w=2.0, smooth=False)
    plate(c, [(300, 516), (292, 556), (322, 578), (356, 566), (356, 526), (336, 508)],
          SHELL_D, SHELL_L, r=6, ao=False)
    # 오른팔: 레이피어를 앞아래로 겨눔
    tube(c, [(446, 348), (508, 400), (546, 442)], SUIT_D, SUIT_L, 52, 44)
    tube(c, [(546, 442), (580, 468), (610, 492)], SUIT_D, SUIT, 36, 30)
    plate(c, [(518, 416), (510, 452), (540, 478), (568, 462), (568, 424), (548, 404)],
          SHELL_D, SHELL, r=6)
    c.poly([(520, 430), (518, 454), (542, 468), (548, 440)], fill=PINK, ink=EDGE, w=2.0, smooth=False)

    # ── 어깨 장갑 (탑다운이라 윗면이 크게 보임) ───────────
    for side in (-1, 1):
        c.drop([(348, 316), (296, 330), (300, 400), (352, 414)],
               (0, 0, 0, 150), offset=(side * 4, 16), blur=9)
        pauld = [(350, 306), (296, 288), (240, 314), (222, 366), (252, 412),
                 (312, 420), (352, 380)]
        plate(c, pauld if side < 0 else mirror(pauld), SHELL_D, SHELL, r=12)
        top = [(350, 306), (296, 288), (244, 312), (272, 336), (330, 340), (352, 330)]
        face_up(c, top if side < 0 else mirror(top), SHELL_L, SHELL)
        band = [(230, 372), (254, 414), (312, 422), (350, 384), (340, 366),
                (306, 402), (260, 396), (244, 358)]
        c.poly(band if side < 0 else mirror(band), fill=YEL, ink=EDGE, w=2.4, smooth=False)
        fin = [(292, 288), (268, 244), (250, 208), (272, 250), (280, 292)]
        plate(c, fin if side < 0 else mirror(fin), TEAL_D, TEAL_L, r=5, ao=False)
        for rv in ((262, 340), (250, 378), (284, 404)):
            rp = rv if side < 0 else (2 * CX - rv[0], rv[1])
            c.ellipse(rp[0], rp[1], 5.5, 5.5, fill=YEL_D)
            c.ellipse(rp[0] - 1, rp[1] - 1, 3.6, 3.6, fill=YEL_L)

    # ── SF 레이피어 ─────────────────────────────────────
    hx, hy = 624, 508
    tx, ty = 726, 852
    gu = [(576, 466), (558, 492), (600, 512), (650, 516), (688, 500), (670, 472),
          (632, 488), (598, 484)]
    plate(c, gu, YEL_D, YEL_L, r=5, ao=False)
    hilt = [(600, 484), (592, 524), (622, 552), (652, 538), (652, 496), (628, 476)]
    plate(c, hilt, SHELL_D, SHELL_L, r=5, ao=False)
    for i in range(3):
        fy = 494 + i * 17
        plate(c, [(600, fy), (596, fy + 12), (646, fy + 14), (650, fy + 2)],
              SHELL_D, SHELL_L, r=3, ao=False, ew=1.8)
    blade = [(hx - 14, hy + 4), (tx - 10, ty - 90), (tx, ty), (tx + 8, ty - 96), (hx + 12, hy - 4)]
    c.glow(lambda l: c.poly(blade, fill=TEAL_L, smooth=False, target=l), TEAL, 7,
           strength=.95, passes=2)
    c.glow(lambda l: c.poly(blade, fill=PINK_L, smooth=False, target=l), PINK, 13,
           strength=.45, passes=1)
    c.gradient_poly(blade, (245, 255, 255, 255), TEAL, smooth=False)
    c.edge_light(blade, (255, 255, 255, 255), TEAL_D, r=4, strength=230, smooth=False)
    c.spec([(hx - 2, hy + 12), (tx - 6, ty - 40)], (255, 255, 255, 225), 5, blur=2, smooth=False)

    # ── 머리 (위에서 내려다본 각도) ──────────────────────
    c.drop([(300, 250), (CX, 300), (470, 250), (462, 300), (CX, 344), (306, 300)],
           (0, 0, 0, 140), offset=(0, 12), blur=9)
    # 사이버네틱 애니멀 이어
    for side, (base, mid, tipp) in ((-1, ((316, 196), (272, 96), (296, 62))),
                                    (1, ((452, 190), (498, 88), (474, 54)))):
        ear = [base, mid, tipp, (tipp[0] + side * 34, tipp[1] + 26),
               (mid[0] + side * 30, mid[1] + 40), (base[0] + side * 26, base[1] + 18)]
        plate(c, ear, SHELL_D, SHELL_L, r=6, ao=False)
        inner = [(base[0] + side * 6, base[1] - 4), (mid[0] + side * 8, mid[1] + 18),
                 (tipp[0] + side * 14, tipp[1] + 24), (base[0] + side * 20, base[1] + 10)]
        c.poly(inner, fill=PINK, ink=EDGE, w=2.0, smooth=False)
        led = [(base[0] + side * 2, base[1] - 12), (mid[0] + side * 2, mid[1] + 6)]
        c.line(led, TEAL_L, 5, smooth=False)
        c.glow(lambda l, p=led: c.line(p, TEAL_L, 5, smooth=False, target=l), TEAL, 5,
               strength=.7, passes=1)
    # 뒷머리 볼륨
    hair_back = [(CX, 154), (306, 178), (286, 244), (300, 300), (348, 330),
                 (CX, 338), (420, 330), (468, 300), (482, 244), (462, 178)]
    c.gradient_poly(hair_back, HAIR, HAIR_D, smooth=False)
    c.poly(hair_back, ink=EDGE, w=2.4, smooth=False)
    # 얼굴
    face = [(CX - 6, 196), (326, 210), (314, 252), (328, 292), (358, 320),
            (CX - 4, 330), (412, 316), (434, 288), (444, 250), (430, 208)]
    c.gradient_poly(face, SKIN_L, SKIN, smooth=False)
    c.edge_light(face, shade(SKIN_L, .3), SKIN_D, r=7, strength=120, smooth=False)
    c.inner_shadow(face, (80, 40, 32, 255), offset=(0, -26), r=15, strength=150, smooth=False)
    for side in (-1, 1):
        ex = CX - 6 + side * 30
        eye = [(ex - 23, 272), (ex - 6, 258), (ex + 14, 260), (ex + 22, 272),
               (ex + 12, 292), (ex - 12, 292)]
        c.poly(eye, fill=(24, 20, 32, 255), smooth=False)
        c.poly([(ex - 16, 270), (ex - 4, 264), (ex + 13, 266), (ex + 15, 276),
                (ex + 8, 288), (ex - 9, 288)], fill=TEAL, smooth=False)
        c.glow(lambda l, e=eye: c.poly(e, fill=TEAL_L, smooth=False, target=l), TEAL, 4,
               strength=.55, passes=1)
        c.ellipse(ex - 5, 272, 5.5, 6, fill=(255, 255, 255, 245))
        c.line([(ex - 20, 246), (ex + 2, 240), (ex + 19, 248)], HAIR_D, 5, smooth=False)
    c.line([(366, 308), (CX - 4, 312), (394, 307)], (150, 80, 70, 200), 3.4, smooth=False)
    # 앞머리 (짧은 보브 + 노란 하이라이트)
    bangs = [(CX, 148), (328, 164), (302, 206), (314, 236), (334, 196),
             (354, 232), (374, 190), (396, 230), (418, 188), (438, 230),
             (452, 192), (466, 232), (478, 200), (448, 162)]
    c.gradient_poly(bangs, HAIR_L, HAIR, smooth=False)
    c.edge_light(bangs, (222, 255, 255, 255), HAIR_D, r=7, strength=180, smooth=False)
    c.poly(bangs, ink=EDGE, w=2.4, smooth=False)
    for a, b, wid in (((342, 160), (326, 220), 9), ((372, 152), (366, 212), 7),
                      ((404, 152), (410, 212), 7), ((436, 158), (450, 218), 9)):
        c.poly([(a[0] - wid * .5, a[1]), (b[0] - wid * .35, b[1]),
                (b[0] + wid * .35, b[1] - 6), (a[0] + wid * .5, a[1] - 4)],
               fill=YEL, ink=EDGE, w=1.6, smooth=False)
    # 헤드셋 바이저
    vis = [(438, 226), (430, 258), (452, 284), (474, 274), (472, 234)]
    plate(c, vis, SHELL_D, SHELL_L, r=4, ao=False)
    c.poly([(440, 240), (436, 262), (456, 272), (462, 248)], fill=TEAL, ink=EDGE, w=1.8, smooth=False)
    c.glow(lambda l: c.poly([(440, 240), (436, 262), (456, 272), (462, 248)], fill=TEAL_L,
                            smooth=False, target=l), TEAL, 5, strength=.6, passes=1)

    # ── 베이크된 조명 마감 ───────────────────────────────
    c.global_light((255, 250, 236, 46), (10, 16, 38, 96))
    rim = c.layer()
    c.line([(300, 200), (272, 330), (250, 430)], (150, 250, 250, 165), 6, target=rim)
    c.line([(470, 190), (500, 330), (520, 440)], (255, 130, 190, 140), 5, target=rim)
    c.line([(300, 830), (296, 960)], (150, 250, 250, 120), 5, target=rim)
    c.line([(468, 856), (474, 986)], (255, 130, 190, 110), 5, target=rim)
    c.paste(rim.filter(ImageFilter.GaussianBlur(2.4 * c.ss)))
    c.punch(1.28, 1.1)
    return c


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "unit_fiora.png"
    print(build().save(out))
