"""사탕맛 전장 아트를 코드로 그리기 위한 공용 드로잉 헬퍼."""
from __future__ import annotations

import math
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

INK = (16, 10, 34, 255)


def rgba(c, a=255):
    if len(c) == 4:
        return c
    return (c[0], c[1], c[2], a)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def shade(c, t):
    """t<0 어둡게, t>0 밝게."""
    if t < 0:
        return mix(c[:3], (12, 8, 28), -t) + (c[3] if len(c) > 3 else 255,)
    return mix(c[:3], (255, 250, 245), t) + (c[3] if len(c) > 3 else 255,)


def catmull(points, closed=True, samples=16, alpha=0.5):
    """구심 Catmull-Rom 스플라인. alpha=0.5라 코너에서 튀는 오버슈트가 없습니다."""
    pts = list(points)
    n = len(pts)
    if n < 3:
        return pts

    def knot(t, a, b):
        d = math.dist(a, b)
        return t + (d ** alpha if d > 1e-6 else 1e-6)

    out = []
    rng = range(n) if closed else range(-1, n - 2)
    for i in rng:
        if closed:
            p0, p1, p2, p3 = (pts[(i - 1) % n], pts[i % n], pts[(i + 1) % n], pts[(i + 2) % n])
        else:
            j = i + 1
            p0 = pts[max(j - 1, 0)]
            p1 = pts[j] if j < n else pts[-1]
            p2 = pts[min(j + 1, n - 1)]
            p3 = pts[min(j + 2, n - 1)]
        t0 = 0.0
        t1 = knot(t0, p0, p1)
        t2 = knot(t1, p1, p2)
        t3 = knot(t2, p2, p3)
        for s_i in range(samples):
            t = t1 + (t2 - t1) * (s_i / samples)
            a1 = _lerp(p0, p1, (t1 - t) / (t1 - t0), (t - t0) / (t1 - t0))
            a2 = _lerp(p1, p2, (t2 - t) / (t2 - t1), (t - t1) / (t2 - t1))
            a3 = _lerp(p2, p3, (t3 - t) / (t3 - t2), (t - t2) / (t3 - t2))
            b1 = _lerp(a1, a2, (t2 - t) / (t2 - t0), (t - t0) / (t2 - t0))
            b2 = _lerp(a2, a3, (t3 - t) / (t3 - t1), (t - t1) / (t3 - t1))
            out.append(_lerp(b1, b2, (t2 - t) / (t2 - t1), (t - t1) / (t2 - t1)))
    if not closed:
        out.append(pts[-1])
    return out


def _lerp(a, b, wa, wb):
    return (a[0] * wa + b[0] * wb, a[1] * wa + b[1] * wb)


class Canvas:
    """디자인 좌표계에서 그리고, 슈퍼샘플링 후 최종 해상도로 축소."""

    def __init__(self, w, h, ss=3, out=None):
        self.w, self.h, self.ss = w, h, ss
        self.out = out or (w, h)
        self.img = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))

    # ── 내부 ──────────────────────────────────────────────
    def _s(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))

    def paste(self, layer):
        self.img = Image.alpha_composite(self.img, layer)

    # ── 도형 ──────────────────────────────────────────────
    def poly(self, pts, fill=None, ink=None, w=0, smooth=True, closed=True, target=None):
        p = catmull(pts, closed=closed) if smooth and len(pts) > 2 else list(pts)
        img = target if target is not None else self.img
        d = ImageDraw.Draw(img)
        sp = self._s(p)
        if fill:
            d.polygon(sp, fill=rgba(fill))
        if ink and w:
            path = sp + [sp[0]] if closed else sp
            d.line(path, fill=rgba(ink), width=max(1, int(w * self.ss)), joint="curve")
            r = max(1, int(w * self.ss)) / 2
            for x, y in path:
                d.ellipse([x - r, y - r, x + r, y + r], fill=rgba(ink))
        return p

    def gradient_poly(self, pts, top, bottom, ink=None, w=0, smooth=True, horizontal=False):
        """세로(또는 가로) 그라디언트로 채운 폴리곤."""
        p = catmull(pts) if smooth and len(pts) > 2 else list(pts)
        sp = self._s(p)
        xs = [q[0] for q in sp]
        ys = [q[1] for q in sp]
        x0, x1 = int(min(xs)) - 2, int(max(xs)) + 2
        y0, y1 = int(min(ys)) - 2, int(max(ys)) + 2
        bw, bh = max(1, x1 - x0), max(1, y1 - y0)
        grad = Image.new("RGBA", (bw, bh))
        gd = ImageDraw.Draw(grad)
        steps = bw if horizontal else bh
        for i in range(steps):
            c = mix(rgba(top), rgba(bottom), i / max(1, steps - 1))
            if horizontal:
                gd.line([(i, 0), (i, bh)], fill=c)
            else:
                gd.line([(0, i), (bw, i)], fill=c)
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in sp], fill=255)
        layer = self.layer()
        layer.paste(grad, (x0, y0), mask)
        self.paste(layer)
        if ink and w:
            self.poly(p, ink=ink, w=w, smooth=False)
        return p

    def ellipse(self, cx, cy, rx, ry, fill=None, ink=None, w=0, rot=0.0, target=None):
        pts = []
        for i in range(64):
            a = i / 64 * math.tau
            x, y = rx * math.cos(a), ry * math.sin(a)
            ca, sa = math.cos(rot), math.sin(rot)
            pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
        return self.poly(pts, fill=fill, ink=ink, w=w, smooth=False, target=target)

    def line(self, pts, color, w, smooth=True, target=None):
        p = catmull(pts, closed=False) if smooth and len(pts) > 2 else list(pts)
        img = target if target is not None else self.img
        ImageDraw.Draw(img).line(self._s(p), fill=rgba(color), width=max(1, int(w * self.ss)), joint="curve")
        return p

    def glow(self, draw_fn, color, radius, strength=1.0, passes=2):
        """draw_fn(layer)로 그린 형태를 블러해 발광 레이어로 합성."""
        for i in range(passes):
            layer = self.layer()
            draw_fn(layer)
            r = radius * self.ss * (i + 1)
            layer = layer.filter(ImageFilter.GaussianBlur(r))
            if strength != 1.0 or True:
                a = layer.split()[3].point(lambda v: min(255, int(v * strength)))
                layer.putalpha(a)
            tinted = Image.new("RGBA", layer.size, rgba(color)[:3] + (0,))
            tinted.putalpha(layer.split()[3])
            self.paste(tinted)

    def sparkles(self, spots, color=(255, 255, 255, 255)):
        layer = self.layer()
        d = ImageDraw.Draw(layer)
        for cx, cy, r in spots:
            s = self.ss
            d.polygon([(cx * s, (cy - r) * s), ((cx + r * .28) * s, cy * s),
                       ((cx + r) * s, cy * s), ((cx + r * .28) * s, (cy + r * .22) * s),
                       (cx * s, (cy + r) * s), ((cx - r * .28) * s, (cy + r * .22) * s),
                       ((cx - r) * s, cy * s), ((cx - r * .28) * s, cy * s)], fill=rgba(color))
        blur = layer.filter(ImageFilter.GaussianBlur(2.2 * self.ss))
        self.paste(blur)
        self.paste(layer)

    # ── 3D 렌더 톤 헬퍼 ───────────────────────────────────
    def mask_of(self, pts, smooth=True):
        p = catmull(pts) if smooth and len(pts) > 2 else list(pts)
        m = Image.new("L", self.img.size, 0)
        ImageDraw.Draw(m).polygon(self._s(p), fill=255)
        return m

    def clip(self, layer, mask):
        a = ImageChops.multiply(layer.split()[3], mask)
        layer.putalpha(a)
        return layer

    def edge_light(self, pts, light, dark, r=9, strength=210, smooth=True):
        """가장자리에 위=하이라이트 / 아래=음영을 넣어 금속 플레이트처럼 보이게 합니다."""
        mask = self.mask_of(pts, smooth)
        blurred = mask.filter(ImageFilter.GaussianBlur(r * self.ss * .45))
        inner = blurred.point(lambda v: 255 if v > 190 else 0)
        band = ImageChops.subtract(mask, inner).filter(
            ImageFilter.GaussianBlur(max(1.0, r * self.ss * .07)))
        bbox = mask.getbbox()
        if bbox is None:
            return
        y0, y1 = bbox[1], bbox[3]
        grad = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        span = max(1, y1 - y0)
        for y in range(y0, y1):
            t = (y - y0) / span
            gd.line([(bbox[0], y), (bbox[2], y)], fill=mix(rgba(light), rgba(dark), t ** .8))
        grad.putalpha(band.point(lambda v: int(v * strength / 255)))
        self.paste(self.clip(grad, mask))

    def inner_shadow(self, pts, color, offset=(0, 14), r=14, strength=150, smooth=True):
        """플레이트 아래쪽에 드리우는 접촉 그림자(AO)."""
        mask = self.mask_of(pts, smooth)
        shifted = Image.new("L", self.img.size, 0)
        shifted.paste(mask, (int(offset[0] * self.ss), int(offset[1] * self.ss)))
        band = ImageChops.subtract(mask, shifted).filter(
            ImageFilter.GaussianBlur(r * self.ss * .3))
        layer = Image.new("RGBA", self.img.size, rgba(color)[:3] + (0,))
        layer.putalpha(band.point(lambda v: int(v * strength / 255)))
        self.paste(self.clip(layer, mask))

    def spec(self, pts, color, w, blur=3, smooth=True):
        """블러 처리된 하이라이트 스트로크."""
        layer = self.layer()
        self.line(pts, color, w, smooth=smooth, target=layer)
        self.paste(layer.filter(ImageFilter.GaussianBlur(blur * self.ss)))

    def drop(self, pts, color=(0, 0, 0, 150), offset=(6, 10), blur=8, smooth=True):
        """오브젝트 뒤로 떨어지는 그림자."""
        p = catmull(pts) if smooth and len(pts) > 2 else list(pts)
        layer = self.layer()
        ImageDraw.Draw(layer).polygon(
            [(x * self.ss + offset[0] * self.ss, y * self.ss + offset[1] * self.ss) for x, y in p],
            fill=rgba(color))
        self.paste(layer.filter(ImageFilter.GaussianBlur(blur * self.ss)))

    def grain(self, amount=7, seed=3):
        import random
        random.seed(seed)
        w, h = self.img.size
        small = Image.new("L", (w // 6, h // 6))
        small.putdata([128 + random.randint(-amount * 4, amount * 4) for _ in range(small.size[0] * small.size[1])])
        noise = small.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.5))
        base = self.img.convert("RGBA")
        r, g, b, a = base.split()
        r = ImageChops.overlay(r, noise)
        g = ImageChops.overlay(g, noise)
        b = ImageChops.overlay(b, noise)
        self.img = Image.merge("RGBA", (r, g, b, a))

    def global_light(self, top=(255, 244, 226, 44), bottom=(10, 12, 30, 118)):
        """실루엣 전체에 위→아래 광원 그라디언트를 곱합니다."""
        alpha = self.img.split()[3]
        bbox = alpha.getbbox()
        if bbox is None:
            return
        grad = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        y0, y1 = bbox[1], bbox[3]
        span = max(1, y1 - y0)
        for y in range(y0, y1):
            gd.line([(0, y), (self.img.size[0], y)], fill=mix(rgba(top), rgba(bottom), (y - y0) / span))
        grad.putalpha(ImageChops.multiply(grad.split()[3], alpha))
        self.paste(grad)

    def punch(self, saturation=1.3, contrast=1.1):
        """알파를 유지한 채 채도/대비를 끌어올립니다."""
        alpha = self.img.split()[3]
        rgb = self.img.convert("RGB")
        rgb = ImageEnhance.Color(rgb).enhance(saturation)
        rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
        self.img = rgb.convert("RGBA")
        self.img.putalpha(alpha)

    # ── 출력 ──────────────────────────────────────────────
    def save(self, path):
        img = self.img.resize(self.out, Image.LANCZOS)
        img.save(path)
        return path
