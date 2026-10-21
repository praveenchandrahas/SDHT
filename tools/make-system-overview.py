#!/usr/bin/env python3
"""Draws docs/img/system-overview.svg and .png: every component of the home theatre, hardware and software.
Needs matplotlib.   Usage: python3 tools/make-system-overview.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "img")
SURF, INK, INK2, GRID, BLUE, GREY, ORANGE = "#fcfcfb", "#0b0b0b", "#52514e", "#dcdbd6", "#2a78d6", "#efeeea", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
fig, ax = plt.subplots(figsize=(22, 14.2))
fig.patch.set_facecolor(SURF)
ax.set_xlim(0, 222); ax.set_ylim(-32, 142); ax.axis("off")


def box(x, y, w, h, text, hw=False, size=9, dashed=False, bold=True, ec=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.1", fc=GREY if hw else SURF,
                                ec=ec or (INK2 if hw else BLUE), lw=1.5, ls="--" if dashed else "-"))
    lines = text.split("\n")
    n = len(lines)
    for i, ln in enumerate(lines):
        ax.text(x + w / 2, y + h / 2 + (n - 1) * 1.45 - i * 2.9, ln, ha="center", va="center", fontsize=size, color=INK,
                fontweight="bold" if (i == 0 and bold) else "normal")


def container(x, y, w, h, title, color=BLUE, dashed=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.5", fc="none", ec=color, lw=1.4,
                                ls="--" if dashed else "-"))
    ax.text(x + 1.5, y + h - 2.3, title, fontsize=9.6, fontweight="bold", color=color, va="center")


def arrow(p, q, color=INK2, ls="-", lw=1.4):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


def lane(y, label):
    ax.plot([1, 221], [y, y], color=GRID, lw=1)
    ax.text(1.5, y - 1.8, label, fontsize=9.5, color=INK2, fontweight="bold", va="center")


ax.text(2, 139, "Home theatre: every component", fontsize=17, fontweight="bold", va="center")
ax.text(2, 135.4, "Blue outline = software, grey fill = hardware, dashed = optional or status to confirm. Two sources feed the W1070: the laptop and the Fire Stick. 10 x 10 ft room, Atmos 5.1.2.", fontsize=10, color=INK2, va="center")

# ---------------------------------------------------------------- source + computer
lane(130, "PLAYBACK")
box(2, 96, 20, 24, "Media library\nremuxes (Atmos,\nTrueHD, DTS-HD)\non a FUSE mount", hw=False, ec=INK2)
container(26, 36, 96, 90, "Linux laptop (Kubuntu)    planned: desktop PC")
box(30, 98, 26, 22, "mpv-atmos\nharletty-bridge decode\nOmniphony VBAP\nrender to 5.1.2")
box(61, 98, 26, 22, "PipeWire graph\ntheater-route links\nmpv to CamillaDSP\n(8 ch)")
box(91, 98, 28, 22, "CamillaDSP 4.1.3\nbass EQ preset drone2\ndelays + level trims\n(--align=bed)")
box(30, 72, 26, 20, "mpv video path\n16:9, gpu-next")
box(61, 72, 58, 20, "GPU decode and tone-mapping\nVAAPI hardware decode, libplacebo HDR tone-mapping\ntargeting 60 nits, bt.2390 / bt.1886 / bt.709")
box(30, 40, 89, 26, "Control plane (systemd user services + tools)\ncamilladsp.service  ·  theater-router.service  ·  eq on / off / toggle\nset-eq.py presets + alignment table  ·  route-mpv.sh  ·  tone-test.sh")
arrow((22, 109), (30, 109)); arrow((56, 109), (61, 109)); arrow((87, 109), (91, 109)); arrow((43, 98), (43, 92))
arrow((56, 82), (61, 82))

# ---------------------------------------------------------------- audio out
box(126, 98, 20, 22, "USB 7.1\naudio interface\n(C-Media)\n8 analog outputs", hw=True, size=8.8)
arrow((119, 109), (126, 109))
ax.plot([74, 74], [120, 127], color=ORANGE, lw=1.6, ls="--"); ax.plot([74, 136], [127, 127], color=ORANGE, lw=1.6, ls="--")
arrow((136, 127), (136, 120), color=ORANGE, ls="--", lw=1.6)
ax.text(105, 128.8, "EQ off or CamillaDSP not ready: direct route", fontsize=9, color=ORANGE, ha="center", fontweight="bold")
box(152, 106, 30, 18, "Logitech Z906\ncontrol pod + amp\nanalog 5.1 or TOSLINK in\nfixed sub level", hw=True, size=8.6)
box(152, 84, 30, 17, "Salcon Class-D amp\n(2 x 50 W, heights only)", hw=True, size=8.8)
arrow((146, 112), (152, 114)); arrow((146, 104), (152, 93))
container(186, 80, 34, 46, "Speakers", color=INK2)
for x, t in ((188, "FL"), (198, "FC"), (208, "FR")):
    box(x, 106, 9, 12, t, hw=True, size=9)
for x, t in ((188, "SL"), (198, "SR")):
    box(x, 92, 9, 12, t, hw=True, size=9)
box(208, 92, 9, 12, "Z906\nsub", hw=True, size=7.6, bold=False)
box(188, 82, 13, 8, "RL height", hw=True, size=7.8, bold=False)
box(203, 82, 14, 8, "RR height", hw=True, size=7.8, bold=False)
arrow((182, 115), (186, 115)); arrow((182, 92), (186, 87))
box(186, 70, 34, 8, "Custom JBL A1500HI sub: on hold, not in chain", hw=True, dashed=True, size=7.6, bold=False)

# ---------------------------------------------------------------- video out
box(126, 72, 20, 20, "Laptop video out\n(HDMI)", hw=True, size=9)
box(152, 56, 30, 22, "Projector (primary display)\nBenQ W1070\n1080p DLP", hw=True)
box(186, 38, 34, 28, "Screen\n107 inch DIY\n(gypsum board,\nmatte paint)", hw=True)
arrow((119, 82), (126, 82)); arrow((146, 82), (152, 70)); arrow((182, 64), (186, 56))
box(126, 38, 22, 14, "Fire Stick 4K Max\n(1st gen)", hw=True, size=8.2)
box(154, 38, 28, 14, "TD-876H\nHDMI to optical\nsplitter", hw=True, size=8.2)
arrow((148, 45), (154, 45)); arrow((168, 52), (168, 56))
ax.text(169.5, 54, "HDMI", fontsize=7.8, color=INK2, va="center")
ax.plot([182, 184], [44, 44], color=INK2, lw=1.4); ax.plot([184, 184], [44, 108], color=INK2, lw=1.4)
arrow((184, 108), (182, 108))
ax.text(182, 35.8, "TOSLINK 5.1 to Z906", fontsize=7.8, color=INK2, ha="right")

# ---------------------------------------------------------------- room and seat
lane(34, "ROOM AND MEASUREMENT")
box(126, 8, 94, 21, "Room 10 x 10 ft, no space behind the seat\nfirst-reflection panels, grey carpet, matte-black surfaces\nlistening seat opposite the centre speaker (the tuning reference)", hw=True, size=9)
box(2, 8, 28, 21, "Dayton iMM-6S\nmeasurement mic\nat the seat, ear height", hw=True, size=8.8)
box(36, 8, 30, 21, "SPACETOUCH USB\naudio adapter\n(second clock)", hw=True, size=8.8)
box(72, 8, 48, 21, "REW sweeps, rec.sh, delay test, bed test\nanalysis tools, findings to set-eq.py", size=8.8)
arrow((30, 18), (36, 18)); arrow((66, 18), (72, 18))
arrow((96, 29), (96, 40), color=BLUE, ls="--")
ax.text(98, 33.5, "recordings in, presets out", fontsize=8.4, color=BLUE, va="center")

# ---------------------------------------------------------------- other setups
container(2, -30, 218, 22, "Other setups in the house (not part of this chain)", color=INK2, dashed=True)
box(6, -28, 100, 15, "Planetarium rig (DIY)\nBorsso Crystal Edge projector -> convex acrylic mirror\n-> ceiling / walls; Stellarium", hw=True, dashed=True, size=8.4, bold=True)
box(112, -28, 100, 15, "Family rig\nToshiba 65U7980 TV, Samsung HW-Q930F soundbar,\nFire TV Cube 3", hw=True, dashed=True, size=8.4)
fig.savefig(os.path.join(OUT, "system-overview.svg"), facecolor=SURF, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "system-overview.png"), dpi=120, facecolor=SURF, bbox_inches="tight")
print("wrote system-overview.svg and .png")
