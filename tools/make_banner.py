#!/usr/bin/env python3
"""生成 GitHub 主页顶部 banner：身份 + 关键指标 + 控制栈分层 + 档案统计。

视觉语言对齐 atec-robotics-projects 的任务封面（深色底、青绿强调、大字号指标），
让主页与各仓库内的图看起来是同一套设计。整张图是独立深色卡片，
在 GitHub 亮色/暗色主题下都成立，因此只出一版。

banner 只放跨项目通用的信息；具体项目名与数字归 README 正文维护，
避免每加一个仓库就要改图。
"""
from pathlib import Path

W = 1000
PAD = 28
HEAD_H = 128
ROW_H = 58
ROW_GAP = 6
FOOT_H = 46
BAR_W = 3

C = dict(
    bg="#0f1621", card="#18212f", line="#243043",
    title="#f0f4f8", sub="#93a1b5", body="#b8c4d4",
    accent="#3ddc97", repo="#6fb4f0", dim="#5f6e82",
    badge_bg="#143a2a", badge_fg="#3ddc97",
)

# (数字, 单位, 说明)
# 三条各占一层：规划/感知、实时执行、部署验证
METRICS = [
    ("286", "m", "四足带臂连续越障"),
    ("2", "ms", "实车控制周期"),
    ("43,200", "次", "C++ 零物理推理"),
]

# (层名, 技术点, 对应仓库, 色条不透明度)
LAYERS = [
    ("任务与路径规划", "多智能体路径规划 · 终身执行调度 · RGB-D 闭环导航",
     "MAPF 研究线 · atec-robotics-projects", 0.30),
    ("轨迹生成与优化", "约束 MPC · DLS 解析逆运动学 · 残差策略 PPO · ONNX 实时推理",
     "wheel-legged-control-lab · ddt-d1-rl-lab", 0.47),
    ("反馈控制", "LQR · 滑模 SMC · ESO 扰动观测 · 阻抗 / 导纳 / 力位混合 · VMC",
     "robot-arm-compliant-control-lab · gimbal-lqr-eso · gimbal-smc-controller", 0.65),
    ("状态估计与辨识", "递推最小二乘 · 编码器与摩擦辨识 · PnP 位姿 · IMU 融合",
     "robot-vision-control-lab · gimbal-lqr-eso · 系统辨识课程", 0.82),
    ("执行器与实时层", "GM6020 电流模式 · DM4310 MIT 力矩 · 50–100 Hz 决策 / 500 Hz 物理 · FreeRTOS",
     "Rudder-Swerve-Control · ddt-d1-rl-lab", 1.0),
]

# 底部统计：只写结构性事实，不写会随提交变化的小数字
FOOT_LEFT = "控制栈 5 层 · 公开项目 16"
FOOT_RIGHT = "研究 · 实车 · 教学 · 工具 · 更新 2026-11"

FONT = ('-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",'
        '"PingFang SC","Microsoft YaHei",Helvetica,Arial,sans-serif')
MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace'

TECH_X = PAD + 190


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    h = (HEAD_H + len(LAYERS) * ROW_H + (len(LAYERS) - 1) * ROW_GAP
         + FOOT_H + PAD)
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" '
        f'aria-label="LYH · 机器人控制与规划 · 控制栈分层档案">',
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
        f'.ft{{font-family:{FONT};font-size:9.5px;fill:{C["dim"]};letter-spacing:.2px}}'
        f'.idx{{font-family:{MONO};font-size:11px;font-weight:600;'
        f'fill:{C["accent"]};fill-opacity:.55}}'
        f'</style>',
        f'<defs>'
        f'<radialGradient id="bg" cx="12%" cy="0%" r="95%">'
        f'<stop offset="0" stop-color="#17222f"/>'
        f'<stop offset="1" stop-color="#0e141d"/>'
        f'</radialGradient>'
        f'<linearGradient id="mark" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{C["accent"]}" stop-opacity="1"/>'
        f'<stop offset="1" stop-color="{C["accent"]}" stop-opacity=".2"/>'
        f'</linearGradient>'
        f'</defs>',
        f'<rect width="{W}" height="{h}" rx="12" fill="url(#bg)"/>',
        # 左侧色标，给名字一个视觉起点
        f'<rect x="{PAD}" y="24" width="4" height="62" rx="2" fill="url(#mark)"/>',
        f'<text class="nm" x="{PAD + 18}" y="58">LYH</text>',
        f'<text class="dir" x="{PAD + 18}" y="84">机器人控制 / 规划控制</text>',
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
        o.append(f'<text class="idx" x="{PAD + 16}" y="{y + 35}">{i + 1:02d}</text>')
        o.append(f'<text class="ln" x="{PAD + 46}" y="{y + 34}">{esc(name)}</text>')
        o.append(f'<text class="tc" x="{TECH_X}" y="{y + 25}">{esc(tech)}</text>')
        o.append(f'<text class="rp" x="{TECH_X}" y="{y + 42}">{esc(repos)}</text>')

        if i == len(LAYERS) - 1:
            bw = 78
            bx = PAD + cw - bw - 16
            o.append(f'<rect x="{bx}" y="{y + 19}" width="{bw}" height="20" rx="10" '
                     f'fill="{C["badge_bg"]}"/>'
                     f'<text class="bd" x="{bx + bw / 2}" y="{y + 32.5}" '
                     f'text-anchor="middle">赛季实车验证</text>')

    # 底部档案统计：左右各一条，中间留空保持呼吸感
    foot_top = HEAD_H + len(LAYERS) * ROW_H + (len(LAYERS) - 1) * ROW_GAP
    o.append(f'<line x1="{PAD}" y1="{foot_top + 18}" x2="{W - PAD}" '
             f'y2="{foot_top + 18}" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(f'<text class="ft" x="{PAD}" y="{foot_top + 40}">{esc(FOOT_LEFT)}</text>')
    o.append(f'<text class="ft" x="{W - PAD}" y="{foot_top + 40}" '
             f'text-anchor="end">{esc(FOOT_RIGHT)}</text>')

    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    p = out / "banner.svg"
    p.write_text(build(), encoding="utf-8")
    print(f"{p}  {p.stat().st_size} bytes")
