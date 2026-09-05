# -*- coding: utf-8 -*-
"""生成《差速器 / 传动 / 悬挂 基本结构》PDF 说明书。

用法:  python tools/make_mech_guide.py
产物:  docs/team/机械结构说明书.pdf
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
F = "STSong-Light"

W, H = A4
M = 18 * mm                      # 页边距
INK = (0.12, 0.12, 0.14)
GREY = (0.45, 0.45, 0.48)
ACC = (0.85, 0.35, 0.15)         # 强调橙
BLUE = (0.15, 0.40, 0.70)
LIGHT = (0.90, 0.90, 0.92)


class Page:
    def __init__(self, c, title, subtitle=""):
        self.c = c
        self.y = H - M
        c.setFillColorRGB(*INK)
        c.setFont(F, 19)
        c.drawString(M, self.y, title)
        self.y -= 7 * mm
        if subtitle:
            c.setFillColorRGB(*GREY)
            c.setFont(F, 9.5)
            c.drawString(M, self.y, subtitle)
            self.y -= 5 * mm
        c.setStrokeColorRGB(*ACC)
        c.setLineWidth(1.6)
        c.line(M, self.y, W - M, self.y)
        self.y -= 8 * mm

    def h2(self, t):
        self.y -= 2 * mm
        self.c.setFillColorRGB(*ACC)
        self.c.setFont(F, 12.5)
        self.c.drawString(M, self.y, t)
        self.y -= 6.5 * mm

    def p(self, t, size=10, gap=5.4, color=INK, indent=0):
        self.c.setFillColorRGB(*color)
        self.c.setFont(F, size)
        self.c.drawString(M + indent, self.y, t)
        self.y -= gap * mm

    def bullet(self, t, size=10):
        self.c.setFillColorRGB(*ACC)
        self.c.setFont(F, size)
        self.c.drawString(M + 1 * mm, self.y, "·")
        self.c.setFillColorRGB(*INK)
        self.c.drawString(M + 5 * mm, self.y, t)
        self.y -= 5.4 * mm

    def note(self, t, size=9.5):
        self.c.setFillColorRGB(*BLUE)
        self.c.setFont(F, size)
        self.c.drawString(M + 1 * mm, self.y, t)
        self.y -= 5.2 * mm

    def gap(self, mm_):
        self.y -= mm_ * mm


def box(c, x, y, w, h, label, sub="", fill=None, fs=9):
    if fill:
        c.setFillColorRGB(*fill)
        c.roundRect(x, y, w, h, 2 * mm, stroke=0, fill=1)
    c.setStrokeColorRGB(*INK)
    c.setLineWidth(0.9)
    c.roundRect(x, y, w, h, 2 * mm, stroke=1, fill=0)
    c.setFillColorRGB(*INK)
    c.setFont(F, fs)
    if sub:
        c.drawCentredString(x + w / 2, y + h / 2 + 1.2 * mm, label)
        c.setFillColorRGB(*GREY)
        c.setFont(F, fs - 1.5)
        c.drawCentredString(x + w / 2, y + h / 2 - 3.2 * mm, sub)
    else:
        c.drawCentredString(x + w / 2, y + h / 2 - 1.2 * mm, label)


def arrow(c, x1, y1, x2, y2, label="", color=INK):
    c.setStrokeColorRGB(*color)
    c.setFillColorRGB(*color)
    c.setLineWidth(1.1)
    c.line(x1, y1, x2, y2)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    s = 2.2 * mm
    c.line(x2, y2, x2 - s * math.cos(a - 0.4), y2 - s * math.sin(a - 0.4))
    c.line(x2, y2, x2 - s * math.cos(a + 0.4), y2 - s * math.sin(a + 0.4))
    if label:
        c.setFont(F, 8)
        c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 1.5 * mm, label)


def spring(c, x, y_top, y_bot, w=4 * mm, coils=7):
    """画一个弹簧(竖直方向的之字线)"""
    c.setStrokeColorRGB(*INK)
    c.setLineWidth(1.0)
    n = coils * 2
    step = (y_top - y_bot) / n
    px, py = x, y_top
    for i in range(1, n + 1):
        nx = x + (w / 2 if i % 2 else -w / 2)
        ny = y_top - step * i
        c.line(px, py, nx, ny)
        px, py = nx, ny
    c.line(px, py, x, y_bot)


# ============================================================== 生成
os.makedirs("docs/team", exist_ok=True)
OUT = "docs/team/机械结构说明书.pdf"
c = canvas.Canvas(OUT, pagesize=A4)

# -------------------------------------------------- P1 动力链路总览
p = Page(c, "整车动力链路", "从电机到车轮，动力怎么一步步传过去")

p.p("先建立整体印象。你手上的所有传动件，都是下面这条链路上的一环：")
p.gap(3)

y0 = p.y - 26 * mm
bw, bh = 30 * mm, 16 * mm
xs = M
box(c, xs, y0, bw, bh, "电机", "13000rpm", fill=LIGHT)
arrow(c, xs + bw, y0 + bh / 2, xs + bw + 8 * mm, y0 + bh / 2)
xs2 = xs + bw + 8 * mm
box(c, xs2, y0, 24 * mm, bh, "8T 小齿", "装电机轴")
arrow(c, xs2 + 24 * mm, y0 + bh / 2, xs2 + 24 * mm + 8 * mm, y0 + bh / 2, "啮合")
xs3 = xs2 + 24 * mm + 8 * mm
box(c, xs3, y0, 34 * mm, bh, "差速器", "29T 盘齿", fill=LIGHT)
arrow(c, xs3 + 34 * mm, y0 + bh / 2, xs3 + 34 * mm + 8 * mm, y0 + bh / 2)
xs4 = xs3 + 34 * mm + 8 * mm
box(c, xs4, y0, 30 * mm, bh, "万向节", "传动轴 x2")
arrow(c, xs4 + 30 * mm, y0 + bh / 2, xs4 + 30 * mm + 8 * mm, y0 + bh / 2)
box(c, xs4 + 38 * mm, y0, 20 * mm, bh, "车轮", "Ø28.14", fill=LIGHT)

p.y = y0 - 10 * mm
p.p("传动比 = 29 / 8 = 3.625     极速约 5.3 m/s (19 km/h)", size=10.5, color=BLUE)
p.p("电机小齿与差速器盘齿的中心距 = 0.5 x (8 + 29) / 2 = 9.25 mm", size=10.5, color=BLUE)
p.gap(3)

p.h2("三个子系统各管什么")
p.bullet("差速器 —— 让左右轮在过弯时能有不同转速，否则内侧轮必然拖地打滑")
p.bullet("传动机制 —— 把电机的高转速低扭矩，换成车轮要的低转速高扭矩")
p.bullet("悬挂 —— 在颠簸和过弯时把轮胎按在地面上，没有抓地力一切都是空谈")
p.gap(4)

p.h2("一句话记住它们的关系")
p.p("传动决定“跑多快”，差速决定“弯里顺不顺”，悬挂决定“力能不能真的传到地上”。")
p.gap(5)

p.h2("怎么用这份文档")
p.bullet("第 2~4 页各讲一个子系统：原理 -> 结构图 -> 装配要点")
p.bullet("第 5 页是零件对照表和装配顺序，动手时照着走")
p.bullet("图是示意图，不是装配图 —— 具体件的细节以实物和驻场导师为准")
p.gap(5)

p.h2("已经定下来的参数")
p.p("车轮直径 28.14 mm        差速器盘齿 29T (待数齿确认)")
p.p("电机小齿 8T              传动比 3.625        中心距 9.25 mm")
p.p("齿轮模数 m = 0.5         电机 13000 rpm / 28 g·cm")
p.gap(4)
p.note("传动比一旦改动，车速、加速度和电控里的 COUNTS_PER_METER 都要跟着重算。")

c.showPage()

# -------------------------------------------------- P2 差速器
p = Page(c, "一、差速器", "你手上这个是成品总成，不用拆装")

p.h2("为什么需要它")
p.p("过弯时，外侧轮走的弧线比内侧长，所以外侧必须转得更快。")
p.p("如果左右轮硬连在一根轴上，过弯时一定有一个轮在地上蹭 —— 既慢又容易失控。")
p.gap(2)

p.h2("内部结构")

# 差速器剖面示意图
cx = W / 2
cy = p.y - 34 * mm
hw, hh = 30 * mm, 20 * mm
c.setStrokeColorRGB(*INK); c.setLineWidth(1.2)
c.roundRect(cx - hw, cy - hh, hw * 2, hh * 2, 3 * mm, stroke=1, fill=0)
# 盘齿(外圈锯齿示意)
c.setStrokeColorRGB(*ACC); c.setLineWidth(2.0)
c.line(cx - hw, cy + hh, cx + hw, cy + hh)
c.line(cx - hw, cy - hh, cx + hw, cy - hh)
c.setFillColorRGB(*ACC); c.setFont(F, 8.5)
c.drawCentredString(cx, cy + hh + 3 * mm, "盘齿(29T) — 电机的动力从这里进来")
# 半轴齿轮 (左右两个三角形)
c.setStrokeColorRGB(*INK); c.setLineWidth(1.0)
for sgn in (-1, 1):
    x = cx + sgn * 15 * mm
    c.setFillColorRGB(0.80, 0.85, 0.92)
    pth = c.beginPath()
    pth.moveTo(x + sgn * 6 * mm, cy + 9 * mm)
    pth.lineTo(x + sgn * 6 * mm, cy - 9 * mm)
    pth.lineTo(x - sgn * 2 * mm, cy)
    pth.close()
    c.drawPath(pth, stroke=1, fill=1)
# 行星齿轮 (中间上下两个小三角)
for sgn in (-1, 1):
    y = cy + sgn * 10 * mm
    c.setFillColorRGB(0.95, 0.85, 0.75)
    pth = c.beginPath()
    pth.moveTo(cx - 5 * mm, y + sgn * 4 * mm)
    pth.lineTo(cx + 5 * mm, y + sgn * 4 * mm)
    pth.lineTo(cx, y - sgn * 3 * mm)
    pth.close()
    c.drawPath(pth, stroke=1, fill=1)
# 十字轴
c.setStrokeColorRGB(*INK); c.setLineWidth(1.6)
c.line(cx, cy - 15 * mm, cx, cy + 15 * mm)
# 输出轴
c.setLineWidth(2.2)
c.line(cx - hw - 14 * mm, cy, cx - 15 * mm, cy)
c.line(cx + 15 * mm, cy, cx + hw + 14 * mm, cy)
c.setFillColorRGB(*INK); c.setFont(F, 8)
c.drawRightString(cx - hw - 2 * mm, cy - 8 * mm, "左输出")
c.drawString(cx + hw + 2 * mm, cy - 8 * mm, "右输出")

# 图例放在图下方, 避免标签压在齿轮上
ly = cy - hh - 8 * mm
c.setFont(F, 8)
lx = cx - 62 * mm
for color, mark, text in (
    ((0.95, 0.85, 0.75), "▲", "行星齿轮 — 跟壳体公转, 过弯时才自转"),
    ((0.80, 0.85, 0.92), "◀", "半轴齿轮 — 接左右输出"),
    (None, "│", "十字轴 — 行星齿轮套在它上面"),
):
    c.setFillColorRGB(*(color if color else INK))
    c.drawString(lx, ly, mark)
    c.setFillColorRGB(*GREY)
    c.drawString(lx + 5 * mm, ly, text)
    ly -= 4.6 * mm

p.y = ly - 5 * mm
p.h2("它是怎么工作的")
p.bullet("直线跑：左右阻力相同 → 行星齿轮不自转，只跟着壳体公转 → 左右同速")
p.bullet("过弯时：一侧阻力大 → 行星齿轮开始自转 → 一侧减速，另一侧同等加速")
p.gap(2)
p.note("关键性质：左右轮的转速之和恒等于壳体转速的两倍。所以只要一侧悬空，")
p.note("动力就会全跑到那一侧 —— 这是开放式差速器的固有缺点，起步别急给油。")
p.gap(3)

p.h2("装到车上要注意")
p.bullet("两端的轴承坐进底盘的轴承座，必须同轴，歪了会异响和卡滞")
p.bullet("盘齿与电机小齿的中心距 9.25mm，误差控制在 ±0.05mm")
p.bullet("啮合不能太紧(卡死、烧电机)也不能太松(打齿)，装好用手转应顺滑无卡点")

c.showPage()

# -------------------------------------------------- P3 传动
p = Page(c, "二、传动机制", "减速齿轮组 + 万向节传动轴")

p.h2("为什么要减速")
p.p("电机转速 13000rpm、扭矩只有 28 g·cm —— 转得飞快但没力气。")
p.p("直接接轮子的话，车会以 70+ km/h 的理论速度起步，而实际扭矩根本推不动。")
p.p("齿轮减速就是拿转速换扭矩：转速降到 1/3.625，扭矩放大 3.625 倍。")
p.gap(3)

p.h2("模数与中心距 — 建模打孔必须用这两条公式")
p.p("分度圆直径  d = m x z          (m = 模数 = 0.5，z = 齿数)", size=10.5, color=BLUE)
p.p("中心距      a = m x (z1 + z2) / 2", size=10.5, color=BLUE)
p.gap(1)
p.note("注意：卡尺量到的是齿顶圆 d顶 = m(z+2)，不是分度圆。两者差 2 个齿，")
p.note("折算到中心距是 0.5mm 误差 —— 足以让齿轮卡死或打齿。要数齿数核对。")
p.gap(4)

p.h2("万向节传动轴 — 为什么不能用一根直轴")
yj = p.y - 22 * mm
c.setStrokeColorRGB(*INK); c.setLineWidth(1.2)
# 差速器输出
box(c, M, yj - 5 * mm, 22 * mm, 12 * mm, "差速器", fs=8.5, fill=LIGHT)
# 轴 + 两个球头
x1 = M + 22 * mm
x2 = x1 + 46 * mm
c.setLineWidth(2.4)
c.line(x1 + 4 * mm, yj + 1 * mm, x2 - 4 * mm, yj + 1 * mm)
c.setFillColorRGB(*ACC)
c.circle(x1 + 4 * mm, yj + 1 * mm, 2.6 * mm, stroke=1, fill=1)
c.circle(x2 - 4 * mm, yj + 1 * mm, 2.6 * mm, stroke=1, fill=1)
box(c, x2, yj - 5 * mm, 22 * mm, 12 * mm, "轮轴", fs=8.5, fill=LIGHT)
# 摆动示意
c.setStrokeColorRGB(*GREY); c.setLineWidth(0.8); c.setDash(2, 2)
c.line(x2 - 4 * mm, yj + 1 * mm, x2 - 4 * mm + 14 * mm, yj + 10 * mm)
c.line(x2 - 4 * mm, yj + 1 * mm, x2 - 4 * mm + 14 * mm, yj - 8 * mm)
c.setDash()
c.setFillColorRGB(*GREY); c.setFont(F, 8)
c.drawString(x2 + 26 * mm, yj + 6 * mm, "悬挂上下运动时")
c.drawString(x2 + 26 * mm, yj + 1 * mm, "这两端可以摆动")
c.setFillColorRGB(*ACC); c.setFont(F, 8)
c.drawCentredString((x1 + x2) / 2, yj + 6 * mm, "球头 / 万向节")

p.y = yj - 14 * mm
p.bullet("车轮装在悬挂上，会相对车身上下运动；差速器固定在底盘上，不动")
p.bullet("两者之间的距离和角度一直在变，直轴会别死 —— 所以要用带球头的万向节")
p.bullet("你手上那两根带球头的金属组件就是它，左右各一根")
p.gap(3)

p.h2("装配要点")
p.bullet("球头两端都要能自由摆动，装好后手动上下扳一扳确认不卡")
p.bullet("传动轴长度要与悬挂行程匹配：压缩到底和完全伸展时都不能脱出或顶死")
p.bullet("这是全车受力最大的零件之一，装配后每天检查一次有没有旷量变大")

c.showPage()

# -------------------------------------------------- P4 悬挂
p = Page(c, "三、悬挂", "导向轴 + 弹簧 = 滑柱式悬挂")

p.h2("它要解决什么")
p.p("赛道有起伏。轮子一旦离地，抓地力归零 —— 动力、刹车、转向全部失效。")
p.p("悬挂的唯一任务：不管路面怎么颠，把四个轮子始终按在地上。")
p.gap(3)

p.h2("你手上这套是最简单也最可靠的一种")

sy = p.y - 8 * mm
# 底盘
c.setStrokeColorRGB(*INK); c.setLineWidth(1.6)
c.line(M + 20 * mm, sy, M + 90 * mm, sy)
c.setFillColorRGB(*GREY); c.setFont(F, 8.5)
c.drawString(M + 92 * mm, sy - 1 * mm, "底盘 (固定)")
# 导向轴
gx = M + 45 * mm
c.setStrokeColorRGB(*INK); c.setLineWidth(2.0)
c.line(gx, sy, gx, sy - 42 * mm)
c.setFillColorRGB(*ACC); c.setFont(F, 8.5)
c.drawString(gx + 3 * mm, sy - 8 * mm, "导向轴")
# 弹簧
spring(c, gx + 16 * mm, sy, sy - 30 * mm, w=7 * mm, coils=6)
c.setFillColorRGB(*ACC)
c.drawString(gx + 22 * mm, sy - 16 * mm, "弹簧")
# 轮毂座
c.setStrokeColorRGB(*INK); c.setLineWidth(1.0)
c.setFillColorRGB(0.88, 0.90, 0.94)
c.roundRect(gx - 9 * mm, sy - 38 * mm, 30 * mm, 9 * mm, 1.5 * mm, stroke=1, fill=1)
c.setFillColorRGB(*INK); c.setFont(F, 8)
c.drawCentredString(gx + 6 * mm, sy - 35 * mm, "轮毂座")
# 轮轴
c.setLineWidth(1.6)
c.line(gx - 17 * mm, sy - 33.5 * mm, gx - 9 * mm, sy - 33.5 * mm)
# 轮子 (往左挪开, 不与轮毂座文字重叠)
c.setFillColorRGB(0.75, 0.75, 0.78)
c.circle(gx - 26 * mm, sy - 33.5 * mm, 9 * mm, stroke=1, fill=1)
c.setFillColorRGB(*INK); c.setFont(F, 8)
c.drawCentredString(gx - 26 * mm, sy - 35 * mm, "车轮")
# 行程箭头
arrow(c, gx + 27 * mm, sy - 33 * mm, gx + 27 * mm, sy - 24 * mm, color=BLUE)
arrow(c, gx + 27 * mm, sy - 24 * mm, gx + 27 * mm, sy - 33 * mm, color=BLUE)
c.setFillColorRGB(*BLUE); c.setFont(F, 8)
c.drawString(gx + 30 * mm, sy - 29 * mm, "悬挂行程")

p.y = sy - 52 * mm
p.h2("工作方式")
p.bullet("轮毂座套在导向轴上，只能沿轴上下滑动，不会前后左右晃")
p.bullet("弹簧被压缩后产生回弹力，把轮子往地面推")
p.bullet("路面凸起 → 轮子上抬压缩弹簧；路面凹陷 → 弹簧伸展把轮子推下去")
p.gap(3)

p.h2("三个要调的参数")
p.bullet("行程 —— 上下能走多远。太小容易触底，太大车身会晃、重心转移过多")
p.bullet("预压 —— 装配时弹簧已被压缩的量。预压越大悬挂越硬、响应越快但越颠")
p.bullet("刚度 —— 弹簧本身的软硬。前后可以配不同刚度来调转向特性")
p.gap(2)
p.note("经验起点：静止时悬挂压缩掉总行程的 1/4 到 1/3，剩下的留给路面起伏。")
p.note("完全压不动 = 太硬(等于没悬挂)；一放上去就压到底 = 太软(过弯会触底)。")
p.gap(3)

p.h2("装配要点")
p.bullet("导向轴必须垂直于底盘，歪了会卡滞甚至完全动不了")
p.bullet("装好后用手压轮子，应能顺滑上下且自己弹回原位，无卡点、无异响")
p.bullet("左右两侧的预压必须一致，否则车会自动往一边跑")

c.showPage()

# -------------------------------------------------- P5 清单与顺序
p = Page(c, "四、零件对照与装配顺序", "把手上的件对上号")

p.h2("零件用途对照")
rows = [
    ("差速器总成 (含轴承)", "1", "后桥核心，成品，不用拆"),
    ("万向节传动轴", "2", "差速器 -> 左右轮"),
    ("大齿轮 / 小齿轮", "若干", "减速齿轮组，本方案只用 8T + 差速器盘齿"),
    ("轴承", "~8", "差速器 2、轮轴 4、其余备用"),
    ("弹簧", "~6", "悬挂，每轮一根"),
    ("直金属轴", "~8", "导向轴(悬挂) / 轮轴"),
    ("球头螺柱", "~6", "转向拉杆、悬挂连杆"),
]
c.setFont(F, 9)
for name, qty, use in rows:
    c.setFillColorRGB(*INK)
    c.drawString(M, p.y, name)
    c.setFillColorRGB(*ACC)
    c.drawString(M + 52 * mm, p.y, qty)
    c.setFillColorRGB(*GREY)
    c.drawString(M + 66 * mm, p.y, use)
    p.y -= 5.6 * mm
p.gap(3)

p.h2("建议装配顺序")
steps = [
    "差速器压进底盘轴承座 —— 先确认两个座同轴",
    "装电机 + 8T 小齿 —— 调整到与盘齿啮合顺滑，中心距 9.25mm",
    "装悬挂：导向轴穿轮毂座，套弹簧，两侧预压对称",
    "装万向节传动轴 —— 连接差速器与轮轴，上下扳动确认不卡",
    "装转向：舵机 + 球头拉杆，确认左右打角对称",
    "整车手动推行一圈 —— 无卡滞、无异响才能上电",
]
for i, s in enumerate(steps, 1):
    c.setFillColorRGB(*ACC); c.setFont(F, 10)
    c.drawString(M, p.y, f"{i}.")
    c.setFillColorRGB(*INK)
    c.drawString(M + 6 * mm, p.y, s)
    p.y -= 6.0 * mm
p.gap(3)

p.h2("上电前最后检查 (PPT 强制要求)")
p.bullet("用手转动传动系统一整圈，确认没有任何机械卡死")
p.bullet("电池正负极正确，板上无锡球、无导体杂质")
p.bullet("万用表测电源对地不短路")
p.gap(4)

c.setFillColorRGB(*GREY)
c.setFont(F, 8.5)
c.drawString(M, M, "本文档为通用结构说明，具体件的装配细节以驻场导师和实物为准。")

c.showPage()
c.save()
print("已生成:", OUT, os.path.getsize(OUT), "bytes")
