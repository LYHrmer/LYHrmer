#!/usr/bin/env python3
"""生成 GitHub 主页顶部 banner：身份 + 关键指标 + 控制栈分层。

视觉语言对齐 atec-robotics-projects 的任务封面（深色底、青绿强调、大字号指标），
让主页与各仓库内的图看起来是同一套设计。整张图是独立深色卡片，
在 GitHub 亮色/暗色主题下都成立，因此只出一版。
"""
from pathlib import Path

W = 1000
PAD = 28
HEAD_H = 112
ROW_H = 56
ROW_GAP = 6
BAR_W = 3

C = dict(
    bg="#0f1621", card="#18212f", line="#243043",
    title="#f0f4f8", sub="#93a1b5", body="#b8c4d4",
    accent="#3ddc97", repo="#6fb4f0", dim="#5f6e82",
    badge_bg="#143a2a", badge_fg="#3ddc97",
)

# (数字, 单位, 说明)
METRICS = [
    ("286", "m", "四足带臂连续越障"),
    ("1.359", "mm", "力控跟踪误差"),
    ("2", "ms", "实车控制周期"),
]

# (层名, 技术点, 对应仓库, 色条不透明度)
LAYERS = [
    ("任务与路径规划", "多智能体路径规划 · 终身场景执行调度 · RGB-D 闭环导航",
     "MAPF 执行层 · atec-robotics-projects", 0.30),
    ("轨迹生成与优化", "约束 MPC · DLS 解析逆运动学 · 残差策略（PPO） · 地形课程",
     "wheel-legged-control-lab · atec-robotics-projects", 0.47),
    ("反馈控制", "LQR · 滑模 SMC · ESO 扰动观测 · 阻抗 / 导纳 / 力位混合 · VMC",
     "robot-arm-compliant-control-lab · gimbal-lqr-eso · gimbal-smc-controller", 0.65),
    ("状态估计与辨识", "递推最小二乘 · 编码器与摩擦辨识 · PnP 位姿 · IMU 融合",
     "robot-vision-control-lab · gimbal-lqr-eso", 0.82),
    ("执行器与实时层", "GM6020 电流模式 · DM4310 MIT 力矩 · 2 ms 控制周期 · FreeRTOS",
     "Rudder-Swerve-Control", 1.0),
]

FONT = ('-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",'
        '"PingFang SC","Microsoft YaHei",Helvetica,Arial,sans-serif')
MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace'

TECH_X = PAD + 172


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    h = HEAD_H + len(LAYERS) * ROW_H + (len(LAYERS) - 1) * ROW_GAP + PAD
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" '
        f'aria-label="LYH · 运动控制与规划控制 · 技术栈分层">',
        f'<style>'
        f'.nm{{font-family:{FONT};font-size:33px;font-weight:700;fill:{C["title"]}}}'
        f'.dir{{font-family:{FONT};font-size:13px;font-weight:500;fill:{C["accent"]};'
        f'letter-spacing:.4px}}'
        f'.mv{{font-family:{FONT};font-size:25px;font-weight:700;fill:{C["accent"]}}}'
        f'.mu{{font-family:{FONT};font-size:12px;font-weight:500;fill:{C["accent"]}}}'
        f'.ml{{font-family:{FONT};font-size:10px;fill:{C["dim"]}}}'
        f'.ln{{font-family:{FONT};font-size:13px;font-weight:600;fill:{C["title"]}}}'
        f'.tc{{font-family:{FONT};font-size:10.5px;fill:{C["body"]}}}'
        f'.rp{{font-family:{MONO};font-size:9px;fill:{C["repo"]}}}'
        f'.bd{{font-family:{FONT};font-size:8.5px;font-weight:600;fill:{C["badge_fg"]}}}'
        f'</style>',
        f'<rect width="{W}" height="{h}" rx="12" fill="{C["bg"]}"/>',
        f'<text class="nm" x="{PAD}" y="54">LYH</text>',
        f'<text class="dir" x="{PAD}" y="80">运动控制 / 规划控制</text>',
    ]

    # 右上角指标，从右向左排布
    mw = 148
    x0 = W - PAD - mw * len(METRICS)
    for i, (val, unit, label) in enumerate(METRICS):
        x = x0 + i * mw
        if i:
            o.append(f'<line x1="{x - 14}" y1="34" x2="{x - 14}" y2="82" '
                     f'stroke="{C["line"]}" stroke-width="1"/>')
        o.append(f'<text class="mv" x="{x}" y="58">{val}'
                 f'<tspan class="mu" dx="3">{unit}</tspan></text>')
        o.append(f'<text class="ml" x="{x}" y="77">{esc(label)}</text>')

    o.append(f'<line x1="{PAD}" y1="{HEAD_H - 14}" x2="{W - PAD}" y2="{HEAD_H - 14}" '
             f'stroke="{C["line"]}" stroke-width="1"/>')

    cw = W - PAD * 2
    for i, (name, tech, repos, op) in enumerate(LAYERS):
        y = HEAD_H + i * (ROW_H + ROW_GAP)
        o.append(f'<clipPath id="k{i}"><rect x="{PAD}" y="{y}" width="{cw}" '
                 f'height="{ROW_H}" rx="6"/></clipPath>')
        o.append(f'<rect x="{PAD}" y="{y}" width="{cw}" height="{ROW_H}" rx="6" '
                 f'fill="{C["card"]}"/>')
        # 色条随层级加深：从规划抽象层走向硬件执行层
        o.append(f'<rect x="{PAD}" y="{y}" width="{BAR_W}" height="{ROW_H}" '
                 f'fill="{C["accent"]}" fill-opacity="{op}" clip-path="url(#k{i})"/>')
        o.append(f'<text class="ln" x="{PAD + 18}" y="{y + 32}">{esc(name)}</text>')
        o.append(f'<text class="tc" x="{TECH_X}" y="{y + 24}">{esc(tech)}</text>')
        o.append(f'<text class="rp" x="{TECH_X}" y="{y + 41}">{esc(repos)}</text>')

        if i == len(LAYERS) - 1:
            bw = 78
            bx = PAD + cw - bw - 16
            o.append(f'<rect x="{bx}" y="{y + 18}" width="{bw}" height="20" rx="10" '
                     f'fill="{C["badge_bg"]}"/>'
                     f'<text class="bd" x="{bx + bw / 2}" y="{y + 31.5}" '
                     f'text-anchor="middle">赛季实车验证</text>')

    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    p = out / "banner.svg"
    p.write_text(build(), encoding="utf-8")
    print(f"{p}  {p.stat().st_size} bytes")
