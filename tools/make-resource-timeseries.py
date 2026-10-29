#!/usr/bin/env python3
"""Figure 24: the 4K run of 2026-10-29 over time (data in docs/data). Run start taken as 09:58:41 (environment.txt), so event times are good to about 1 s.
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
rows = list(csv.DictReader(open(os.path.join(D, "resource-log-20261029-4k-samples.csv"))))
col = lambda k: [float(r[k]) for r in rows]
t, net, io, mcpu, err = col("t_s"), col("net_rx_mbps"), col("psi_io_pct"), col("mpv_cpu_pct"), col("pw_err_sum")
ev = []
for s in open(os.path.join(D, "resource-log-20261029-4k-buffer-empty-times.txt")).read().split():
    h, m, sec = map(int, s.split(":"))
    ev.append(h * 3600 + m * 60 + sec - (9 * 3600 + 58 * 60 + 41))
fig, axs = plt.subplots(4, 1, figsize=(11, 8.6), sharex=True, gridspec_kw={"height_ratios": [2, 1.4, 1.4, 1.4]})
axs[0].fill_between(t, net, color=BLUE, alpha=0.85, lw=0, zorder=3); axs[0].set_ylabel("Network in\n(Mbit/s)")
axs[0].text(2, max(net) * 0.9, "Network in: bursts of ~450 Mbit/s, then silence", color=INK, fontsize=9)
axs[1].plot(t, mcpu, color=ORANGE, lw=1.4, zorder=3); axs[1].set_ylabel("mpv CPU\n(% of one core)")
axs[2].plot(t, io, color=GREY, lw=1.6, zorder=3); axs[2].set_ylabel("I/O pressure\n(PSI %)")
axs[3].step(t, err, color=INK, lw=1.6, where="post", zorder=3); axs[3].set_ylabel("PipeWire xruns\n(cumulative)")
for a in axs:
    for e in ev: a.axvline(e, color=AQUA, lw=0.7, alpha=0.5, zorder=1)
axs[3].set_xlabel("Seconds into the run (green lines: each CamillaDSP \"buffer empty\" line)")
fig.suptitle("4K remux streamed from the mount, 600 s: 116 buffer-empty lines (green) against load", x=0.01, ha="left", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig(os.path.join(OUT, "24_4k_run_over_time.png"), dpi=140)
