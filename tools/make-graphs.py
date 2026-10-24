#!/usr/bin/env python3
"""Draws every graph in docs/graphs/ (the README appendix uses a selection of them).

Sources, so nothing here is invented:
  * data/rew/*.txt                 real REW sweeps (19 Oct 2026, before any DSP)
  * scripts/set-eq.py              the exact filter sets, alignment table and height tone filters (responses are computed)
  * numbers written in docs/status.md, docs/alignment.md, docs/tuning-log.md and the measurement reports of 2026-10-21 to
    2026-10-24 (sweep runs 1 and 2, sub test, dialogue kit, reflection analysis, Tenet comparison). Those are summary values:
    the raw recordings are not in the repository, so curves that need them cannot be redrawn here.
Each figure's caption in the file says which of the three it is.   Usage: python3 tools/make-graphs.py   (needs numpy, matplotlib)
"""
import importlib.util
import os
import textwrap

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "docs", "graphs")
os.makedirs(OUT, exist_ok=True)

spec = importlib.util.spec_from_file_location("seteq", os.path.join(ROOT, "scripts", "set-eq.py"))
SE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SE)

BLUE, ORANGE, GREEN, RED, GREY = "#2a6fb0", "#d9822b", "#2e8b57", "#c0392b", "#8a8a8a"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.dpi": 100})


REDRAWN_FROM_RECORDINGS = {"03_drone2_predicted_vs_recorded", "07_dialogue", "08_early_reflections"}


def save(fig, name, note):
    if name in REDRAWN_FROM_RECORDINGS:
        print("skip", name, "(drawn from the recordings by tools/make-recording-graphs.py)")
        plt.close(fig)
        return
    for a in fig.axes:
        if a.get_xscale() == "log":
            a.minorticks_off()
    wrapped = textwrap.fill(note, int(fig.get_figwidth() * 17))
    lines = wrapped.count("\n") + 1
    fig.text(0.01, 0.005, wrapped, fontsize=7, color="#666", va="bottom")
    fig.tight_layout(rect=(0, 0.018 * lines + 0.02, 1, 1))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=160)
    plt.close(fig)
    print("wrote", name)


def read_rew(path):
    f, s = [], []
    for line in open(path):
        if line.startswith("*") or not line.strip():
            continue
        p = line.split()
        f.append(float(p[0]))
        s.append(float(p[1]))
    return np.array(f), np.array(s)


def smooth(f, s, grid, frac=6):
    """Power-average in a 1/frac-octave window."""
    out = []
    for g in grid:
        m = (f >= g * 2 ** (-0.5 / frac)) & (f <= g * 2 ** (0.5 / frac))
        out.append(10 * np.log10(np.mean(10 ** (s[m] / 10))) if m.any() else np.nan)
    return np.array(out)


def band(grid, y, lo, hi):
    return np.nanmean(y[(grid >= lo) & (grid <= hi)])


def filt_db(grid, flt):
    return np.array([sum(SE.peaking_db(g, f0, gn, q) for _, f0, gn, q in flt) for g in grid])


def highshelf_db(f, f0, gain, q, fs=48000):
    a = 10 ** (gain / 40)
    w0 = 2 * np.pi * f0 / fs
    al = np.sin(w0) / (2 * q)
    c = np.cos(w0)
    sq = 2 * np.sqrt(a) * al
    b0, b1, b2 = a * ((a + 1) + (a - 1) * c + sq), -2 * a * ((a - 1) + (a + 1) * c), a * ((a + 1) + (a - 1) * c - sq)
    a0, a1, a2 = (a + 1) - (a - 1) * c + sq, 2 * ((a - 1) - (a + 1) * c), (a + 1) - (a - 1) * c - sq
    z = np.exp(-1j * 2 * np.pi * np.asarray(f) / fs)
    h = (b0 + b1 * z + b2 * z ** 2) / (a0 + a1 * z + a2 * z ** 2)
    return 20 * np.log10(np.abs(h))


GRID = 2 ** np.arange(np.log2(25), np.log2(1000), 1 / 24)
fL, sL = read_rew(os.path.join(ROOT, "data", "rew", "L-sweep-2026-10-19.txt"))
fF, sF = read_rew(os.path.join(ROOT, "data", "rew", "LFE-sweep-2026-10-19.txt"))
yL, yF = smooth(fL, sL, GRID), smooth(fF, sF, GRID)
mid = lambda y: band(GRID, y, 300, 400)
yL -= mid(yL)
yF -= mid(yF)

# ---------------------------------------------------------------------------------------------------------------- 1
fig, ax = plt.subplots(figsize=(9, 4.4))
ax.semilogx(GRID, yL, color=GREY, lw=2, label="before: left speaker, REW sweep at the seat")
ax.semilogx(GRID, yF, color=GREY, lw=1, ls=":", label="before: LFE input (same hump: the sub is shared)")
after = yL + filt_db(GRID, SE.FILTER_SETS["drone2"])
ax.semilogx(GRID, after, color=ORANGE, lw=2, label="after: predicted with the drone2 preset")
ax.axhline(0, color="k", lw=0.5)
pk = (GRID >= 40) & (GRID <= 100)
ib, ia = np.argmax(np.where(pk, yL, -99)), np.argmax(np.where(pk, after, -99))
ax.plot([GRID[ib]], [yL[ib]], "o", color=GREY, ms=5)
ax.plot([GRID[ia]], [after[ia]], "o", color=ORANGE, ms=5)
ax.annotate(f"peak {yL[ib]:+.0f} dB at {GRID[ib]:.0f} Hz", (GRID[ib], yL[ib]), (150, yL[ib] + 2), arrowprops=dict(arrowstyle="-", color=GREY), color="#555")
ax.annotate(f"peak {after[ia]:+.0f} dB at {GRID[ia]:.0f} Hz (kept on purpose)", (GRID[ia], after[ia]), (150, after[ia] - 6), arrowprops=dict(arrowstyle="-", color=ORANGE), color=ORANGE)
print("fig01 peaks: before %+.1f dB at %.0f Hz, after %+.1f dB at %.0f Hz" % (yL[ib], GRID[ib], after[ia], GRID[ia]))
ax.set_xlim(25, 1000)
ax.set_xticks([25, 40, 63, 100, 160, 250, 400, 630, 1000])
ax.set_xticklabels(["25", "40", "63", "100", "160", "250", "400", "630", "1k"])
ax.set_xlabel("Hz")
ax.set_ylabel("dB re the 300-400 Hz level, 1/6 octave")
ax.set_title("The bass hump the Z906 and the room produce, and what drone2 does to it")
ax.legend(loc="upper right", fontsize=8)
save(fig, "01_bass_before_after", "Real REW sweeps (data/rew, 19 Oct 2026, mic calibration applied, no timing reference so read shapes). "
     "'After' is computed, not measured: the sweep plus the exact drone2 filters from scripts/set-eq.py. Labels mark the highest point of each curve between 40 and 100 Hz. Single speaker, one seat.")

# ---------------------------------------------------------------------------------------------------------------- 2
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
ax = axs[0]
names = [("rew", "flat (REW auto-EQ)", GREY), ("hump8", "hump8", "#9bc4e2"), ("hump20", "hump20", "#4b9acb"),
         ("punch20x", "punch20x", "#7a5aa6"), ("drone2", "drone2 (in use)", ORANGE)]
for key, lab, col in names:
    ax.semilogx(GRID, yL + filt_db(GRID, SE.FILTER_SETS[key]), color=col, lw=2.4 if key == "drone2" else 1.3, label=lab)
ax.semilogx(GRID, yL, color="k", lw=0.8, ls="--", label="no EQ")
ax.set_xlim(30, 400)
ax.set_xticks([30, 50, 63, 100, 160, 250, 400])
ax.set_xticklabels(["30", "50", "63", "100", "160", "250", "400"])
ax.set_ylim(-12, 40)
ax.set_xlabel("Hz")
ax.set_ylabel("dB re 300-400 Hz")
ax.set_title("Predicted response at the seat, by preset")
ax.legend(fontsize=8, ncol=2)
ax = axs[1]
sets = ["flat", "hump8", "hump14", "thump14", "hump20", "no EQ"]
song = [8, 12, 18, 23, 23, 35]
clip = [21, 25, 30, 34, 35, 45]
x = np.arange(len(sets))
ax.bar(x - 0.2, song, 0.4, color=BLUE, label="Toliver track (stereo)")
ax.bar(x + 0.2, clip, 0.4, color=ORANGE, label="output.mka clip (Atmos)")
ax.set_xticks(x)
ax.set_xticklabels(sets, rotation=30)
ax.set_ylabel("predicted bass-to-mids balance (dB)")
ax.set_title("Why the first presets were not enough")
ax.legend(fontsize=8)
save(fig, "02_filter_sets", "Left: computed from the real L sweep and the filter sets in scripts/set-eq.py. Right: predicted balances from the 2026-10-19/20 fitting session "
     "(they only mean something relative to each other). drone2 was derived from punch20x with two extra cuts.")

# ---------------------------------------------------------------------------------------------------------------- 3
fig, axs = plt.subplots(1, 2, figsize=(10.5, 4))
ax = axs[0]
g2 = 2 ** np.arange(np.log2(25), np.log2(400), 1 / 48)
fdb = filt_db(g2, SE.FILTER_SETS["drone2"])
ax.semilogx(g2, fdb, color=ORANGE, lw=2, label="drone2 filters (computed)")
bands_ = [(50, "40-63 Hz", -6.0), (80, "80 Hz", -12.0), (100, "100 Hz", -7.5), (125, "125 Hz", -5.0)]
ax.scatter([b[0] for b in bands_], [b[2] for b in bands_], color=BLUE, zorder=5, s=36, label="recorded change, Tenet 'freeport' (about)")
for fx, lab, v in bands_:
    ax.annotate(lab, (fx, v), (fx * 1.05, v - 2.3), fontsize=7.5, color=BLUE)
ax.axhline(0, color="k", lw=0.5)
ax.set_xlim(25, 400)
ax.set_xticks([30, 50, 63, 100, 160, 250, 400])
ax.set_xticklabels(["30", "50", "63", "100", "160", "250", "400"])
ax.set_xlabel("Hz")
ax.set_ylabel("change, dB")
ax.set_ylim(-22, 3)
ax.legend(fontsize=8, loc="lower right")
ax.set_title("Prediction vs recording")
ax = axs[1]
t = ["F1 opening", "Godzilla", "Tenet last 15 s"]
ax.axis("off")
ax.text(0, 0.95, "What the checks showed", fontsize=10, weight="bold", va="top")
ax.text(0, 0.84,
        "Recordings at the seat with and without drone2\nagreed with the predicted band-energy change\nwithin about 1-2 dB wherever the mic did not clip.\n\n"
        "Tenet 'freeport' (neither recording clipped,\nplayback level identical above 500 Hz):\n"
        "  40-63 Hz   about -6 dB\n  80 Hz      about -12 dB\n  100 Hz     about -7.5 dB\n  125 Hz     about -5 dB\n\n"
        "F1 drone sits at 63-92 Hz, the thump at 56-63 Hz:\nthe cuts remove the first and keep the second.\n"
        "Owner's listening agrees (F1, Godzilla).", fontsize=8.5, va="top")
save(fig, "03_drone2_predicted_vs_recorded", "Filter curve computed from scripts/set-eq.py; recorded points are the rounded values from the Tenet comparison (docs/tuning-log.md). "
     "The raw recordings are not in the repository.")

# ---------------------------------------------------------------------------------------------------------------- 4
fig, axs = plt.subplots(1, 3, figsize=(12, 4))
spk = ["FL", "FR", "FC", "SL", "SR", "RL*", "RR*"]
delay = [SE.ALIGN[i][1] for i in (0, 1, 4, 6, 7, 2, 3)]
trim = [SE.ALIGN[i][2] for i in (0, 1, 4, 6, 7, 2, 3)]
ax = axs[0]
ax.bar(spk, delay, color=BLUE)
for i, v in enumerate(delay):
    ax.text(i, v + 0.08, f"{v:.2f}", ha="center", fontsize=7.5)
ax.set_ylabel("delay added (ms)")
ax.set_title("Delays applied (chirp test, 21 Oct; * = height)")
ax = axs[1]
d_after = {"FL": 0.0, "FR": -0.18, "FC": -0.08, "SL": 0.08, "SR": -0.12, "RL": 0.06, "RR": -0.15}
order = ["FL", "FR", "FC", "SL", "SR", "RL", "RR"]
ms_delay = {n: d for n, d in zip(order, delay)}
before = [d_after[n] - (ms_delay[n] - ms_delay["FL"]) for n in order]
after = [d_after[n] for n in order]
yy = np.arange(len(order))
ax.axvspan(-0.9, 0.9, color=GREY, alpha=0.15, lw=0)
for i in yy:
    ax.plot([before[i], after[i]], [i, i], color="#bbb", lw=2, zorder=1)
ax.scatter(before, yy, color=RED, s=40, zorder=3, label="before delays (reconstructed)")
ax.scatter(after, yy, color=GREEN, s=40, zorder=3, label="after, measured (sweep run 1)")
ax.set_yticks(yy)
ax.set_yticklabels(order)
ax.invert_yaxis()
ax.set_xlabel("arrival vs FL (ms); shaded: +-1 ft seating tolerance")
ax.legend(fontsize=7.5, loc="lower left")
ax.set_title(f"Arrival spread {max(before) - min(before):.1f} ms (reconstructed) to {max(after) - min(after):.1f} ms")
ax = axs[2]
pre = [0, 1.9, 0.8, 4.4, 0.7, 0.6, 0.3]
ax.bar(np.arange(7) - 0.2, pre, 0.4, color=RED, label="before trims (above FL, dB)")
post = {"FR": -0.5, "SL": 0.9, "SR": 1.7}
ax.bar([order.index(k) + 0.2 for k in post], list(post.values()), 0.4, color=GREEN, label="after, measured (sweep run 1)")
ax.axhspan(-2, 2, color=GREY, alpha=0.15, lw=0)
ax.set_xticks(range(7))
ax.set_xticklabels(order)
ax.set_ylabel("level re FL (dB)")
ax.set_title("Level trims (within about +-2 dB)")
ax.set_ylim(-2.5, 6)
ax.legend(fontsize=7.5, loc="upper right")
save(fig, "04_alignment", "Delays and trims: scripts/set-eq.py ALIGN table. 'After' arrival and level: sweep run 1 (docs/alignment.md, docs/status.md). 'Before' arrival is "
     "reconstructed as measured arrival minus the delay applied (the REW sweeps carry no timing reference); the 2026-10-24 comparison quotes about 4.9 ms for all speakers. "
     "Before-trim levels are the band-energy values of the chirp test; after-trim values for FC and the heights were not recorded. Quoted values: where they differ from the redrawn figures 12, 13 and 15, those are the better ones.")

# ---------------------------------------------------------------------------------------------------------------- 5
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
ax = axs[0]
gt = 2 ** np.arange(np.log2(100), np.log2(20000), 1 / 24)
resp = np.array([SE.peaking_db(g, 310, -7.5, 1.0) + SE.peaking_db(g, 1700, -7.0, 2.5) for g in gt]) + highshelf_db(gt, 6000, 2.5, 0.8) + SE.HEIGHT_TONE_TRIM_DB
ax.semilogx(gt, resp, color=ORANGE, lw=2, label="filters + trim")
ax.axhline(0, color="k", lw=0.5)
ax.set_xlim(100, 20000)
ax.set_xticks([100, 310, 1000, 1700, 6000, 20000])
ax.set_xticklabels(["100", "310", "1k", "1.7k", "6k", "20k"])
ax.set_ylabel("dB")
ax.set_xlabel("Hz")
ax.set_title(f"Height tone-match (trim {SE.HEIGHT_TONE_TRIM_DB:+.1f} dB included)")
ax = axs[1]
cats = ["bass gap vs bed\n(40-400 Hz)", "tone vs bed\n(170 Hz-12.5 kHz)"]
b_l, b_r = [25, 3.4], [28, 3.7]
a_l, a_r = [4.0, 2.9], [3.4, 3.3]
x = np.arange(2)
ax.bar(x - 0.3, b_l, 0.15, color=GREY, label="RL before")
ax.bar(x - 0.15, b_r, 0.15, color="#555", label="RR before")
ax.bar(x + 0.0, a_l, 0.15, color="#f0b27a", label="RL after")
ax.bar(x + 0.15, a_r, 0.15, color=ORANGE, label="RR after")
ax.set_xticks(x)
ax.set_xticklabels(cats)
ax.set_ylabel("rms deviation (dB)")
ax.set_title("Heights vs the five bed speakers (REW baseline)")
ax.legend(fontsize=7.5)
save(fig, "05_heights", "Left: computed from HEIGHT_TONE in scripts/set-eq.py. Right: before/after values quoted in the 2026-10-23/24 comparison (REW baseline of 19 Oct against the final profile). "
     "Same-session sweeps 1 and 2 gave a smaller tone gain (4.5/4.1 to 3.1/3.5 dB) and, for the bass, 41 dB (heights alone, the analyser's per-bin rms; about 27 dB with 1/6-octave smoothing) to 2.6/2.7 dB: see docs/status.md. The heights alone are 11 dB down at 125 Hz and 27 dB down at 100 Hz.")

# ---------------------------------------------------------------------------------------------------------------- 6
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axs[0]
fq = np.array([40, 35.6, 31.7, 28.3, 25.2, 22.4])
lv = np.array([-1.4, -3.0, -7.5, -11.0, -16.0, -21.0])
dist = [2, 5, 16, 16, 14]
ax.plot(fq, lv, color=BLUE, marker="o", lw=2)
ax.set_xscale("log")
ax.invert_xaxis()
ax.set_xticks([40, 35.6, 31.7, 28.3, 25.2, 22.4])
ax.set_xticklabels(["40", "35.6", "31.7", "28.3", "25.2", "22.4"], rotation=45)
ax.minorticks_off()
ax.set_ylabel("level vs 45 Hz (dB)")
ax.set_xlabel("Hz")
for f, v, d in zip(fq[:5], lv[:5], dist):
    ax.annotate(f"{d}% dist.", (f, v), xytext=(8, -14), textcoords="offset points", fontsize=7.5, color=RED)
ax.annotate("at the noise floor", (22.4, -21), xytext=(-8, 10), textcoords="offset points", fontsize=7.5, color="#777", ha="right")
ax.set_ylim(-25, 1)
ax.set_title("Sub range, sweep at -14 dBFS (mic rolls off below ~20 Hz)")
ax = axs[1]
gs = GRID[(GRID >= 25) & (GRID <= 200)]
ax.semilogx(gs, yF[(GRID >= 25) & (GRID <= 200)], color=GREY, lw=2)
ax.axvspan(56, 63, color=ORANGE, alpha=0.2, lw=0)
ax.axvspan(71, 90, color=BLUE, alpha=0.15, lw=0)
tr = ax.get_xaxis_transform()
ax.axvline(100, color="#999", lw=0.8, ls=":")
ax.text(59, 0.04, "mode\n56-63 Hz", transform=tr, fontsize=8, color="#a65d00", ha="center")
ax.text(80, 0.04, "null\n71-90 Hz", transform=tr, fontsize=8, color=BLUE, ha="center")
ax.text(103, 0.04, "peak at\n100 Hz (+5 dB)", transform=tr, fontsize=8, color="#555", ha="left")
ax.set_xticks([25, 40, 63, 100, 160])
ax.set_xticklabels(["25", "40", "63", "100", "160"])
ax.minorticks_off()
ax.set_xlabel("Hz")
ax.set_ylabel("dB re 300-400 Hz")
ax.set_title("Room modes at the seat (real LFE sweep, before any DSP)")
save(fig, "20_room_modes", "Left: values from the 2026-10-23 sub test report (sweeps at -30, -22, -14 dBFS; no compression above 35 Hz (up to about 2.5 dB at 25-30 Hz, fig 06); stepped-tone rattle hunt grew by at most 4 dB when 10 dB louder, "
     "so no rattle). Right: real REW LFE sweep of 19 Oct (before any DSP); the shaded bands and the 100 Hz peak are the frequencies stated in docs/tuning-log.md, taken from the later sweeps.")

# ---------------------------------------------------------------------------------------------------------------- 7
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
ax = axs[0]
vals = [("IR, no noise", 0.83), ("IR + noise", 0.79), ("direct, centre", 0.79), ("direct, phantom", 0.81)]
ax.axhspan(0.75, 1, color="#e8f3ec", lw=0)
ax.bar(range(4), [v for _, v in vals], color=["#9bc4e2", "#4b9acb", GREEN, BLUE], width=0.6)
for i, (_, v) in enumerate(vals):
    ax.text(i, v + 0.01, f"{v:.2f}", ha="center", weight="bold")
ax.set_xticks(range(4))
ax.set_xticklabels([n for n, _ in vals], fontsize=8)
ax.set_ylim(0.4, 1.0)
ax.set_ylabel("STI (STIPA-style)")
ax.text(-0.45, 0.955, "green band: excellent (> 0.75)", ha="left", fontsize=7.5, color="#3a7")
ax.set_title("Dialogue intelligibility")
ax.text(0.02, 0.05, "C50 +9.9 dB, RT60 0.37-0.44 s", transform=ax.transAxes, fontsize=8)
ax = axs[1]
bands = [125, 250, 500, 1000, 2000, 4000, 8000]
dia = [-60.1, -64.4, -63.0, -67.3, -72.7, -73.9, -76.5]
noi = [-74.2, -78.0, -75.6, -82.9, -87.5, -92.3, -92.8]
ax.plot(range(7), dia, color=GREEN, marker="o", lw=2, label="dialogue at the seat")
ax.plot(range(7), noi, color=GREY, marker="s", lw=2, label="room noise floor")
ax.fill_between(range(7), noi, dia, color="#e8f3ec")
for i in range(7):
    ax.text(i, (dia[i] + noi[i]) / 2, f"{dia[i] - noi[i]:.0f}", ha="center", va="center", fontsize=8, weight="bold")
ax.set_xticks(range(7))
ax.set_xticklabels([str(b) for b in bands])
ax.set_xlabel("octave band, Hz")
ax.set_ylabel("dBFS (uncalibrated)")
ax.legend(loc="lower left", fontsize=8)
ax.set_title("Dialogue to noise per band (dB, shown in the fill)")
save(fig, "07_dialogue", "From the dialogue-kit report on dlg1.wav quoted in the 2026-10-24 working session (one seat, one mic position; differences under about 2 dB per band or 0.03 STI are within repeatability). "
     "STI is a STIPA-style estimate without auditory masking, not a certified measurement. docs/status.md still lists the dialogue kit as not yet run in the room: reconcile that before relying on this figure.")

# ---------------------------------------------------------------------------------------------------------------- 8
fig, ax = plt.subplots(figsize=(8, 4))
sp = ["FC", "FR", "FL", "RL (height)", "RR (height)"]
worst = [-14, -14, -8, -1, -1]
cols = [GREEN, GREEN, ORANGE, RED, RED]
hatch = ["//", "//", "", "", ""]
for i, (w, c, h) in enumerate(zip(worst, cols, hatch)):
    ax.bar(i, w, color=c, hatch=h, edgecolor="white")
    ax.text(i, 0.6, ("at most " if h else "") + f"{w} dB", ha="center", va="bottom", fontsize=8.5)
ax.axhline(-10, color=RED, ls="--", lw=1)
ax.text(4.45, -9.3, "ITU-R BS.1116 limit (-10 dB)", ha="right", fontsize=8, color=RED)
ax.set_ylim(-18, 3)
ax.set_xticks(range(5))
ax.set_xticklabels(sp)
ax.set_ylabel("strongest reflection in the first 15 ms\n(dB re direct sound)")
ax.set_title("Early reflections at the seat, panels in place")
save(fig, "08_early_reflections", "Values from the reflection analysis of sweep run 2 (docs/status.md). FC and FR: nothing above -14 dB (hatched bars are an upper bound). FL: one reflection at 5.1 ms, "
     "-8 dB. Heights: a reflection about -1 dB at 3.6-3.8 ms. No panels-off baseline yet, so this shows where the energy is, not what the panels do.")

# ---------------------------------------------------------------------------------------------------------------- 9
fig, axs = plt.subplots(1, 4, figsize=(12, 3.6))
items = [("bass hump\n(dB over mids)", 31, 24), ("bed level spread\n(dB)", 4.7, 1.6), ("arrival spread\n(ms)", 4.9, 0.6),
         ("heights' bass gap\n(dB rms)", 26.5, 3.7)]
for ax, (t, b, a) in zip(axs, items):
    ax.bar([0, 1], [b, a], color=[GREY, ORANGE], width=0.6)
    for i, v in enumerate((b, a)):
        ax.text(i, v + max(b, a) * 0.02, f"{v:g}", ha="center", fontsize=9, weight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["before", "after"])
    ax.set_title(t, fontsize=9)
    ax.set_ylim(0, max(b, a) * 1.18)
axs[0].set_ylabel("value")
save(fig, "09_before_after_summary", "Values from the 2026-10-24 before/after comparison (REW baseline of 19 Oct against the final profile). Heights' bass gap is the mean of RL 25 and RR 28 before, 4.0 and 3.4 after (shown 26.5 to 3.7). "
     "The hump is deliberately kept (24 dB). Heights' tone against the bed improved only about 0.5 dB on this baseline (3.4/3.7 to 2.9/3.3).")

print("done")
