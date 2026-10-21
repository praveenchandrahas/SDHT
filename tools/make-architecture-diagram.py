#!/usr/bin/env python3
"""Draws docs/img/architecture.svg and .png. Needs matplotlib.   Usage: python3 tools/make-architecture-diagram.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "img")
SURF, INK, INK2, GRID, BLUE, GREY, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#dcdbd6", "#2a78d6", "#efeeea", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})

fig, ax = plt.subplots(figsize=(18, 11.4))
fig.patch.set_facecolor(SURF)
ax.set_xlim(0, 180); ax.set_ylim(-2, 116); ax.axis("off")


def box(x, y, w, h, text, hw=False, size=9.2, bold_first=True, lw=1.6, ec=BLUE, fc=None, dashed=False):
    fc = fc or (GREY if hw else SURF)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=fc,
                                ec=INK2 if hw else ec, lw=lw, ls="--" if dashed else "-"))
    lines = text.split("\n")
    n = len(lines)
    for i, ln in enumerate(lines):
        yy = y + h / 2 + (n - 1) * 1.5 - i * 3.0
        ax.text(x + w / 2, yy, ln, ha="center", va="center", fontsize=size, color=INK,
                fontweight="bold" if (i == 0 and bold_first) else "normal")


def container(x, y, w, h, title):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.5", fc="none", ec=BLUE, lw=1.4))
    ax.text(x + 1.5, y + h - 2.2, title, fontsize=9.4, fontweight="bold", color=BLUE, va="center")


def arrow(p, q, color=INK2, ls="-", lw=1.4, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def lane(y, label):
    ax.plot([1, 179], [y, y], color=GRID, lw=1)
    ax.text(1.5, y - 1.8, label, fontsize=9.5, color=INK2, fontweight="bold", va="center")


ax.text(2, 113, "Software-defined home theatre: signal path, control plane and measurement loop", fontsize=16, fontweight="bold", va="center")
ax.text(2, 109.6, "Linux, Atmos 5.1.2 (bed + 2 heights) in a 10 x 10 ft room. Blue outline = software, grey fill = hardware.", fontsize=10, color=INK2, va="center")

# ------------------------------------------------------------ audio path
lane(103, "AUDIO PATH")
box(2, 66, 17, 20, "Media library\nremuxes on a\nFUSE mount", hw=False, ec=INK2)
container(23, 58, 44, 38, "mpv-atmos  (mpv-omniphony 0.4.2)")
box(25, 62, 18, 24, "harletty-bridge\nTrueHD / E-AC-3\nAtmos decode\n(objects + bed)")
box(47, 62, 18, 24, "Omniphony\nVBAP renderer\n5.1.2 -> 8 ch PCM\nlayout FL FR RL RR\nFC LFE SL SR")
box(71, 66, 16, 20, "PipeWire\nnode  mpv\n8 ports\nFL .. SR")
container(91, 52, 40, 46, "CamillaDSP 4.1.3  (camilladsp.service)")
box(93, 82, 36, 9, "camilladsp-capture   input_1 .. 8", size=8.6)
box(93, 68, 36, 11, "Bass EQ  (preset drone2)\non FL FR FC LFE SL SR", size=8.6)
box(93, 57, 36, 9.5, "Delays + level trims  (--align=bed)", size=8.6)
ax.text(111, 54.2, "camilladsp-playback  output_1 .. 8", fontsize=8.4, ha="center", va="center", color=INK2)
box(136, 66, 14, 20, "USB 7.1\ninterface\n(C-Media)\n8 outputs", hw=True, size=8.8)
box(154, 76, 25, 17, "Logitech Z906\nFL FR FC SL SR\n+ LFE -> sub", hw=True)
box(154, 56, 25, 17, "Height amp\nRL, RR ->\n2 height speakers", hw=True)
for p, q in (((19, 76), (23, 76)), ((43, 74), (47, 74)), ((67, 76), (71, 76)), ((87, 76), (91, 76)), ((131, 76), (136, 76)),
             ((150, 80), (154, 84)), ((150, 72), (154, 64))):
    arrow(p, q)
# bypass over the top
ax.plot([79, 79], [86, 100], color=ORANGE, lw=1.6, ls="--")
ax.plot([79, 143], [100, 100], color=ORANGE, lw=1.6, ls="--")
arrow((143, 100), (143, 86), color=ORANGE, ls="--", lw=1.6)
ax.text(111, 101.8, "EQ off, or CamillaDSP not ready: direct links mpv -> USB (no EQ, no delays)", fontsize=9, color=ORANGE, ha="center", va="center", fontweight="bold")

# ------------------------------------------------------------ control plane
lane(46, "CONTROL PLANE")
box(4, 22, 34, 18, "eq  on | off | toggle | status\nstate file\n~/.local/state/theater/eq")
box(46, 22, 54, 18, "theater-route daemon  (theater-router.service)\npolls PipeWire every 0.5 s\nlinks mpv -> CamillaDSP -> USB, make-before-break\nfalls back to direct if CamillaDSP is not ready", size=8.8)
box(108, 22, 52, 18, "set-eq.py  (presets, ALIGN table, --invert)\nwrites ~/.config/camilladsp/config.yml\nrestarts camilladsp.service, relinks", size=8.8)
arrow((38, 31), (46, 31))
arrow((79, 40), (79, 66), color=BLUE, ls="--")          # router -> PipeWire graph
ax.text(81, 53, "pw-link", fontsize=8.6, color=BLUE, va="center")
arrow((120, 40), (120, 52), color=BLUE, ls="--")         # set-eq -> CamillaDSP
ax.text(122, 46.4, "config + restart", fontsize=8.6, color=BLUE, va="center")

# ------------------------------------------------------------ measurement
lane(15, "MEASUREMENT LOOP")
box(4, -1, 30, 13, "Listening seat\nopposite the centre\nDayton iMM-6S mic", hw=True)
box(42, -1, 38, 13, "Second USB audio device\nrec.sh  (pw-record) or REW\nsweeps, chirps, bed test", size=8.8)
box(88, -1, 40, 13, "Analysis  (tools/)\ndelay test, level and polarity\nchecks, filter fitting", size=8.8)
box(136, -1, 42, 13, "Decisions\nfilter sets + ALIGN table\ncommitted into set-eq.py", size=8.8)
for p, q in (((34, 5.5), (42, 5.5)), ((80, 5.5), (88, 5.5)), ((128, 5.5), (136, 5.5))):
    arrow(p, q)
arrow((150, 12), (140, 22), color=BLUE, ls="--")
fig.savefig(os.path.join(OUT, "architecture.svg"), facecolor=SURF, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "architecture.png"), dpi=130, facecolor=SURF, bbox_inches="tight")
print("wrote architecture.svg and architecture.png")
