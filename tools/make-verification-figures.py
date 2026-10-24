#!/usr/bin/env python3
"""Summary figures for the README, drawn from the numbers recorded in docs/status.md, docs/alignment.md and
tools/upmixtest/README.md. These are the documented summary values, not re-analysed recordings: the raw sweep
recordings are not in the repository (see data/README.md). Output: docs/graphs/10_verification_summary.png, 11_upmix_adaptive_vs_fixed.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "graphs")
C1, C2, GREY = "#2a6fb0", "#d9822b", "#8a8a8a"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))

# 1. arrival time relative to FL, sweep run 1 (2026-10-23), docs/alignment.md
spk = ["FR", "FC", "SL", "SR", "RL", "RR"]
arr = [-0.18, -0.08, 0.08, -0.12, 0.06, -0.15]
ax[0].axhspan(-0.2, 0.2, color=GREY, alpha=0.18, lw=0)
ax[0].bar(spk, arr, color=C1)
ax[0].axhline(0, color="k", lw=0.6)
ax[0].set_ylim(-0.5, 0.5)
ax[0].set_ylabel("arrival vs FL (ms)")
ax[0].set_title("Delays, measured (run 1, six speakers vs FL)\n(within 0.2 ms, shaded; sub not shown)", fontsize=9)

# 2. level vs FL at 500 Hz-2 kHz, sweep run 1, docs/status.md
spk2 = ["FR", "SL", "SR"]
lvl = [-0.5, 0.9, 1.7]
ax[1].axhspan(-2, 2, color=GREY, alpha=0.18, lw=0)
ax[1].bar(spk2, lvl, color=C1)
ax[1].axhline(0, color="k", lw=0.6)
ax[1].set_ylim(-4, 4)
ax[1].set_ylabel("level vs FL (dB)")
ax[1].set_title("Level trims, measured\n(about +-2 dB, mic-position limit)", fontsize=9)

# 3. heights vs bed (docs/status.md): two separate quantities, each on its own axis
pos = ax[2].get_position()
ax[2].remove()
inner = fig.add_gridspec(1, 2, left=0.70, right=0.985, bottom=pos.y0, top=pos.y1, wspace=0.6)
b1, b2 = fig.add_subplot(inner[0]), fig.add_subplot(inner[1])
for a_, bef, aft, ttl in ((b1, 41.1, 2.65, "heights + sub vs bed,\n40-400 Hz (rms dB)"), (b2, 4.3, 3.3, "heights tone vs bed,\n170 Hz-12.5 kHz (rms dB)")):
    a_.bar([0, 1], [bef, aft], color=[GREY, C2], width=0.6)
    a_.set_xticks([0, 1])
    a_.set_xticklabels(["before", "after"])
    for i, v in enumerate((bef, aft)):
        a_.text(i, v + 0.02 * max(bef, aft), f"{v:.1f}" if v < 10 else f"{v:.0f}", ha="center", fontsize=8)
    a_.set_title(ttl, fontsize=8)
    a_.set_ylim(0, max(bef, aft) * 1.15)
b1.set_ylabel("rms deviation (dB)")
fig.suptitle("Measured at one seat, 2026-10-23 sweep runs (values from docs/status.md)", fontsize=10, x=0.01, ha="left")
fig.subplots_adjust(left=0.06, right=0.985, bottom=0.27, top=0.76, wspace=0.3)
fig.text(0.01, 0.01, "Left two panels: sweep run 1. Right (mean of RL and RR): run 1 (before) and run 2 (after); the mic moved between the runs.\nThe before bass is the heights alone, no sub feed, per analysis bin; with 1/6-octave smoothing it is about 27 dB (fig 13).", fontsize=7, color="#666")
fig.savefig(os.path.join(OUT, "10_verification_summary.png"), dpi=160)

# 4. upmix: fixed side-signal matrix vs adaptive ambience, tools/upmixtest/README.md
w = 0.36
fig, ax = plt.subplots(figsize=(6.4, 3.9))
stim = ["harmonic notes,\nhard left", "harmonic notes,\n70% left", "dense noise,\nhard left"]
fixed = [3.6, 8.5, 3.6]
adapt = [21, 22, 4.0]
x = range(3)
ax.bar([i - w / 2 for i in x], fixed, w, label="fixed S=(L-R)/2", color=GREY)
ax.bar([i + w / 2 for i in x], adapt, w, label="adaptive", color=C2)
ax.set_xticks(list(x))
ax.set_xticklabels(stim)
ax.set_ylabel("ambience minus instrument leak (dB)")
ax.set_title("Adaptive ambience prototype (offline, synthetic test signals)", fontsize=9)
ax.legend(frameon=False)
fig.tight_layout(rect=(0, 0.14, 1, 1))
fig.text(0.01, 0.01, "Synthetic signals only: an instrument (harmonic notes or noise) panned into a stereo mix with reverb,\nso the leak and the retained ambience are known exactly. Metric: ambience kept in the surrounds\nminus instrument leaking into them, dB (tools/upmixtest). Not music.", fontsize=6.5, color="#666")
fig.savefig(os.path.join(OUT, "11_upmix_adaptive_vs_fixed.png"), dpi=160)
print("ok")
