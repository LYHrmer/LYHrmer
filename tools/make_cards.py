#!/usr/bin/env python3
"""生成主页精选区的两张图卡，以及控制器同场对比动图。

图卡把画面和说明文字画在同一张图里：两张图在 README 中并排、各占 48.5% 宽，
文字只有画进图里才能和图片严格对齐，不会随窗口宽度换行错位。底色取 GitHub
亮色 #ffffff 与暗色 #0d1117，与页面底色一致，看起来是页面里的一段排版。

原图放在 /var/tmp/imgchk（历史素材目录，不进仓库）；这里只做裁剪、缩放和排版，
结果输出到 assets/。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence

SRC = Path("/var/tmp/imgchk")
OUT = Path(__file__).resolve().parent.parent / "assets"

# 图卡尺寸按 GitHub 正文宽度的两倍出图：README 里两张并排、各显示约 422px 宽
CARD_W, PHOTO_H, CAP_H = 844, 475, 126

THEMES = {
    "light": dict(bg=(255, 255, 255), ink=(23, 24, 26), muted=(95, 100, 107)),
    "dark": dict(bg=(13, 17, 23), ink=(238, 240, 242), muted=(154, 160, 168)),
}

# (源图, 纵向取景重心, 输出名, 标题, 副标题)
PROJECTS = [
    dict(src="r_2024-swerve.jpg", focus=0.375, out="card-swerve",
         title="Rudder-Swerve-Control",
         metric="RoboMaster 2024 辽宁站亚军 · 2 ms 控制周期"),
    dict(src="atec.jpg", focus=0.5, out="card-atec",
         title="atec-robotics-projects",
         metric="连续越障 286 m · 抓取 18/18"),
]

# 同一套 CJK 字体在 Linux / macOS 上的候选，取第一个能加载且含中文的
FONT_BOLD = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 2),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1),
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
]
FONT_REGULAR = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 2),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
]

TITLE_PT, METRIC_PT = 34, 24
GIF_W = 1100


def load_font(candidates, size):
    """按候选顺序加载字号；中文缺字回退到系统字体，找不到就报错而不是静默降级。"""
    for path, index in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size, index=index)
    raise FileNotFoundError("找不到可用的 CJK 字体：" + str(candidates))


def crop_ratio(im, ratio, focus):
    """按目标宽高比居中裁剪；focus 指定纵向取景重心（0=顶部，1=底部）。"""
    w, h = im.size
    if w / h > ratio:            # 过宽 → 裁两侧
        nw = int(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / ratio)          # 过高 → 按 focus 裁上下
    top = max(0, min(h - nh, int(h * focus - nh / 2)))
    return im.crop((0, top, w, top + nh))


def make_card(prj, theme_name):
    """把一张图卡画成 JPEG：上方画面，下方标题与副标题。"""
    t = THEMES[theme_name]
    photo = Image.open(SRC / prj["src"]).convert("RGB")
    photo = crop_ratio(photo, CARD_W / PHOTO_H, prj["focus"])
    photo = photo.resize((CARD_W, PHOTO_H), Image.LANCZOS)

    card = Image.new("RGB", (CARD_W, PHOTO_H + CAP_H), t["bg"])
    card.paste(photo, (0, 0))
    d = ImageDraw.Draw(card)
    # x=2 避开字形左边缘被裁掉的那一像素
    d.text((2, PHOTO_H + 40), prj["title"],
           font=load_font(FONT_BOLD, TITLE_PT), fill=t["ink"])
    d.text((2, PHOTO_H + 88), prj["metric"],
           font=load_font(FONT_REGULAR, METRIC_PT), fill=t["muted"])

    path = OUT / f"{prj['out']}-{theme_name}.jpg"
    card.save(path, "JPEG", quality=90, subsampling=0,
              optimize=True, progressive=True)
    return path


def white_bbox(im):
    """返回非白内容的包围盒，用于去掉 matplotlib 输出的大片留白。"""
    g = ImageOps.invert(im.convert("L"))
    return g.point(lambda p: 255 if p > 6 else 0).getbbox()


def make_strip_gif(src, dst, step=3, pad=10, colors=32):
    """裁掉上下留白并等比缩放，保留动画。

    不指定 disposal，让编码器自己做帧间差分——显式设 disposal=2 会强制每帧
    存完整画面，反而比原图更大。
    """
    im = Image.open(SRC / src)
    box = white_bbox(im.convert("RGB"))
    top = max(0, box[1] - pad)
    bot = min(im.size[1], box[3] + pad)

    frames, durations = [], []
    for i, fr in enumerate(ImageSequence.Iterator(im)):
        if i % step:
            continue
        f = fr.convert("RGB").crop((0, top, im.size[0], bot))
        nh = round(f.size[1] * GIF_W / f.size[0])
        frames.append(f.resize((GIF_W, nh), Image.LANCZOS)
                      .quantize(colors=colors, method=Image.MEDIANCUT))
        durations.append(fr.info.get("duration", 50) * step)

    frames[0].save(OUT / dst, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    return OUT / dst, len(frames), frames[0].size


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for prj in PROJECTS:
        for theme_name in THEMES:
            p = make_card(prj, theme_name)
            print(f"{p.name:26} {p.stat().st_size // 1024} KB")

    p, n, size = make_strip_gif("wheel.gif", "strip-wheel-legged.gif")
    print(f"{p.name:26} {p.stat().st_size // 1024} KB  {n} 帧  "
          f"{size[0]}x{size[1]}")
