#!/usr/bin/env python3
"""生成主页「控制栈」分区图：5 层结构，浅色与深色两版。

每层一行：左侧序号、层名、关键方法，右侧一个代表指标；行间只用发丝线分隔，
靠字号拉开层级，读起来是文档里的一张结构图，而不是仪表盘。序号用强调色的
透明度做递减——层数越靠上越浅，对应控制栈从上到下的顺序。

README 用 <picture> 按主题切换两版；每个仓库的具体结果放在图下方的折叠区，
图只负责概览，避免同一批文字出现两遍。
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

FONT = ('-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",'
        '"PingFang SC","Microsoft YaHei",Helvetica,Arial,sans-serif')
MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace'

W, PAD, TOP, ROW_H = 1120, 40, 30, 112

# (序号, 层名, 关键方法, 代表指标, 指标说明)
LAYERS = [
    ("01", "轨迹生成与优化",
     "约束 MPC · DLS 解析逆运动学 · 残差策略 PPO · ONNX 实时推理",
     "0.0333 m/s", "留出道路速度误差"),
    ("02", "反馈控制",
     "LQR · 滑模 SMC · ESO 扰动观测 · 阻抗 / 导纳 / 力位混合 · VMC",
     "−72.5%", "DM4310 Pitch 误差"),
    ("03", "状态估计与辨识",
     "递推最小二乘 · 编码器与摩擦辨识 · PnP 位姿 · IMU 融合",
     "6.03 mm", "PnP 位置误差"),
    ("04", "执行器与实时层",
     "GM6020 电流模式 · DM4310 力矩 · 500 Hz 物理步进 · FreeRTOS",
     "2 ms", "实车控制周期"),
    ("05", "感知、导航与仿真",
     "RGB-D 闭环导航 · 点云聚类抓取 · 连续越障",
     "286 m", "四足带臂连续越障"),
]

PALETTES = {
    "light": dict(ink="#17181a", muted="#5f646b", faint="#8d939a",
                  hair="#e4e4e0", accent="#0f766e"),
    "dark": dict(ink="#eef0f2", muted="#9aa0a8", faint="#6a7078",
                 hair="#2a2f36", accent="#4fd1c5"),
}


def build(kind):
    """按配色返回一份 SVG 文本；两版结构一致，只换颜色。"""
    p = PALETTES[kind]
    css = (
        f'.ln{{stroke:{p["hair"]};stroke-width:1.2}}'
        f'.idx{{font-family:{MONO};font-size:13px;font-weight:600;'
        f'fill:{p["accent"]}}}'
        f'.nm{{font-family:{FONT};font-size:25px;font-weight:600;'
        f'fill:{p["ink"]}}}'
        f'.mt{{font-family:{FONT};font-size:17px;font-weight:400;'
        f'fill:{p["muted"]}}}'
        f'.mv{{font-family:{FONT};font-size:26px;font-weight:600;'
        f'fill:{p["ink"]}}}'
        f'.ml{{font-family:{FONT};font-size:14px;font-weight:400;'
        f'fill:{p["faint"]}}}'
    )
    h = TOP * 2 + ROW_H * len(LAYERS)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
         f'viewBox="0 0 {W} {h}" role="img" '
         f'aria-label="控制栈 5 层：轨迹生成与优化、反馈控制、状态估计与辨识、'
         f'执行器与实时层、感知导航与仿真">',
         f'<style>{css}</style>']
    for i, (idx, name, methods, metric, metric_label) in enumerate(LAYERS):
        y0 = TOP + i * ROW_H
        if i:
            o.append(f'<line class="ln" x1="{PAD}" y1="{y0}" '
                     f'x2="{W - PAD}" y2="{y0}"/>')
        opacity = 0.38 + 0.155 * i
        o.append(f'<text class="idx" x="{PAD}" y="{y0 + 44}" '
                 f'fill-opacity="{opacity:.2f}">{idx}</text>')
        o.append(f'<text class="nm" x="{PAD + 44}" y="{y0 + 46}">{name}</text>')
        o.append(f'<text class="mt" x="{PAD + 44}" y="{y0 + 80}">{methods}</text>')
        o.append(f'<text class="mv" x="{W - PAD}" y="{y0 + 46}" '
                 f'text-anchor="end">{metric}</text>')
        o.append(f'<text class="ml" x="{W - PAD}" y="{y0 + 80}" '
                 f'text-anchor="end">{metric_label}</text>')
    o.append('</svg>')
    return '\n'.join(o) + '\n'


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for kind in PALETTES:
        path = OUT / f"stack-{kind}.svg"
        path.write_text(build(kind), "utf-8")
        print(f"{path.name:18} {path.stat().st_size // 1024} KB")
