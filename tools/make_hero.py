#!/usr/bin/env python3
"""生成主页顶部横幅：浅色与深色两版 SVG，GitHub 按主题切换。

版式是左侧身份、右侧指标的一行式：姓名、方向，加一句定位；右边三条可核验的
数字，用发丝线隔开。整张图不铺底色——浅色版叠在页面白底上、深色版叠在 #0d1117
上，两版共用同一套坐标，只换配色，因此看起来像页面里的一段排版，而不是贴上去
的海报。

README 用 <picture> + prefers-color-scheme 引用两版。图里只放跨项目通用的数字，
具体项目名和结果归 README 正文维护，免得每加一个仓库就要改图。
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

FONT = ('-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans CJK SC",'
        '"PingFang SC","Microsoft YaHei",Helvetica,Arial,sans-serif')

W, H = 1400, 300

PALETTES = {
    "light": dict(ink="#17181a", muted="#5f646b", faint="#8d939a",
                  hair="#e4e4e0", accent="#0f766e"),
    "dark": dict(ink="#eef0f2", muted="#9aa0a8", faint="#6a7078",
                 hair="#2a2f36", accent="#4fd1c5"),
}

# (数值, 单位, 说明)：只放跨项目通用、且有结果文档支撑的数字
METRICS = [
    ("286", "m", "四足带臂连续越障"),
    ("2", "ms", "实车控制周期"),
    ("43,200", "次", "单线程 ONNX 推理"),
]
METRIC_X = [820, 1010, 1200]


def build(kind):
    """按配色返回一份 SVG 文本；两版除颜色外结构完全一致。"""
    p = PALETTES[kind]
    css = (
        f'.nm{{font-family:{FONT};font-size:70px;font-weight:600;'
        f'letter-spacing:-2.2px;fill:{p["ink"]}}}'
        f'.role{{font-family:{FONT};font-size:23px;font-weight:500;'
        f'fill:{p["ink"]}}}'
        f'.tag{{font-family:{FONT};font-size:18px;font-weight:400;'
        f'fill:{p["muted"]}}}'
        f'.mv{{font-family:{FONT};font-size:32px;font-weight:600;'
        f'fill:{p["ink"]}}}'
        f'.mu{{font-family:{FONT};font-size:17px;font-weight:500;'
        f'fill:{p["faint"]}}}'
        f'.ml{{font-family:{FONT};font-size:16px;font-weight:400;'
        f'fill:{p["faint"]}}}'
        f'.ln{{stroke:{p["hair"]};stroke-width:1.2}}'
        f'.dot{{fill:{p["accent"]}}}'
    )
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="LYH · 机器人控制与规划 · 从任务规划到执行器实时层">',
         f'<style>{css}</style>']
    o.append('<text class="nm" x="64" y="142">LYH</text>')
    o.append('<circle class="dot" cx="70" cy="190" r="4.4"/>')
    o.append('<text class="role" x="88" y="198">机器人控制与规划</text>')
    o.append('<text class="tag" x="64" y="248">'
             '从任务规划到执行器实时层 · 实车与整机上可复现</text>')
    for i, (num, unit, label) in enumerate(METRICS):
        x = METRIC_X[i]
        o.append(f'<text class="mv" x="{x}" y="138">{num}'
                 f'<tspan class="mu" dx="5">{unit}</tspan></text>')
        o.append(f'<text class="ml" x="{x}" y="168">{label}</text>')
    for i in range(1, len(METRICS)):
        sx = METRIC_X[i] - 26
        o.append(f'<line class="ln" x1="{sx}" y1="104" x2="{sx}" y2="176"/>')
    o.append('</svg>')
    return '\n'.join(o) + '\n'


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for kind in PALETTES:
        path = OUT / f"hero-{kind}.svg"
        path.write_text(build(kind), "utf-8")
        print(f"{path.name:18} {path.stat().st_size // 1024} KB")
