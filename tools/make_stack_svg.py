#!/usr/bin/env python3
"""生成 GitHub 主页用的控制栈分层图，输出 light / dark 两版 SVG。

两版只有配色不同，结构由同一份 LAYERS 数据驱动，避免手写两份 SVG 产生漂移。
"""
from pathlib import Path

W = 880
PAD = 8
ROW_H = 64
GAP = 10
BAR_W = 5

# (层名, 技术点, 对应仓库, 色条不透明度)
LAYERS = [
    ("任务与路径规划", "多智能体路径规划 · 终身场景执行调度 · RGB-D 闭环导航",
     "MAPF 执行层（研究中） · atec-robotics-projects", 0.32),
    ("轨迹生成与优化", "约束 MPC · DLS 解析逆运动学 · 残差策略（PPO） · 地形课程",
     "wheel-legged-control-lab · atec-robotics-projects", 0.48),
    ("反馈控制", "LQR · 滑模 SMC · ESO 扰动观测 · 阻抗 / 导纳 / 力位混合 · VMC",
     "robot-arm-compliant-control-lab · gimbal-lqr-eso · gimbal-smc-controller", 0.66),
    ("状态估计与辨识", "递推最小二乘 · 编码器与摩擦辨识 · PnP 位姿 · IMU 融合",
     "robot-vision-control-lab · gimbal-lqr-eso", 0.84),
    ("执行器与实时层", "GM6020 电流模式 · DM4310 MIT 力矩 · 2 ms 控制周期 · FreeRTOS",
     "Rudder-Swerve-Control（实车）", 1.0),
]

THEMES = {
    "light": dict(card="#f6f8fa", border="#d8dee4", title="#1f2328",
                  body="#57606a", repo="#0969da", accent="#0969da",
                  axis="#8c959f", badge_bg="#dafbe1", badge_fg="#1a7f37"),
    "dark": dict(card="#161b22", border="#30363d", title="#e6edf3",
                 body="#8b949e", repo="#58a6ff", accent="#58a6ff",
                 axis="#6e7681", badge_bg="#132d1b", badge_fg="#3fb950"),
}

FONT = ('-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",'
        '"PingFang SC","Microsoft YaHei",Helvetica,Arial,sans-serif')
MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace'

AXIS_X = 34          # 左侧下行箭头
CARD_X = AXIS_X + 26
CARD_W = W - CARD_X - PAD
TEXT_X = CARD_X + 18
TECH_X = CARD_X + 150


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(theme_name: str) -> str:
    c = THEMES[theme_name]
    height = len(LAYERS) * ROW_H + (len(LAYERS) - 1) * GAP + PAD * 2
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" '
        f'aria-label="运动控制与规划技术栈分层图">',
        "<defs>",
        '  <marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        f'    <path d="M0,1 L9,5 L0,9 z" fill="{c["axis"]}"/>',
        "  </marker>",
        "</defs>",
        f'<style>'
        f'.t{{font-family:{FONT};font-size:13.5px;font-weight:600;fill:{c["title"]}}}'
        f'.b{{font-family:{FONT};font-size:11px;fill:{c["body"]}}}'
        f'.r{{font-family:{MONO};font-size:9.5px;fill:{c["repo"]}}}'
        f'.ax{{font-family:{FONT};font-size:10px;fill:{c["axis"]}}}'
        f'.bg{{font-family:{FONT};font-size:9px;font-weight:600;fill:{c["badge_fg"]}}}'
        f'</style>',
    ]

    top, bot = PAD + 6, height - PAD - 6
    o.append(f'<line x1="{AXIS_X}" y1="{top}" x2="{AXIS_X}" y2="{bot}" '
             f'stroke="{c["axis"]}" stroke-width="1.1" marker-end="url(#arw)"/>')
    mid = (top + bot) / 2
    o.append(f'<text class="ax" transform="translate({AXIS_X - 9},{mid}) rotate(-90)" '
             f'text-anchor="middle">指令下行 · 状态上行</text>')

    for i, (name, tech, repos, op) in enumerate(LAYERS):
        y = PAD + i * (ROW_H + GAP)
        o.append(f'<clipPath id="c{i}"><rect x="{CARD_X}" y="{y}" '
                 f'width="{CARD_W}" height="{ROW_H}" rx="7"/></clipPath>')
        o.append(f'<rect x="{CARD_X}" y="{y}" width="{CARD_W}" height="{ROW_H}" '
                 f'rx="7" fill="{c["card"]}" stroke="{c["border"]}"/>')
        # 色条随层级加深，表示从规划抽象层走向硬件执行层
        o.append(f'<rect x="{CARD_X}" y="{y}" width="{BAR_W}" height="{ROW_H}" '
                 f'fill="{c["accent"]}" fill-opacity="{op}" clip-path="url(#c{i})"/>')

        o.append(f'<text class="t" x="{TEXT_X}" y="{y + 30}">{esc(name)}</text>')
        o.append(f'<text class="b" x="{TECH_X}" y="{y + 27}">{esc(tech)}</text>')
        o.append(f'<text class="r" x="{TECH_X}" y="{y + 46}">{esc(repos)}</text>')

        if "实车" in repos:
            bx = CARD_X + CARD_W - 74
            o.append(f'<rect x="{bx}" y="{y + 12}" width="58" height="17" rx="8.5" '
                     f'fill="{c["badge_bg"]}"/>'
                     f'<text class="bg" x="{bx + 29}" y="{y + 23.5}" '
                     f'text-anchor="middle">上车验证</text>')

    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for name in THEMES:
        p = out / f"control-stack-{name}.svg"
        p.write_text(build(name), encoding="utf-8")
        print(f"{p}  {p.stat().st_size} bytes")
