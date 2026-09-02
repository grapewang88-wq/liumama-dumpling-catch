#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「接馅料·包饺子」专属素材生成
--------------------------------------------------
现有素材库里只有整只饺子（600x480）和馅料艺术字，没有单个食材。
这里按同一套像素画风格生成 11 种下落食材 + 奖励金币 + 接馅料的饺子皮 + 若干特效。

做法：高倍超采样画矢量形状 -> 降到 40x40 像素网格 -> 描边 -> 整数放大 4 倍
这样出来的是真·像素画（每个像素是 4x4 的方块），和饺子素材放一起不违和。

输出：assets/items/*.png (160x160)  assets/skin.png  assets/skin-shadow.png
"""
import os, math
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
ITEMS = os.path.join(OUT, "items")
os.makedirs(ITEMS, exist_ok=True)

GRID = 40      # 像素画网格
SS = 8         # 超采样倍率
PX = 4         # 最终每个像素放大成 4x4
SIZE = GRID * SS
OUTLINE = (58, 33, 22, 255)   # 与饺子素材同款深棕描边


def canvas():
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def poly(d, pts, fill):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)


def ell(d, x0, y0, x1, y1, fill):
    d.ellipse([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=fill)


def rrect(d, x0, y0, x1, y1, r, fill):
    d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill)


def line(d, pts, fill, w):
    d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(w * SS), joint="curve")


def pixelate(im):
    """降到像素网格，硬化 alpha"""
    small = im.resize((GRID, GRID), Image.LANCZOS)
    px = small.load()
    for y in range(GRID):
        for x in range(GRID):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 110 else (0, 0, 0, 0)
    return small


def add_outline(small, color=OUTLINE):
    """在像素网格上给不透明区域加 1px 外描边"""
    w, h = small.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    src = small.load()
    dst = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] > 0:
                continue
            hit = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
                    hit = True
                    break
            if hit:
                dst[x, y] = color
    out.alpha_composite(small)
    return out


def finish(im, name, outline=True):
    small = pixelate(im)
    if outline:
        small = add_outline(small)
    big = small.resize((GRID * PX, GRID * PX), Image.NEAREST)
    big.save(os.path.join(ITEMS, name))
    return big


# ============================================================
#  11 种食材
# ============================================================

def chive():          # 韭菜
    im, d = canvas()
    dark, mid, lite = (58, 122, 44, 255), (92, 168, 58, 255), (152, 208, 92, 255)
    for i, (x, col) in enumerate([(11, dark), (19, mid), (27, dark)]):
        sway = 2 if i == 1 else 0
        poly(d, [(x - 3, 34), (x + 3, 34), (x + 4 + sway, 8), (x - 1 + sway, 5), (x - 4, 9)], col)
    line(d, [(19, 30), (20, 14), (21, 8)], lite, 1.6)
    line(d, [(11, 31), (12, 12)], (120, 186, 74, 255), 1.2)
    return finish(im, "item-chive.png")


def shrimp():         # 虾仁
    im, d = canvas()
    body, shade, lite = (244, 140, 96, 255), (214, 92, 60, 255), (255, 198, 164, 255)
    # C 形虾身
    d.arc([9 * SS, 8 * SS, 33 * SS, 32 * SS], 300, 210, fill=body, width=int(7.5 * SS))
    d.arc([9 * SS, 8 * SS, 33 * SS, 32 * SS], 300, 210, fill=shade, width=int(2.2 * SS))
    d.arc([11 * SS, 10 * SS, 31 * SS, 30 * SS], 300, 200, fill=body, width=int(4.4 * SS))
    d.arc([12 * SS, 11 * SS, 29 * SS, 28 * SS], 320, 170, fill=lite, width=int(1.6 * SS))
    # 尾扇
    poly(d, [(14, 30), (8, 36), (6, 30), (10, 27)], shade)
    poly(d, [(13, 30), (9, 34), (8, 30), (11, 28)], body)
    ell(d, 26, 12, 29, 15, (72, 40, 30, 255))   # 眼
    return finish(im, "item-shrimp.png")


def corn():           # 玉米
    im, d = canvas()
    husk, husk2 = (96, 166, 62, 255), (140, 196, 84, 255)
    poly(d, [(13, 31), (3, 18), (5, 27), (11, 35)], husk)
    poly(d, [(27, 31), (37, 18), (35, 27), (29, 35)], husk)
    poly(d, [(13, 29), (7, 21), (9, 28), (12, 32)], husk2)
    rrect(d, 11, 6, 29, 34, 8, (232, 176, 46, 255))
    for r in range(7):
        for c in range(4):
            x = 13 + c * 4 + (2 if r % 2 else 0)
            y = 9 + r * 3.4
            if 11 < x < 28:
                ell(d, x - 1.5, y - 1.4, x + 1.5, y + 1.4, (252, 216, 92, 255))
    rrect(d, 12.5, 8, 16, 30, 3, (255, 234, 150, 90))
    return finish(im, "item-corn.png")


def pork():           # 五花肉
    im, d = canvas()
    rrect(d, 6, 11, 34, 30, 5, (226, 122, 118, 255))
    rrect(d, 6, 15.5, 34, 19, 2, (255, 236, 226, 255))
    rrect(d, 6, 23, 34, 26, 2, (255, 236, 226, 255))
    rrect(d, 6, 11, 34, 13.5, 2, (248, 228, 214, 255))
    rrect(d, 8, 12.5, 16, 15, 2, (245, 168, 160, 160))
    return finish(im, "item-pork.png")


def fennel():         # 茴香
    im, d = canvas()
    stem, frond, lite = (86, 148, 52, 255), (118, 190, 72, 255), (172, 224, 118, 255)
    line(d, [(20, 35), (20, 16)], stem, 2.2)
    for i, y in enumerate((30, 25, 20, 15)):
        sp = 10 - i * 1.2
        line(d, [(20, y + 1), (20 - sp, y - 4)], frond, 1.6)
        line(d, [(20, y + 1), (20 + sp, y - 4)], frond, 1.6)
        line(d, [(20 - sp * .6, y - 1.5), (20 - sp * .95, y - 6)], lite, 1.1)
        line(d, [(20 + sp * .6, y - 1.5), (20 + sp * .95, y - 6)], lite, 1.1)
    line(d, [(20, 17), (20, 8)], frond, 1.6)
    line(d, [(20, 12), (16, 7)], lite, 1.1)
    line(d, [(20, 12), (24, 7)], lite, 1.1)
    return finish(im, "item-fennel.png")


def egg():            # 煎蛋
    im, d = canvas()
    white, shade = (255, 250, 236, 255), (232, 220, 196, 255)
    poly(d, [(8, 22), (5, 15), (11, 9), (20, 6), (30, 8), (35, 15), (33, 24),
             (27, 32), (18, 34), (10, 30)], white)
    poly(d, [(9, 27), (16, 33), (26, 32), (31, 26), (30, 30), (20, 34), (11, 31)], shade)
    ell(d, 15, 12, 28, 25, (240, 168, 40, 255))
    ell(d, 16.5, 13.5, 25, 21, (255, 206, 74, 255))
    ell(d, 18, 15, 21.5, 18, (255, 234, 160, 255))
    return finish(im, "item-egg.png")


def mackerel():       # 鲅鱼
    im, d = canvas()
    back, belly, lite = (78, 118, 154, 255), (226, 234, 240, 255), (140, 180, 208, 255)
    poly(d, [(6, 20), (13, 12), (24, 10), (32, 15), (35, 20), (31, 26), (21, 30), (11, 27)], belly)
    poly(d, [(6, 20), (13, 12), (24, 10), (32, 15), (35, 20), (24, 19), (12, 20)], back)
    poly(d, [(14, 12), (24, 11), (22, 15), (13, 16)], lite)
    poly(d, [(6, 20), (1, 12), (0, 27), (7, 22)], back)      # 尾鳍
    poly(d, [(18, 24), (25, 24), (21, 30)], lite)            # 腹鳍
    poly(d, [(19, 11), (26, 12), (22, 7)], back)             # 背鳍
    ell(d, 29, 16, 32.5, 19.5, (250, 250, 250, 255))
    ell(d, 30, 17, 32, 19, (48, 34, 30, 255))
    return finish(im, "item-mackerel.png")


def octopus():        # 八蛸
    im, d = canvas()
    body, shade, lite = (198, 106, 148, 255), (162, 72, 118, 255), (238, 168, 196, 255)
    ell(d, 10, 5, 30, 24, body)
    ell(d, 13, 8, 22, 15, lite)
    for i, (x, dirn) in enumerate([(11, -1), (16, -1), (24, 1), (29, 1)]):
        for k in range(3):
            pass
        line(d, [(x, 20), (x + dirn * 3, 27), (x + dirn * 6, 30), (x + dirn * 4, 35)], body, 3.2)
    line(d, [(20, 22), (20, 31), (18, 36)], shade, 3.0)
    for (x, y) in [(9, 30), (14, 33), (26, 33), (31, 30)]:
        ell(d, x - 1.2, y - 1.2, x + 1.2, y + 1.2, shade)
    ell(d, 15, 13, 18.5, 17, (255, 255, 255, 255))
    ell(d, 22, 13, 25.5, 17, (255, 255, 255, 255))
    ell(d, 16, 14.2, 18, 16.4, (48, 34, 30, 255))
    ell(d, 23, 14.2, 25, 16.4, (48, 34, 30, 255))
    return finish(im, "item-octopus.png")


def scallop():        # 干贝 / 扇贝
    im, d = canvas()
    shell, shade, lite = (240, 206, 150, 255), (206, 160, 100, 255), (255, 238, 202, 255)
    poly(d, [(20, 33), (5, 16), (9, 10), (20, 6), (31, 10), (35, 16)], shell)
    for a in range(-5, 6):
        x = 20 + a * 3
        line(d, [(20, 32), (x, 9 + abs(a) * 1.1)], shade, 0.9)
    poly(d, [(20, 30), (9, 18), (12, 12), (20, 9), (28, 12), (31, 18)], (0, 0, 0, 0))
    poly(d, [(20, 33), (5, 16), (9, 10), (20, 6), (31, 10), (35, 16)], (0, 0, 0, 0))
    # 重画（避免上面清空）：底 + 放射纹 + 高光
    poly(d, [(20, 33), (5, 16), (9, 10), (20, 6), (31, 10), (35, 16)], shell)
    for a in range(-4, 5):
        x = 20 + a * 3.5
        line(d, [(20, 32), (x, 8.5 + abs(a) * 1.2)], shade, 0.9)
    poly(d, [(20, 33), (16, 30), (17, 34), (23, 34), (24, 30)], shade)
    line(d, [(13, 14), (18, 10)], lite, 1.4)
    return finish(im, "item-scallop.png")


def radish():         # 白萝卜
    im, d = canvas()
    white, shade = (250, 250, 248, 255), (216, 220, 226, 255)
    poly(d, [(14, 10), (26, 10), (27, 22), (23, 33), (20, 37), (17, 33), (13, 22)], white)
    poly(d, [(23, 12), (27, 22), (23, 33), (21, 36), (22, 26), (21, 13)], shade)
    line(d, [(15, 16), (25, 16)], (232, 236, 240, 255), 0.9)
    line(d, [(16, 22), (24, 22)], (232, 236, 240, 255), 0.9)
    for x, tip in [(14, (9, 3)), (20, (20, 1)), (26, (31, 4))]:
        line(d, [(x, 11), (tip[0], tip[1])], (96, 170, 62, 255), 2.2)
    ell(d, 17.5, 4, 22.5, 9, (132, 196, 78, 255))
    return finish(im, "item-radish.png")


def zhizha():         # 脂渣
    im, d = canvas()
    gold, deep, lite = (206, 142, 62, 255), (162, 100, 40, 255), (240, 194, 118, 255)
    chunks = [(13, 22, 9), (26, 17, 8), (22, 29, 7.5), (30, 28, 6)]
    for (cx, cy, r) in chunks:
        poly(d, [(cx - r * .9, cy), (cx - r * .5, cy - r * .8), (cx + r * .4, cy - r * .9),
                 (cx + r * .9, cy - r * .2), (cx + r * .6, cy + r * .8), (cx - r * .4, cy + r * .9)], gold)
    for (cx, cy, r) in chunks:
        poly(d, [(cx - r * .5, cy + r * .3), (cx + r * .5, cy + r * .5),
                 (cx + r * .5, cy + r * .85), (cx - r * .3, cy + r * .85)], deep)
        ell(d, cx - r * .55, cy - r * .6, cx - r * .05, cy - r * .1, lite)
    return finish(im, "item-zhizha.png")


# ============================================================
#  饺子皮（接馅料用的，就是擀好的那张皮）
# ============================================================

def skin():
    """一张擀好的圆饺子皮，略带俯视角所以画成扁椭圆。
       输出 320x160，和原来的竹托盘同宽，接取判定不用重调。"""
    G, H, P = 80, 40, 4
    im = Image.new("RGBA", (G * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def e(x0, y0, x1, y1, fill):
        d.ellipse([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=fill)

    def ln(pts, fill, w):
        d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(w * SS))

    # 背景是米黄天空，皮太白会糊在里面，所以整体压暖压深一档
    dough_d = (198, 160, 100, 255)     # 皮的厚度（侧面）
    dough   = (246, 226, 176, 255)     # 皮面
    lite    = (255, 246, 214, 255)     # 高光
    edge    = (216, 184, 124, 255)     # 边缘阴影
    flour   = (255, 252, 236, 255)     # 干面粉

    # 皮是薄的：底下只垫 2px 当厚度，再厚就成盘子了
    e(2, 13, 78, 35, dough_d)
    e(2, 11, 78, 33, dough)

    # 手擀的边不是正圆，沿边压几个浅鼓包
    for cx, cy, r in [(10,14,3.2),(26,12,3.4),(42,11.6,3.4),(58,12.4,3.4),(70,14.6,3.2),
                      (11,30,3.0),(27,32,3.2),(44,32.4,3.2),(60,31.4,3.2),(71,29,3.0)]:
        e(cx - r, cy - r * .55, cx + r, cy + r * .55, dough)

    e(13, 15, 67, 30, (240, 216, 162, 255))   # 中间擀得更薄，颜色略沉一点点
    ln([(13, 17), (32, 13.5)], lite, 1.5)     # 左上高光
    ln([(48, 13.5), (66, 17)], lite, 1.1)
    ln([(10, 27), (34, 31)], edge, 1.0)       # 下沿一条浅影，撑出一点厚度

    for fx, fy in [(21,19),(32,16.5),(45,19.5),(55,17),(27,26),(39,28),(52,25),(62,22),(17,23)]:
        e(fx, fy, fx + 1.2, fy + 1.2, flour)  # 撒的干面粉

    small = im.resize((G, H), Image.LANCZOS)
    px = small.load()
    for y in range(H):
        for x in range(G):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 110 else (0, 0, 0, 0)
    small = add_outline(small)
    big = small.resize((G * P, H * P), Image.NEAREST)
    big.save(os.path.join(OUT, "skin.png"))
    return big


def skin_shadow():
    w, h = 320, 60
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([14, 12, w - 14, h - 12], fill=(58, 30, 12, 165))
    im = im.filter(ImageFilter.GaussianBlur(8))
    im.save(os.path.join(OUT, "skin-shadow.png"))


def coin():           # 1 元硬币（限时奖励）
    """币面上手点了「1元」两个字。
       字是按 40x40 的网格一格一格点出来的 —— 用字体渲染再缩到这个尺寸会糊成一团。"""
    im, d = canvas()
    gold  = (240, 190, 56, 255)
    deep  = (188, 132, 24, 255)     # 边缘 / 厚度
    face  = (248, 206, 84, 255)     # 币面
    lite2 = (255, 250, 218, 255)
    ink   = (146, 96, 14, 255)      # 压印的字，深一档才看得清

    ell(d, 6, 9, 34, 34, deep)      # 底下垫一层当厚度，看着是立着的一枚
    ell(d, 6, 6, 34, 31, gold)
    ell(d, 8.2, 8.2, 31.8, 28.8, deep)    # 外圈凹槽
    ell(d, 9.4, 9.4, 30.6, 27.6, face)
    d.arc([9 * SS, 9 * SS, 31 * SS, 28 * SS], 195, 265, fill=lite2, width=int(1.5 * SS))

    # ---- 币面的「1元」，1 格 = 1 像素 ----
    def stamp(bits, ox, oy, color):
        for r, row in enumerate(bits):
            for c, ch in enumerate(row):
                if ch == "1":
                    d.rectangle([(ox + c) * SS, (oy + r) * SS,
                                 (ox + c + 1) * SS - 1, (oy + r + 1) * SS - 1], fill=color)

    ONE = ["010",
           "110",
           "010",
           "010",
           "010",
           "010",
           "111"]
    YUAN = ["0111110",
            "0000000",
            "1111111",
            "0010100",
            "0010100",
            "0100100",
            "1100111"]
    stamp(ONE,  14, 15, ink)
    stamp(YUAN, 18, 15, ink)
    return finish(im, "item-coin.png")


def sparkle():
    """接对时的小星星"""
    G, P = 24, 4
    im = Image.new("RGBA", (G * SS, G * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (255, 246, 200, 255)
    d.polygon([(12 * SS, 0), (14.5 * SS, 9.5 * SS), (24 * SS, 12 * SS), (14.5 * SS, 14.5 * SS),
               (12 * SS, 24 * SS), (9.5 * SS, 14.5 * SS), (0, 12 * SS), (9.5 * SS, 9.5 * SS)], fill=c)
    small = im.resize((G, G), Image.LANCZOS)
    px = small.load()
    for y in range(G):
        for x in range(G):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 110 else (0, 0, 0, 0)
    small = add_outline(small, (255, 196, 80, 255))
    small.resize((G * P, G * P), Image.NEAREST).save(os.path.join(ITEMS, "fx-sparkle.png"))



# ============================================================
#  标题艺术字
#  做法跟「馅料名艺术字」一致：小尺寸渲染 -> 分层描边 -> 整数放大 3 倍
#  所以笔画边缘是硬的方块，和那六张艺术字是同一挂
# ============================================================

FONT_CANDIDATES = [
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2),   # W6，最粗的一档
    ("/System/Library/Fonts/STHeiti Medium.ttc", 1),
]


def _load_font(size):
    from PIL import ImageFont
    for path, idx in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    raise RuntimeError("找不到中文字体，改 FONT_CANDIDATES")


def _dilate(mask, r):
    """把字形往外扩 r 像素，用来做描边层"""
    from PIL import ImageFilter
    out = mask
    for _ in range(r):
        out = out.filter(ImageFilter.MaxFilter(3))
    return out


def _vgrad(size, top, bottom):
    w, h = size
    g = Image.new("RGBA", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4)))
    return g.resize((w, h), Image.NEAREST)


def word_art(text, out_name, scale=2, font_px=64, pad=20, gap=3,
             fill_top=(255, 253, 242, 255), fill_mid=(255, 224, 138, 255), fill_bot=(232, 150, 26, 255),
             rim=(74, 36, 16, 255), outer=(240, 182, 70, 255), rim_r=5, outer_r=7,
             shadow=(60, 28, 12, 120), shadow_dy=7):
    """一张游戏艺术字。字形先二值化，保证放大后边缘是硬方块而不是糊边。"""
    from PIL import ImageDraw as _D
    font = _load_font(font_px)

    probe = _D.Draw(Image.new("L", (10, 10)))
    boxes = [probe.textbbox((0, 0), ch, font=font) for ch in text]
    widths = [b[2] - b[0] for b in boxes]
    W = sum(widths) + gap * (len(text) - 1) + pad * 2
    H = font_px + pad * 2

    mask = Image.new("L", (W, H), 0)
    md = _D.Draw(mask)
    x = pad
    for ch, b, w in zip(text, boxes, widths):
        md.text((x - b[0], pad - b[1]), ch, font=font, fill=255)
        x += w + gap
    mask = mask.point(lambda v: 255 if v >= 128 else 0)      # 二值化 = 像素硬边

    m_outer = _dilate(mask, outer_r)
    m_rim   = _dilate(mask, rim_r)

    im = Image.new("RGBA", (W, H + shadow_dy), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (W, H), shadow), (0, shadow_dy), m_outer)
    im.alpha_composite(sh)

    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.paste(Image.new("RGBA", (W, H), outer), (0, 0), m_outer)
    lay.paste(Image.new("RGBA", (W, H), rim), (0, 0), m_rim)

    # 字面：上白 → 中浅金 → 下金，三段渐变，比两段更有"糖霜感"
    grad = Image.new("RGBA", (W, H))
    for y in range(H):
        t = y / max(1, H - 1)
        if t < .52:
            k = t / .52
            c = tuple(int(fill_top[i] + (fill_mid[i] - fill_top[i]) * k) for i in range(4))
        else:
            k = (t - .52) / .48
            c = tuple(int(fill_mid[i] + (fill_bot[i] - fill_mid[i]) * k) for i in range(4))
        for xx in range(W):
            grad.putpixel((xx, y), c)
    lay.paste(grad, (0, 0), mask)
    im.alpha_composite(lay, (0, 0))

    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    big.save(os.path.join(OUT, out_name))
    return big


def titles():
    word_art("接馅料·包饺子", "title-catch.png")                       # 约 1004 x 182
    word_art("包饺子排行榜", "title-board.png", font_px=52, rim_r=4, outer_r=6, shadow_dy=6)


if __name__ == "__main__":
    for fn in (chive, shrimp, corn, pork, fennel, egg, mackerel, octopus, scallop, radish, zhizha):
        fn()
        print("ok", fn.__name__)
    coin(); skin(); skin_shadow(); sparkle(); titles()
    print("饺子皮 / 阴影 / 星星 完成")
