#!/usr/bin/env python3
"""Draws the resource-log figures (21 to 23 in docs/graphs). The numbers are typed in from the four summary.md files of 2026-10-28/29
(Roomtone's scripts/resource-log); nothing is read from the rig, so a figure is only as good as these transcriptions. To redraw after a new
run, add its numbers to RUNS and run:  python3 tools/make-resource-graphs.py [output-directory]"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "graphs")
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = {"atmos": "#2a78d6", "dtsx": "#eb6834", "4k": "#1baf7a", "idle": "#8a8984"}      # categorical slots 1 to 3 (validated), idle neutral
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID, "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True})

# name: (label, colour key, seconds with mpv, numbers). None = not measured in that run.
RUNS = {
    "atmos": dict(label="Atmos, small file", c="atmos", secs=54, mpv=(18.8, 58.8), cdsp=(4.4, 5.8), cpu=(32.6, 39.2), ram=5979, gpu_r=None, gpu_v=None,
                  net=(0.2, 1.0), bempty=0, xruns=0, vdrop=0, avmax=0.0),
    "dtsx": dict(label="DTS:X, small file", c="dtsx", secs=47, mpv=(48.0, 62.3), cdsp=(4.9, 5.8), cpu=(39.1, 43.1), ram=5939, gpu_r=(31.1, 36.7), gpu_v=(3.1, 4.0),
                 net=(0.0, 0.1), bempty=41, xruns=0, vdrop=0, avmax=0.0),
    "4k": dict(label="4K DV remux, streamed", c="4k", secs=600, mpv=(21.7, 33.4), cdsp=(7.6, 8.8), cpu=(14.6, 27.6), ram=6562, gpu_r=(39.7, 45.1), gpu_v=(5.3, 6.5),
               net=(165.8, 469.8), bempty=116, xruns=37, vdrop=7, avmax=32.0),
}
IDLE = dict(label="Idle (nothing playing)", cpu=(29.0, 38.0), ram=5460)
NOTE = "Numbers typed in from resource-log summary.md files (2026-10-28 and 29); see docs/status.md for what they do and do not show."


def bars(ax, xs, vals, colors, fmt="{:g}", ylabel="", p95=None, ylim=None, pad=0.03):
    ax.bar(xs, vals, color=colors, width=0.62, zorder=3)
    top = max(list(vals) + (list(p95) if p95 else [0])) or 1
    for i, v in enumerate(vals):
        hi = max(v, p95[i]) if p95 and p95[i] is not None else v
        ax.text(i, hi + top * pad, fmt.format(v), ha="center", va="bottom", color=INK, fontsize=9)
    if p95:
        for i, v in enumerate(p95):
            if v is not None:
                ax.plot([i - 0.31, i + 0.31], [v, v], color=INK, lw=1.6, zorder=4)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, ylim or top * 1.25)
    ax.set_xticks(xs)


def fig_load():
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.4))
    names = ["atmos", "dtsx", "4k"]
    lab = ["Atmos\n(small file)", "DTS:X\n(small file)", "4K DV remux\n(streamed)"]
    ax = axs[0][0]
    w = 0.38
    for k, n in enumerate(names):
        r = RUNS[n]
        ax.bar(k - w / 2, r["mpv"][0], w, color=C[n], zorder=3)
        ax.bar(k + w / 2, r["cdsp"][0], w, color=C[n], alpha=0.45, zorder=3)
        ax.plot([k - w / 2 - 0.17, k - w / 2 + 0.17], [r["mpv"][1]] * 2, color=INK, lw=1.6, zorder=4)
        ax.plot([k + w / 2 - 0.17, k + w / 2 + 0.17], [r["cdsp"][1]] * 2, color=INK, lw=1.6, zorder=4)
        ax.text(k - w / 2, r["mpv"][1] + 1.8, f"{r['mpv'][0]:g}", ha="center", fontsize=9)
        ax.text(k + w / 2, r["cdsp"][1] + 1.8, f"{r['cdsp'][0]:g}", ha="center", fontsize=9)
    ax.set_xticks(range(3)); ax.set_xticklabels(lab); ax.set_ylim(0, 75)
    ax.set_ylabel("% of one core (mean; bar-end line = p95)")
    ax.set_title("mpv (solid) and CamillaDSP (faded)", loc="left", fontsize=11, color=INK)
    ax = axs[0][1]
    xs = [0, 1, 2, 3]
    vals = [IDLE["cpu"][0]] + [RUNS[n]["cpu"][0] for n in names]
    p95 = [IDLE["cpu"][1]] + [RUNS[n]["cpu"][1] for n in names]
    bars(ax, xs, vals, [C["idle"]] + [C[n] for n in names], "{:g}", "% of all threads (mean; line = p95)", p95, 55)
    ax.set_xticklabels(["Idle", "Atmos\n(small)", "DTS:X\n(small)", "4K\n(streamed)"])
    ax.set_title("Whole-computer CPU", loc="left", fontsize=11, color=INK)
    ax = axs[1][0]
    vals = [IDLE["ram"]] + [RUNS[n]["ram"] for n in names]
    bars(ax, xs, [v / 1000 for v in vals], [C["idle"]] + [C[n] for n in names], "{:.1f}", "GB in use (mean)", None, 16)
    ax.axhline(15.4, color=INK2, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(3.45, 15.55, "15.4 GiB installed", ha="right", va="bottom", color=INK2, fontsize=8.5)
    ax.set_xticklabels(["Idle", "Atmos\n(small)", "DTS:X\n(small)", "4K\n(streamed)"])
    ax.set_title("RAM in use", loc="left", fontsize=11, color=INK)
    ax = axs[1][1]
    for k, n in enumerate(["dtsx", "4k"]):
        r = RUNS[n]
        ax.bar(k - w / 2, r["gpu_r"][0], w, color=C[n], zorder=3)
        ax.bar(k + w / 2, r["gpu_v"][0], w, color=C[n], alpha=0.45, zorder=3)
        ax.plot([k - w / 2 - 0.17, k - w / 2 + 0.17], [r["gpu_r"][1]] * 2, color=INK, lw=1.6, zorder=4)
        ax.plot([k + w / 2 - 0.17, k + w / 2 + 0.17], [r["gpu_v"][1]] * 2, color=INK, lw=1.6, zorder=4)
        ax.text(k - w / 2, r["gpu_r"][1] + 1.8, f"{r['gpu_r'][0]:g}", ha="center", fontsize=9)
        ax.text(k + w / 2, r["gpu_v"][1] + 1.8, f"{r['gpu_v'][0]:g}", ha="center", fontsize=9)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["DTS:X (small)", "4K DV remux (streamed)"]); ax.set_xlim(-0.6, 1.6); ax.set_ylim(0, 65)
    ax.set_ylabel("% busy (mean; line = p95)")
    ax.set_title("GPU: Render/3D (solid) and video decode (faded)", loc="left", fontsize=11, color=INK)
    ax.text(0.5, 58, "no GPU data in the Atmos run", ha="center", color=INK2, fontsize=8.5)
    fig.suptitle("Load by run: the chain's own components are small; the 4K stream is heaviest on GPU, RAM and network, not on CPU", x=0.01, ha="left", fontsize=13, color=INK)
    fig.text(0.01, 0.005, NOTE, color=INK2, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(os.path.join(OUT, "21_resource_load_by_run.png"), dpi=140)
    plt.close(fig)


def fig_drops():
    fig, axs = plt.subplots(1, 4, figsize=(13, 4.4))
    names = ["atmos", "dtsx", "4k"]
    lab = ["Atmos\n54 s", "DTS:X\n47 s", "4K\n600 s"]
    xs = [0, 1, 2]
    cols = [C[n] for n in names]
    bars(axs[0], xs, [RUNS[n]["bempty"] for n in names], cols, "{:g}", "lines", None, 140)
    axs[0].set_title("CamillaDSP 'buffer empty'\nlines while mpv ran", loc="left", fontsize=10.5, color=INK)
    bars(axs[1], xs, [RUNS[n]["xruns"] for n in names], cols, "{:g}", "count", None, 45)
    axs[1].set_title("PipeWire xruns\n(pw-top ERR, best effort)", loc="left", fontsize=10.5, color=INK)
    bars(axs[2], xs, [RUNS[n]["vdrop"] for n in names], cols, "{:g}", "frames", None, 9)
    axs[2].set_title("mpv frames dropped by the\ndisplay path (decoder drops: 0)", loc="left", fontsize=10.5, color=INK)
    bars(axs[3], xs, [RUNS[n]["avmax"] for n in names], cols, "{:g}", "ms (max, absolute)", None, 50)
    axs[3].axhline(41.7, color=INK2, lw=1, ls=(0, (4, 3)), zorder=2)
    axs[3].text(2.45, 42.5, "one frame at 24 fps", ha="right", va="bottom", color=INK2, fontsize=8.5)
    axs[3].set_title("Audio/video sync offset\n(max)", loc="left", fontsize=10.5, color=INK)
    for ax in axs:
        ax.set_xticklabels(lab)
    fig.suptitle("Dropouts by run: the small files show no xruns or drops; the 4K stream shows the first xruns and display drops", x=0.01, ha="left", fontsize=12.5, color=INK)
    fig.text(0.01, 0.005, NOTE + "\n'Buffer empty' lines come about 21 ms apart, so 116 lines are at most 2.4 s of silence; their timing and cause are not yet checked.", color=INK2, fontsize=7.8)
    fig.tight_layout(rect=(0, 0.07, 1, 0.9))
    fig.savefig(os.path.join(OUT, "22_resource_dropouts_by_run.png"), dpi=140)
    plt.close(fig)


def fig_cost():
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axs[0]
    film = 71.3e9 * 8 / (2 * 3600 + 36 * 60 + 29) / 1e6
    vals = [film, RUNS["4k"]["net"][0], RUNS["4k"]["net"][1]]
    bars(ax, [0, 1, 2], vals, ["#8a8984", C["4k"], C["4k"]], "{:.0f}", "Mbit/s", None, 560)
    ax.set_xticklabels(["Film's own\naverage bitrate\n(71.3 GB / 2:36:29)", "Received while\nstreaming: mean", "Received while\nstreaming: p95"])
    ax.set_title("Streaming F1 from the mount (10 min)", loc="left", fontsize=11, color=INK)
    ax.text(0.0, 520, f"mean = {RUNS['4k']['net'][0] / film:.1f}x the film's\naverage rate; 10 min at\nthe mean = {RUNS['4k']['net'][0] * 600 / 8 / 1000:.1f} GB", ha="left", va="top", color=INK2, fontsize=8.8)
    ax = axs[1]
    labs = ["PyAV, one 4K remux\n(earlier measurement)", "ffmpeg command,\nsame remux", "live queue over HTTP,\nunbounded (whole\ncomputer, 2026-10-28)", "F1 built via the mount\n(whole computer,\n2026-10-29)"]
    v = [9.8, 62.7, 65, 211.0]
    bars(ax, [0, 1, 2, 3], v, ["#8a8984", "#8a8984", "#8a8984", C["4k"]], "{:g}", "MB received per thumbnail", None, 250)
    ax.set_xticklabels(labs, fontsize=8.5)
    ax.axhline(3.27 / 469 * 1000 / 1000, color=INK2, lw=0)       # the thumbnails themselves (3.27 MB for 469) are 0.007 MB each: not drawable
    ax.set_title("Reading cost per thumbnail (not like-for-like)", loc="left", fontsize=11, color=INK)
    ax.text(-0.4, 240, "for scale, the stored thumbnail itself is 0.007 MB", ha="left", va="top", color=INK2, fontsize=8.5)
    fig.suptitle("What the data costs: streaming and thumbnail building both move far more than the content needs", x=0.01, ha="left", fontsize=12.5, color=INK)
    fig.text(0.01, 0.005, NOTE + "\nThe four right-hand bars were measured in different ways (see the seekthumbs README); only the last is a full film.", color=INK2, fontsize=7.8)
    fig.tight_layout(rect=(0, 0.07, 1, 0.92))
    fig.savefig(os.path.join(OUT, "23_stream_and_thumbnail_cost.png"), dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig_load()
    fig_drops()
    fig_cost()
    print("wrote 21, 22, 23 to", os.path.abspath(OUT))
