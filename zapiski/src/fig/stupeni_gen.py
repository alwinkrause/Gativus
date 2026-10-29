# -*- coding: utf-8 -*-
"""Рис. «Четыре ступени прототипа» к записке «Прототип GTRN», р1."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "Liberation Sans"
W, H = 17.0, 7.6
fig = plt.figure(figsize=(W / 2.54, H / 2.54), dpi=220)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

ST = [
    ("1", "Исполняемая\nспецификация", ["сорта, 20 операций,", "аксиомы А1–А9", "на Maude"],
     "#3a5a96", "#e8eef8"),
    ("2", "Макет\nна фон Неймане", ["сеть TRIN поверх Linux;", "карты в хранилище GATE;",
                                   "эвокация уведомлениями"], "#3d7a45", "#e9f3ea"),
    ("3", "Вехи\nи приёмка", ["ZGTR · нематода ·", "связка GTR1 и GTR2;",
                             "критерии стабильности"], "#a07020", "#f6efe0"),
    ("4", "Железо\nпо замерам", ["в ПЛИС — только", "операции, дорогие", "в переводе"],
     "#8a2b2b", "#f6e6e6"),
]
bw, bh, gap, y0 = 3.55, 3.5, 0.55, 3.75
for k, (n, t, lines, ec, fc) in enumerate(ST):
    x = 0.45 + k * (bw + gap)
    ax.add_patch(FancyBboxPatch((x, y0), bw, bh, boxstyle="round,pad=0,rounding_size=0.15",
                                fc=fc, ec=ec, lw=1.3, zorder=2))
    ax.add_patch(plt.Circle((x + 0.42, y0 + bh - 0.42), 0.26, fc=ec, ec="none", zorder=3))
    ax.text(x + 0.42, y0 + bh - 0.42, n, ha="center", va="center", color="white",
            fontsize=9, fontweight="bold", zorder=4)
    ax.text(x + 0.85, y0 + bh - 0.5, t, ha="left", va="center", color=ec, fontsize=8.0,
            fontweight="bold", zorder=4, wrap=True)
    ax.text(x + bw / 2, y0 + bh / 2 - 0.55, "\n".join(lines), ha="center", va="center",
            fontsize=7.6, color="#222222", linespacing=1.4, zorder=4)
    if k < 3:
        ax.annotate("", xy=(x + bw + gap - 0.05, y0 + bh / 2), xytext=(x + bw + 0.05, y0 + bh / 2),
                    arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.3,
                                    mutation_scale=12), zorder=5)

def back(x0, x1, y, text, c):
    ax.plot([x0, x0, x1], [y0, y, y], color=c, lw=1.1, ls="--", zorder=1)
    ax.annotate("", xy=(x1, y0), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=1.1, ls="--",
                                mutation_scale=10), zorder=1)
    ax.text((x0 + x1) / 2, y - 0.25, text, ha="center", va="top", fontsize=7.0,
            color=c, style="italic")

cx = [0.45 + k * (bw + gap) + bw / 2 for k in range(4)]
back(cx[0], cx[1] - 0.6, 2.95, "спецификация — оракул: те же сценарии,\nте же имена и карты",
     "#3a5a96")
back(cx[1] + 0.6, cx[3] + 0.6, 1.35, "замеры макета: какие операции сигнатуры\n"
     "дороже всего переводить в машину фон Неймана", "#8a2b2b")
for ext in ("png", "svg"):
    fig.savefig(os.path.join(HERE, "stupeni." + ext))
print("ok")
