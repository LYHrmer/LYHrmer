#!/usr/bin/env python3
"""把各仓库的原始素材加工成主页可直接用的统一规格图，输出到 assets/。

只处理三张视觉够强的素材：赛场实车照、ATEC 任务封面、三联控制器对比动图。
matplotlib 曲线图不在此列——裁剪会丢坐标轴，塞进固定比例网格也不好看。
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageSequence

SRC = Path("/var/tmp/imgchk")
OUT = Path(__file__).resolve().parent.parent / "assets"
CARD_W, CARD_H = 800, 450          # 卡片位统一 16:9
BANNER_W = 1100                    # 通栏动图宽度


def crop_to_ratio(im, ratio, focus=0.5):
    """按目标宽高比居中裁剪；focus 指定纵向取景重心（0=顶部，1=底部）。"""
    w, h = im.size
    if w / h > ratio:                      # 过宽 → 裁两侧
        nw = int(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / ratio)                    # 过高 → 按 focus 裁上下
    top = max(0, min(h - nh, int(h * focus - nh / 2)))
    return im.crop((0, top, w, top + nh))


def make_card(src, dst, focus=0.5, quality=86):
    im = Image.open(SRC / src).convert("RGB")
    im = crop_to_ratio(im, CARD_W / CARD_H, focus)
    im = im.resize((CARD_W, CARD_H), Image.LANCZOS)
    im.save(OUT / dst, "JPEG", quality=quality, optimize=True, progressive=True)
    return OUT / dst


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
        nh = round(f.size[1] * BANNER_W / f.size[0])
        frames.append(f.resize((BANNER_W, nh), Image.LANCZOS)
                      .quantize(colors=colors, method=Image.MEDIANCUT))
        durations.append(fr.info.get("duration", 50) * step)

    frames[0].save(OUT / dst, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    return OUT / dst, len(frames), frames[0].size


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    # 2024 辽宁站合影：4:3 横构图，从顶部裁能同时保住背景板成绩、奖杯与整车
    for p in [make_card("r_2024-swerve.jpg", "card-swerve.jpg", focus=0.375),
              make_card("atec.jpg", "card-atec.jpg")]:
        print(f"{p.name:20} {p.stat().st_size // 1024} KB")

    p, n, size = make_strip_gif("wheel.gif", "strip-wheel-legged.gif")
    print(f"{p.name:20} {p.stat().st_size // 1024} KB  {n} 帧  {size[0]}x{size[1]}")
