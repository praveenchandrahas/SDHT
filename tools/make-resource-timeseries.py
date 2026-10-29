#!/usr/bin/env python3
"""Figures 24 to 27: four runs of 2026-10-29 over time, drawn from the slimmed run data in docs/data (samples and the CamillaDSP buffer-empty times).
Run start is taken from environment.txt (09:58:41, 10:44:33, 12:38:33 and 12:46:12), so event times are good to about 1 s.
Usage: python3 tools/make-resource-timeseries.py [output-directory]"""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "docs", "graphs")
D = os.path.join(HERE, "..", "docs", "data")
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID, "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True})

RUNS = [
    dict(stem="resource-log-20261029-4k", start=(9, 58, 41), file="24_4k_run_over_time.png", figsize=(11, 8.6), until=None, since=0.0, rows_until=None, zero=(),
         title="4K remux streamed from the mount, 600 s: 116 buffer-empty lines (green) against load",
         panels=[("net_rx_mbps", "Network in\n(Mbit/s)", "area", BLUE), ("mpv_cpu_pct", "mpv CPU\n(% of one core)", "line", ORANGE),
                 ("psi_io_pct", "I/O pressure\n(PSI %)", "line", GREY), ("pw_err_sum", "PipeWire xruns\n(cumulative)", "step", INK)]),
    dict(stem="resource-log-20261029-hover", start=(10, 44, 33), file="25_hover_run_over_time.png", figsize=(11, 8.6), until=121.0, since=0.0, rows_until=None, zero=(),
         title="Same stream, 2 minutes: quiet for 110 s, then mpv at up to 100 % CPU, dropped frames and xruns (seek-bar hovering, per the owner)",
         panels=[("net_rx_mbps", "Network in\n(Mbit/s)", "area", BLUE), ("mpv_cpu_pct", "mpv CPU\n(% of one core)", "line", ORANGE),
                 ("mpv_drops", "mpv frames dropped\n(cumulative)", "step", INK), ("pw_err_sum", "PipeWire xruns\n(cumulative)", "step", INK)]),
    dict(stem="resource-log-20261029-hover2", start=(12, 38, 33), file="26_hover2_run_over_time.png", figsize=(11, 8.6), until=65.0, since=2.0, rows_until=64.0, zero=(),
         title="Second hover test (viewer change possibly not installed): clean 35 s, then mpv at 100 to 140 % CPU, 80 drops, 241 xruns",
         panels=[("net_rx_mbps", "Network in\n(Mbit/s)", "area", BLUE), ("mpv_cpu_pct", "mpv CPU\n(% of one core)", "line", ORANGE),
                 ("mpv_drops", "mpv frames dropped\n(cumulative)", "step", INK), ("pw_err_sum", "PipeWire xruns\n(cumulative)", "step", INK)]),
]


RUNS.append(dict(stem="resource-log-20261029-hover3", start=(12, 46, 12), file="27_hover3_run_over_time.png", figsize=(11, 8.6), until=50.2, since=0.0, rows_until=50.1,
                 zero=("pw_err_sum", "mpv_drops"),
                 title="Third hover test (viewer installed): clean for 33 s, then mpv at 65 to 102 % CPU, 14 drops, 58 xruns",
                 panels=[("net_rx_mbps", "Network in\n(Mbit/s)", "area", BLUE), ("mpv_cpu_pct", "mpv CPU\n(% of one core)", "line", ORANGE),
                         ("mpv_drops", "mpv frames dropped\n(since the start)", "step", INK), ("pw_err_sum", "PipeWire xruns\n(since the start)", "step", INK)]))

RUNS.append(dict(stem="resource-log-20261029-hoverA", start=(18, 59, 9), file="28_hoverA_run_over_time.png", figsize=(11, 8.6), until=60.7, since=0.0, rows_until=60.7,
                 zero=("pw_err_sum", "mpv_drops"),
                 title="Run A (viewer with the throttle): the hover (18 to 53 s) has 110 audio dropouts, 21 dropped frames, 140 xruns; the 17 s before and 7 s after have none",
                 panels=[("mpv_cpu_pct", "mpv CPU\n(% of one core)", "line", ORANGE), ("sys_cpu_pct", "Whole computer CPU\n(% of 8 threads)", "line", BLUE),
                         ("mpv_drops", "mpv frames dropped\n(since the start)", "step", INK), ("pw_err_sum", "PipeWire xruns\n(since the start)", "step", INK)]))


def draw(run):
    rows = list(csv.DictReader(open(os.path.join(D, run["stem"] + "-samples.csv"))))
    if run["rows_until"] is not None:                              # the xrun total falls when a node disappears after mpv closes: leave that out
        rows = [r for r in rows if float(r["t_s"]) <= run["rows_until"]]
    h0, m0, s0 = run["start"]
    ev = []
    for s in open(os.path.join(D, run["stem"] + "-buffer-empty-times.txt")).read().split():
        h, m, sec = s.split(":")
        t = int(h) * 3600 + int(m) * 60 + float(sec) - (h0 * 3600 + m0 * 60 + s0)
        if t >= run["since"] and (run["until"] is None or t <= run["until"]):           # lines before the audio started and after mpv stopped are the idle ones
            ev.append(t)
    fig, axs = plt.subplots(len(run["panels"]), 1, figsize=run["figsize"], sharex=True, gridspec_kw={"height_ratios": [2, 1.4, 1.4, 1.4]})
    for ax, (col, label, kind, colour) in zip(axs, run["panels"]):
        pts = [(float(r["t_s"]), float(r[col])) for r in rows if r[col] != ""]
        if col in run["zero"] and pts:                        # counters that were already running when the log started
            pts = [(a, b - pts[0][1]) for a, b in pts]
        t, v = [p[0] for p in pts], [p[1] for p in pts]
        if kind == "area":
            ax.fill_between(t, v, color=colour, alpha=0.85, lw=0, zorder=3)
        elif kind == "step":
            ax.step(t, v, color=colour, lw=1.6, where="post", zorder=3)
        else:
            ax.plot(t, v, color=colour, lw=1.5, zorder=3)
        ax.set_ylabel(label)
        for e in ev:
            ax.axvline(e, color=AQUA, lw=0.7, alpha=0.5, zorder=1)
    axs[-1].set_xlabel("Seconds into the run (green lines: each CamillaDSP \"buffer empty\" line while mpv ran)")
    fig.suptitle(run["title"], x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(os.path.join(OUT, run["file"]), dpi=140)


for r in RUNS:
    draw(r)
