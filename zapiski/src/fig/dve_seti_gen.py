# -*- coding: utf-8 -*-
"""Рис. «Две сети и два шлюза» к записке «TRIN и NDDI», р1."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "Liberation Sans"

W, H = 17.0, 12.4
fig = plt.figure(figsize=(W / 2.54, H / 2.54), dpi=220)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

C_TR = "#e8eef8"; E_TR = "#3a5a96"
C_GW = "#f6efe0"; E_GW = "#a07020"
C_ND = "#e9f3ea"; E_ND = "#3d7a45"
MONO = "Liberation Mono"


def band(y0, y1, color, label):
    ax.add_patch(FancyBboxPatch((0.25, y0), W - 0.5, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=0.18",
                                fc=color, ec="none", alpha=0.55, zorder=0))
    ax.text(0.6, (y0 + y1) / 2, label, rotation=90, ha="center",
            va="center", fontsize=8.5, color="#333333", fontweight="bold")


def box(x, y, w, h, title, lines, ec, fc="white", tsize=9.0, lsize=7.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.2, zorder=2))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="top",
            fontsize=tsize, fontweight="bold", color=ec, zorder=3)
    ax.text(x + w / 2, y + h - 0.85, "\n".join(lines), ha="center",
            va="top", fontsize=lsize, color="#222222", linespacing=1.35,
            zorder=3)


def arrow(x0, y0, x1, y1, color="#555555", both=False, text=None,
          tx=0.0, ty=0.0, ha="left"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>",
                                color=color, lw=1.2, shrinkA=0, shrinkB=0,
                                mutation_scale=10), zorder=4)
    if text:
        ax.text((x0 + x1) / 2 + tx, (y0 + y1) / 2 + ty, text, fontsize=7,
                color=color, ha=ha, va="center", style="italic", zorder=4)


# полосы
band(8.95, 12.15, C_TR, "TRIN · имя TNOM")
band(6.15, 8.75, C_GW, "шлюз")
band(0.25, 5.95, C_ND, "NDDI · UNON · AVEC")

LX, RX, BW = 1.2, 9.25, 7.3

# сторона трансформации
box(LX, 9.25, BW, 2.6, "SRNT: информация",
    ["накапливается при жизни",
     r"карты $\mathrm{MP}_{ij}$, частные карты, записи",
     "L-, r-, t-компоненты и отношения",
     "ND операторов (пишет тренер)"], E_TR)
box(RX, 9.25, BW, 2.6, "SERN: функционал",
    ["не накапливает информацию",
     "операторы ξ, φ, ζ, τ; CNN; рефлекс",
     "линейная конструкция a-компонентов",
     "собственное имя и иконка на кубике"], E_TR)
arrow(RX, 10.45, LX + BW, 10.45, E_TR, both=True)
ax.text((LX + BW + RX) / 2, 10.7, "ND", fontsize=7.5, color=E_TR,
        ha="center", va="bottom", style="italic")

# шлюзы
box(LX, 6.45, BW, 1.9, "GATE: управление данными",
    ["логическая схема ↔ физическое хранение",
     "работает при жизни: каждое чтение и запись"], E_GW)
box(RX, 6.45, BW, 1.9, "компилятор и компоновщик",
    ["функционал → объектный код",
     "работает при порождении"], E_GW)

# сторона оборудования
box(LX, 3.45, W - LX - 0.55, 2.0, "постоянное хранилище GATE (SSD)",
    ["данные карт · ND · объектный код программ — в одной структуре",
     "файловая система переходит в GATE"], E_ND)
box(LX, 0.55, BW, 2.0, "развёртка в NVDIMM / RAM",
    ["рабочие копии данных карт и ND",
     "v-компоненты"], E_ND)
box(RX, 0.55, BW, 2.0, "загрузчик из хранилища → процесс",
    ["запуск на GATE: UPID, UNON",
     "исполнение на CPU / ПЛИС; d-компонент"], E_ND)

# стрелки по вертикали
cxL, cxR = LX + BW / 2, RX + BW / 2
arrow(cxL, 9.25, cxL, 8.35, E_GW, both=True)
arrow(cxL, 6.45, cxL, 5.45, E_GW, both=True)
arrow(cxL, 3.45, cxL, 2.55, E_ND, both=True)
arrow(cxR, 9.25, cxR, 8.35, E_GW)
arrow(cxR, 6.45, cxR, 5.45, E_GW)
arrow(cxR, 3.45, cxR, 2.55, E_ND)

for ext in ("png", "svg"):
    fig.savefig(os.path.join(HERE, "dve_seti." + ext))
print("ok")
