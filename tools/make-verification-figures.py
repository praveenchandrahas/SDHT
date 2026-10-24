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
ax[0].set_title("Delays, verified\n(all within 0.2 ms, shaded)", fontsize=9)

# 2. level vs FL at 500 Hz-2 kHz, sweep run 1, docs/status.md
spk2 = ["FR", "SL", "SR"]
lvl = [-0.5, 0.9, 1.7]
ax[1].axhspan(-2, 2, color=GREY, alpha=0.18, lw=0)
ax[1].bar(spk2, lvl, color=C1)
ax[1].axhline(0, color="k", lw=0.6)
ax[1].set_ylim(-4, 4)
ax[1].set_ylabel("level vs FL (dB)")
ax[1].set_title("Level trims, measured\n(about +-2 dB, mic-position limit)", fontsize=9)

# 3. heights vs bed, sweep run 2 (docs/status.md): rms deviation 40-400 Hz (bass), tone deviation
labels = ["heights + sub\nvs bed, 40-400 Hz", "tone deviation\nvs bed"]
before = [40, 4.3]      # docs: "~40 dB" (approximate); tone 4.5 / 4.1 -> mean 4.3
after = [2.65, 3.3]     # docs: 2.6 / 2.7; tone 3.1 / 3.5 -> mean 3.3
x = range(2)
w = 0.36
ax[2].bar([i - w / 2 for i in x], before, w, label="before", color=GREY)
ax[2].bar([i + w / 2 for i in x], after, w, label="after", color=C2)
ax[2].set_xticks(list(x))
ax[2].set_xticklabels(labels)
ax[2].set_ylabel("rms deviation (dB)")
for i in x:
    ax[2].text(i - w / 2, before[i] + 0.8, f"{before[i]:g}", ha="center", fontsize=8)
    ax[2].text(i + w / 2, after[i] + 0.8, f"{after[i]:.1f}", ha="center", fontsize=8)
ax[2].set_title("Heights bass management and tone-match\n(mean of RL and RR)", fontsize=9)
ax[2].legend(frameon=False)
fig.suptitle("Verification summary, 2026-10-23 sweep runs (documented values, see docs/status.md)", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "10_verification_summary.png"), dpi=160)

# 4. upmix: fixed side-signal matrix vs adaptive ambience, tools/upmixtest/README.md
fig, ax = plt.subplots(figsize=(6.4, 3.4))
stim = ["harmonic notes,\nhard left", "harmonic notes,\n70% left", "dense noise,\nhard left"]
fixed = [3.6, 8.5, 3.6]
adapt = [21, 22, 4.0]
x = range(3)
ax.bar([i - w / 2 for i in x], fixed, w, label="fixed S=(L-R)/2", color=GREY)
ax.bar([i + w / 2 for i in x], adapt, w, label="adaptive", color=C2)
ax.set_xticks(list(x))
ax.set_xticklabels(stim)
ax.set_ylabel("ambience minus instrument leak (dB)")
ax.set_title("Adaptive ambience prototype (offline, not in the signal path)", fontsize=9)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "11_upmix_adaptive_vs_fixed.png"), dpi=160)
print("ok")
