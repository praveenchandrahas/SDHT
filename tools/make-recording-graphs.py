#!/usr/bin/env python3
"""Draws the graphs that need the raw recordings, into docs/graphs/. The recordings are not in the repository (large, and some are of
copyrighted film soundtracks); pass their paths. Each figure is drawn only if its inputs are given.

  python3 tools/make-recording-graphs.py --sweep1 sweep1.wav --sweep2 sweep2.wav --sub sub-sweep.wav --hot subtest-hot.wav \\
      --dlg dlg1.wav --tenet-direct a.wav --tenet-drone2 b.wav --amaze amaze.wav --direct direct2.wav --thump thump20x.wav --tight tight20x.wav

Uses the analysers in tools/sweeptest, tools/subtest, tools/dialoguetest and tools/reflecttest (their reports are re-run and parsed
for the sub and dialogue figures) and scripts/set-eq.py for the filter definitions.  Needs numpy, scipy, matplotlib.
"""
import argparse
import importlib.util
import io
import json
import os
import sys
import re
import contextlib
import textwrap

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch, spectrogram, butter, sosfiltfilt, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "docs", "graphs")
WS = os.environ.get("SDHT_WORKSPACE", os.path.join(ROOT, ".."))   # the repositories are cloned side by side (scripts/clone-all.sh)


def sib(repo, *parts):
    p = os.path.join(WS, repo, *parts)
    if not os.path.exists(p):
        sys.exit(f"{p} not found: clone the {repo} repository next to this one (scripts/clone-all.sh) or set SDHT_WORKSPACE")
    return p
os.makedirs(OUT, exist_ok=True)
FS = 48000
BLUE, ORANGE, GREEN, RED, GREY, PURPLE = "#2a6fb0", "#d9822b", "#2e8b57", "#c0392b", "#8a8a8a", "#7a5aa6"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25})


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SE = load("seteq", sib("theater-router", "scripts", "set-eq.py"))
SW = load("sweepan", sib("theater-measurement", "tools", "sweeptest", "analyze-sweeptest.py"))
SUB = load("subtestan", sib("theater-measurement", "tools", "subtest", "analyze-subtest.py"))
RF = load("reflan", sib("theater-measurement", "tools", "reflecttest", "analyze-reflections.py"))
CSW = json.load(open(sib("theater-measurement", "tools", "sweeptest", "sweeptest-cues.json")))
CSUB = json.load(open(sib("theater-measurement", "tools", "subtest", "subtest-cues.json")))


def save(fig, name, note):
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


def logticks(ax, ticks, lo, hi):
    ax.set_xlim(lo, hi)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t / 1000:g}k" if t >= 1000 else f"{t:g}" for t in ticks])
    ax.minorticks_off()


def smooth_pow(f, p, grid, frac=6):
    out = []
    for g in grid:
        m = (f >= g * 2 ** (-0.5 / frac)) & (f < g * 2 ** (0.5 / frac))
        out.append(p[m].mean() if m.any() else np.nan)
    return np.array(out)


def db(p):
    return 10 * np.log10(np.maximum(p, 1e-30))


def mono(path):
    return SW.load_mono(path)


# ------------------------------------------------------------------------------------------------ sweep recordings
BED = ["FL", "FR", "FC", "SL", "SR"]
NAMES = CSW["names"]


def speakers(path):
    x = SW.load_mono(path)
    a, b, how = SW.placement(x, CSW)
    out = {}
    for sl in CSW["slots"]:
        if len(sl["ch"]) != 1:
            continue
        n = NAMES[sl["ch"][0]]
        if n in out:
            continue
        d = SW.deconv(x, CSW, a, b, sl)
        if d is None:
            continue
        h, pre = d
        lo, hi = (40, 120) if n == "LFE" else (300, 4000)
        t, _ = SW.arrival(h, pre, lo, hi)
        f, H = SW.spectrum(h, pre, t)
        out[n] = dict(f=f, p=np.abs(H) ** 2, t=t, H=H, h=h, pre=pre)
    return out


GRID = 2 ** np.arange(np.log2(25), np.log2(16000), 1 / 12)


def curves(sp, grid=GRID, frac=6):
    c = {n: smooth_pow(v["f"], v["p"], grid, frac) for n, v in sp.items()}
    c["bed"] = np.mean([c[n] for n in BED], axis=0)
    return c


def sweep_figures(p1, p2):
    s1, s2 = speakers(p1), speakers(p2)
    c1, c2 = curves(s1), curves(s2)
    hi = (GRID >= 170) & (GRID <= 12500)
    lf = (GRID >= 40) & (GRID <= 400)
    cols = {"RL": ORANGE, "RR": PURPLE}

    # --- heights tone vs bed, before and after
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4), sharey=True)
    for ax, c, ttl in ((axs[0], c1, "sweep run 1: heights not processed"), (axs[1], c2, "sweep run 2: heights bass-managed and tone-matched")):
        ax.axhspan(-3, 3, color=GREY, alpha=0.15, lw=0)
        for n in BED:
            ax.semilogx(GRID, db(c[n]) - db(c["bed"]), color="#bbb", lw=0.8)
        for n in ("RL", "RR"):
            d = db(c[n]) - db(c["bed"])
            ax.semilogx(GRID, d, color=cols[n], lw=1.8, label=f"{n}: {np.sqrt(np.mean(d[hi] ** 2)):.1f} dB rms (170 Hz-12.5 kHz)")
        ax.axhline(0, color="k", lw=0.5)
        ax.set_ylim(-14, 14)
        logticks(ax, [200, 500, 1000, 2000, 5000, 10000], 170, 14000)
        ax.set_xlabel("Hz")
        ax.set_title(ttl)
        ax.legend(fontsize=8, loc="upper left")
    axs[0].set_ylabel("dB re the mean of the five bed speakers, 1/6 octave")
    axs[0].text(0.99, 0.03, "grey lines: the five bed speakers", transform=axs[0].transAxes, ha="right", fontsize=7.5, color="#888")
    save(fig, "12_heights_tone_before_after", "Real recordings (sweep1.wav, sweep2.wav, 23 Oct, CamillaDSP in the path, deconvolved with the sweep-test analyser). The mic was not in exactly the same spot between the runs: "
         "single bins move 3-7 dB and the bed speakers themselves moved up to 5-7 dB at 310 Hz, so judge the band averages. The sweep analyser's own values for the same data are 4.5/4.1 dB before and 3.1/3.5 dB after (170 Hz-12.5 kHz). The +1.0 dB trim was set after run 2 (run 2 had +3.0 dB).")

    # --- heights bass, own 400-1000 Hz level
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
    norm = (GRID >= 400) & (GRID <= 1000)
    for ax, c, ttl in ((axs[0], c1, "before: heights played as they are"), (axs[1], c2, "after: high-pass 140 Hz, bass sent to the sub")):
        ref = lambda y: y - db(np.mean(10 ** (y[norm] / 10)))
        ax.semilogx(GRID, ref(db(c["bed"])), color=GREY, lw=2.4, label="bed mean")
        for n in ("RL", "RR"):
            ax.semilogx(GRID, ref(db(c[n])), color=cols[n], lw=1.6, label=n)
        ax.set_ylim(-50, 35)
        logticks(ax, [30, 50, 80, 125, 200, 315, 500, 1000], 25, 1000)
        ax.set_xlabel("Hz")
        ax.set_title(ttl)
        ax.legend(loc="lower right", fontsize=8)
    axs[0].set_ylabel("dB re each curve's own 400 Hz-1 kHz level")
    d2 = {n: db(c2[n]) - db(c2["bed"]) for n in ("RL", "RR")}
    d1 = {n: db(c1[n]) - db(c1["bed"]) for n in ("RL", "RR")}
    axs[1].text(0.02, 0.05, f"heights vs bed, 40-400 Hz rms, 1/6-oct smoothing:\nbefore {np.sqrt(np.mean(d1['RL'][lf] ** 2)):.0f} / {np.sqrt(np.mean(d1['RR'][lf] ** 2)):.0f} dB, after {np.sqrt(np.mean(d2['RL'][lf] ** 2)):.1f} / {np.sqrt(np.mean(d2['RR'][lf] ** 2)):.1f} dB (RL / RR)",
                transform=axs[1].transAxes, fontsize=8)
    save(fig, "13_heights_bass", "Real recordings, sweep run 1 and run 2. Each curve is normalised to its own 400 Hz-1 kHz level, so the plot shows bass relative to the mids. After: the sub reproduces the heights' bass, "
         "so the low end lining up with the bed is expected by construction: it shows the bass management works as designed, not that the bass is right. The rms figures in the box use the raw (un-normalised) difference to the bed with 1/6-octave smoothing; the sweep analyser's per-bin figure for the heights alone is 41 dB (docs/status.md), the same gap measured more harshly.")

    # --- each speaker vs the bed (final profile)
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    colset = {"FL": "#0072B2", "FR": "#56B4E9", "FC": "#009E73", "SL": "#CC79A7", "SR": "#E69F00", "RL": ORANGE, "RR": PURPLE}
    g2 = (GRID >= 160) & (GRID <= 12500)
    ax.axhspan(-3, 3, color=GREY, alpha=0.15, lw=0)
    for n in ("FL", "FR", "FC", "SL", "SR", "RL", "RR"):
        ax.semilogx(GRID[g2], (db(c2[n]) - db(c2["bed"]))[g2], color=colset[n], lw=2.2 if n in ("RL", "RR") else 1.1, label=n)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylim(-12, 12)
    logticks(ax, [200, 500, 1000, 2000, 5000, 10000], 160, 12500)
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB re the mean of the five bed speakers")
    ax.set_title("Tone of each speaker alone, final profile (sweep run 2)")
    ax.legend(ncol=4, fontsize=8, loc="lower left")
    save(fig, "14_tone_each_speaker", "Real recording, sweep run 2, 1/6-octave smoothing, one seat. Shaded band: +-3 dB. The bed speakers sit within about +-3 dB of each other in the mids; the top end of the heights is still 4-10 dB above the bed above 8 kHz, "
         "and the narrow differences between RL and RR are ceiling reflections and comb filtering that one seat cannot support EQ for.")

    # --- timing and level
    order = ["FL", "FR", "FC", "SL", "SR", "RL", "RR"]
    ap = {n: SE.ALIGN[i][1] for i, n in ((0, "FL"), (1, "FR"), (4, "FC"), (6, "SL"), (7, "SR"), (2, "RL"), (3, "RR"))}
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    ax = axs[0]
    ax.axvspan(-0.9, 0.9, color=GREY, alpha=0.15, lw=0)
    yy = np.arange(len(order))
    bef1 = [s1[n]["t"] - s1["FL"]["t"] - (ap[n] - ap["FL"]) for n in order]
    aft1 = [s1[n]["t"] - s1["FL"]["t"] for n in order]
    aft2 = [s2[n]["t"] - s2["FL"]["t"] for n in order]
    for i in yy:
        ax.plot([bef1[i], aft1[i]], [i, i], color="#ccc", lw=2, zorder=1)
    ax.scatter(bef1, yy, color=RED, s=40, zorder=3, label="before delays (run 1 minus the delay applied)")
    ax.scatter(aft1, yy, color=GREEN, s=40, zorder=3, label="after, run 1")
    ax.scatter(aft2, yy, color=BLUE, s=26, marker="D", zorder=3, label="after, run 2")
    ax.set_yticks(yy)
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    ax.set_xlabel("arrival vs FL (ms); shaded: +-1 ft seating tolerance")
    ax.set_xlim(-5.2, 1.2)
    ax.legend(fontsize=7.5, loc="upper left")
    ax.set_title(f"Arrival spread: {max(bef1) - min(bef1):.1f} ms before, {max(aft1) - min(aft1):.2f} / {max(aft2) - min(aft2):.2f} ms after")
    ax = axs[1]
    def lv(sp):
        e = {n: np.sum(v["p"][(v["f"] >= 500) & (v["f"] <= 2000)]) for n, v in sp.items()}
        return [10 * np.log10(e[n] / e["FL"]) for n in order]
    x = np.arange(len(order))
    ax.axhspan(-2, 2, color=GREY, alpha=0.15, lw=0)
    ax.bar(x - 0.2, lv(s1), 0.4, color=GREEN, label="run 1")
    ax.bar(x + 0.2, lv(s2), 0.4, color=BLUE, label="run 2 (mic moved; heights at +3 dB trim)")
    ax.set_xticks(x)
    ax.set_xticklabels(order)
    ax.set_ylabel("level 500 Hz-2 kHz re FL (dB)")
    ax.set_title("Levels after the trims (about 2.5 dB at most within a run)")
    ax.legend(fontsize=7.5)
    lfe = f"sub (LFE): arrives {s1['LFE']['t'] - s1['FL']['t']:+.1f} ms after FL by envelope, group delay 50-100 Hz about +15 ms (its own filters included)"
    save(fig, "15_timing_and_level", "Real recordings (levels: 500 Hz-2 kHz band energy from these sweeps; the sweep analyser's own report differs by up to 0.5 dB, e.g. SR +1.7 dB in run 1). The same speaker moves by about 2.3 to 2.5 dB between the runs (SL +0.9 to -1.4 dB in the analyser's report), so the trims are good to roughly 2 dB, not better. 'Before' = the measured arrival minus the delay set-eq.py applies (the REW sweeps carry no timing reference). " + lfe +
         ". The sub arrives 6 to 7 ms late in both runs. Its delay is currently kept equal to FL's (0.20 ms) because its arrival had not been measured before.")
    return s1, s2


# ------------------------------------------------------------------------------------------------ early reflections
def reflection_figure(path):
    xr = SW.load_mono(path)
    a, b, _ = SW.placement(xr, CSW)
    res = {}
    for n in ("FL", "FC", "FR", "RL", "RR"):
        sl = [s for s in CSW["slots"] if s["ch"] == [NAMES.index(n)]][0]
        h, pre = SW.deconv(xr, CSW, a, b, sl)
        t, E, seg, m, k, nfl = RF.etc(h, pre)
        refl = RF.reflections(t, E)
        r15 = [r for r in refl if 1.0 <= r[0] <= 15.0]
        top = max(r15, key=lambda r: r[1])
        res[n] = (t, E, top)
    fig, axs = plt.subplots(5, 1, figsize=(9.5, 10.5), sharex=True)
    colset = {"FL": "#0072B2", "FC": "#009E73", "FR": "#56B4E9", "RL": ORANGE, "RR": PURPLE}
    summary = {}
    for ax, n in zip(axs, ("FL", "FC", "FR", "RL", "RR")):
        t, E, top = res[n]
        ax.axvspan(1, 15, color="#f4f7fb", zorder=0)
        ax.plot(t, E, color=colset[n], lw=1.1)
        ax.axhline(-10, color=RED, ls="--", lw=0.9)
        ax.set_ylim(-45, 6)
        ax.set_xlim(-1, 30)
        ax.set_ylabel(f"{n}, dB")
        v = "PASS" if top[1] <= -15 else ("OK" if top[1] <= -10 else "FAIL")
        ax.annotate(f"{top[0]:.1f} ms, {top[1]:.1f} dB", (top[0], top[1]), xytext=(top[0] + 2.5, top[1] + 9), fontsize=8, arrowprops=dict(arrowstyle="-", color="#999"))
        ax.text(0.995, 0.86, f"worst reflection 1-15 ms: {top[1]:.1f} dB  ->  {v}", transform=ax.transAxes, ha="right", fontsize=8.5, weight="bold")
        summary[n] = top
    axs[0].set_title("Early reflections at the seat (1-8 kHz energy-time curve, dB re the direct sound)")
    axs[-1].set_xlabel("ms after the direct sound   (shaded: 1-15 ms; dashed: ITU-R BS.1116 limit, -10 dB)")
    save(fig, "08_early_reflections", "Real recording, sweep run 2 (panels in place, no panels-off baseline), analysed with tools/reflecttest. The band is 1-8 kHz, where thin absorber panels work. "
         "This shows where the energy is, not what the panels do: that needs the same sweep with the panels covered (--base).")
    # compact bar chart
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ns = ["FC", "FR", "FL", "RL", "RR"]
    vals = [summary[n][1] for n in ns]
    ax.bar(range(5), vals, color=[GREEN if v <= -10 else (ORANGE if v <= -6 else RED) for v in vals])
    for i, (n, v) in enumerate(zip(ns, vals)):
        ax.text(i, 0.6, f"{v:.1f} dB\n{summary[n][0]:.1f} ms", ha="center", va="bottom", fontsize=8)
    ax.axhline(-10, color=RED, ls="--", lw=1)
    ax.text(4.45, -9.3, "BS.1116 limit (-10 dB)", ha="right", fontsize=8, color=RED)
    ax.set_xticks(range(5))
    ax.set_xticklabels(["FC", "FR", "FL", "RL (height)", "RR (height)"])
    ax.set_ylim(-18, 5)
    ax.set_ylabel("worst reflection in 1-15 ms\n(dB re direct sound)")
    ax.set_title("Early reflections: summary")
    save(fig, "08b_early_reflections_summary", "Same data as 08_early_reflections: the strongest reflection 1-15 ms after the direct sound, with its delay.")
    return summary


# ------------------------------------------------------------------------------------------------ sub test
def run_report(mod, path, extra=()):
    buf = io.StringIO()
    import sys
    old = sys.argv
    sys.argv = ["x", path, *extra]
    try:
        with contextlib.redirect_stdout(buf):
            mod.OUT.clear()
            mod.main()
    finally:
        sys.argv = old
    return buf.getvalue()


def nums(s):
    return [float(v) for v in re.findall(r"[-+]?\d+\.?\d*(?:e[-+]?\d+)?", s)]


def sub_figures(path):
    txt = run_report(SUB, path, ["--out=" + os.devnull])
    lines = txt.splitlines()
    i0 = next(i for i, l in enumerate(lines) if l.strip().startswith("Hz") and "compression" in l)
    resp = []
    for l in lines[i0 + 1:]:
        if not l.strip():
            break
        v = nums(l.replace("*", ""))
        star = ["*" in c for c in re.split(r"\s{2,}", l.strip())[1:4]]
        resp.append((v[0], v[1], v[2], v[3], v[4], v[5], star))
    i1 = next(i for i, l in enumerate(lines) if l.strip().startswith("Hz") and "dBFS" in l and "compression" not in l)
    dist = []
    for l in lines[i1 + 1:]:
        if not l.strip() or l.strip().startswith("("):
            break
        v = nums(l)
        dist.append((v[0], v[1], v[2], v[3]))
    resp, dist = np.array([r[:6] for r in resp]), np.array(dist)
    stars = np.array([r[6] for r in [(0, 0, 0, 0, 0, 0, s) for s in []]]) if False else None
    levels = [-30, -22, -14]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2))
    ax = axs[0]
    for j, (lv, col) in enumerate(zip(levels, ("#9bc4e2", "#4b9acb", BLUE))):
        ax.semilogx(resp[:, 0], resp[:, 1 + j], color=col, marker="o", ms=3, lw=1.6, label=f"sweep at {lv} dBFS")
    ax.set_xlim(10, 180)
    logticks(ax, [10, 16, 25, 40, 63, 100, 160], 10, 180)
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB re the highest point of any sweep")
    ax.set_title("Sub range (LFE only, through CamillaDSP)")
    ax.axvspan(10, 22, color="#f1f1f1", zorder=0)
    ax.text(10.5, -5, "mic and USB input\nroll off", fontsize=7.5, color="#777")
    ax.legend(fontsize=7.5, loc="lower right")
    ax = axs[1]
    for j, (lv, col) in enumerate(zip(levels, ("#9bc4e2", "#4b9acb", BLUE))):
        pct = 100 * 10 ** (dist[:, 1 + j] / 20)
        ax.semilogx(dist[:, 0], np.minimum(pct, 100), color=col, marker="o", ms=3, lw=1.6, label=f"{lv} dBFS")
    ax.axhline(10, color=RED, ls="--", lw=0.8)
    ax.text(70, 11, "10 %", color=RED, fontsize=8)
    ax.set_yscale("log")
    ax.set_ylim(0.2, 120)
    logticks(ax, [12, 16, 25, 40, 63, 90], 12, 95)
    ax.set_xlabel("Hz")
    ax.set_ylabel("harmonics 2-5 at the mic (% of the fundamental)")
    ax.set_title("Distortion (below about 1 % is room noise)")
    ax.legend(fontsize=7.5)
    ax = axs[2]
    comp = resp[:, 5]
    ax.axhline(0, color="k", lw=0.5)
    ax.axhspan(-1.5, 1.5, color=GREY, alpha=0.15, lw=0)
    okf = resp[:, 0] >= 22
    ax.semilogx(resp[okf, 0], resp[okf, 4], color=BLUE, marker="o", ms=3, label="-30 to -22 dBFS")
    ax.semilogx(resp[okf, 0], resp[okf, 5], color=ORANGE, marker="o", ms=3, label="-22 to -14 dBFS")
    ax.set_ylim(-3, 4)
    logticks(ax, [25, 40, 63, 100, 160], 22, 180)
    ax.text(0.03, 0.04, "below 22 Hz: mic and noise,\nnot shown", transform=ax.transAxes, fontsize=7.5, color="#777")
    ax.set_xlabel("Hz")
    ax.set_ylabel("compression (dB; 0 = linear)")
    ax.set_title("Compression between levels")
    ax.legend(fontsize=7.5)
    save(fig, "06_sub_range_and_distortion", "Real recording (sub-sweep.wav), tools/subtest analyser: three 8-200 Hz sweeps on the LFE channel. The mic and its USB input roll off below about 20 Hz, so read the comparison between levels, "
         "not the absolute bottom. Compression is shown from 22 Hz up (below that the mic and room noise dominate and the values swing wildly): about 2 to 3 dB between -30 and -22 dBFS at 22-25 Hz, none above 35 Hz. 'Clean' in the README means harmonics below -30 dB (3 %), the analyser's own scale: 2 % at 40 Hz at -14 dBFS, 5 % at 36 Hz. Distortion estimates below about -45 dB are room noise.")
    # --- rattle hunt, from the report table
    i2 = next(i for i, l in enumerate(lines) if l.strip().startswith("Hz") and "level(q)" in l)
    tones = []
    for l in lines[i2 + 1:]:
        if l.strip().startswith("(") or not l.strip():
            break
        a, b = l.split("|")[0], l.split("|")
        v = nums(a) + nums(b[1]) + nums(b[2])
        tones.append(v[:9] if len(v) >= 9 else None)
    tones = np.array([t for t in tones if t is not None])
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4))
    ax = axs[0]
    ax.axhline(5, color=RED, ls="--", lw=0.9)
    ax.text(-0.4, 5.8, "analyser flags a rise above 5-8 dB (if the non-tone energy is also high)", fontsize=7.5, color=RED)
    ax.axhline(0, color="k", lw=0.5)
    ax.bar(range(len(tones)), tones[:, 8], color=[BLUE if v <= 3 else ORANGE for v in tones[:, 8]])
    ax.set_xticks(range(len(tones)))
    ax.set_xticklabels([f"{f:g}" for f in tones[:, 0]], rotation=60, fontsize=7.5)
    ax.set_xlabel("tone, Hz")
    ax.set_ylabel("growth of non-tone energy when 10 dB louder (dB)")
    ax.set_ylim(-30, 12)
    ax.set_title(f"Rattle hunt: {len(tones)} tones, worst rise {tones[:, 8].max():+.0f} dB")
    ax = axs[1]
    ax.plot(tones[:, 0], tones[:, 5], color=BLUE, marker="o", ms=3, label="harmonic distortion, loud pass")
    ax.plot(tones[:, 0], tones[:, 7], color=ORANGE, marker="o", ms=3, label="everything else (noise, buzz), loud pass")
    ax.set_xscale("log")
    logticks(ax, [25, 40, 63, 100, 160], 24, 210)
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB below the tone")
    ax.set_title("What accompanies each tone at -14 dBFS")
    ax.legend(fontsize=7.5)
    save(fig, "16_rattle_hunt", "Real recording (sub-sweep.wav), tools/subtest part 2: 19 steady tones, a quiet pass at -24 dBFS then a loud pass at -14 dBFS. A perfectly linear system shows a 10 dB gain and no rise. "
         "The analyser flags no tone. This pass is at -14 dBFS; film bass can be louder (see the hot run).")
    return resp, dist, tones


# ------------------------------------------------------------------------------------------------ hot sub run
def hot_figure(path):
    x = SUB.load_mono(path)
    a, b, how = SUB.placement(x, CSUB)
    loud = [t for t in CSUB["tones"] if t["pass"] == 1]
    rows = []
    for tn in loud:
        t0 = a + b * tn["t"] + 1.0
        seg = x[int(t0 * FS):int((t0 + 2.6) * FS)]
        pk = np.abs(seg).max()
        rows.append((tn["f"], pk, np.mean(np.abs(seg) >= 0.98 * pk)))
    rows = np.array(rows)
    ceiling = rows[:, 1].max()
    fig = plt.figure(figsize=(12, 4.6))
    gs = fig.add_gridspec(2, 3)
    ax = fig.add_subplot(gs[:, 0])
    ax.bar(range(len(rows)), 20 * np.log10(rows[:, 1]), color=[RED if r > 0.9 * ceiling else BLUE for r in rows[:, 1]])
    ax.set_ylim(-25, 0)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([f"{f:g}" for f in rows[:, 0]], rotation=60, fontsize=7.5)
    ax.set_xlabel("loud tone, Hz")
    ax.set_ylabel("recording peak (dBFS)")
    ax.set_title("Peak of each loud tone in the recording")
    ax.text(0.03, 0.06, f"red: within 10 % of the highest peak\n({20 * np.log10(ceiling):.1f} dBFS, at {ceiling:.3f})", transform=ax.transAxes, fontsize=7.5)
    axw = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 2])]
    for ax, fq in zip(axw, (40, 50, 56, 71)):
        tn = [t for t in loud if t["f"] == fq][0]
        t0 = a + b * tn["t"] + 1.5
        seg = x[int(t0 * FS):int((t0 + 0.12) * FS)]
        ax.plot(np.arange(len(seg)) / FS * 1000, seg, color=BLUE, lw=1)
        ax.axhline(ceiling, color=RED, lw=0.7, ls="--")
        ax.axhline(-ceiling, color=RED, lw=0.7, ls="--")
        ax.set_ylim(-0.7, 0.7)
        ax.set_title(f"{fq} Hz", fontsize=8, pad=2)
        ax.set_xlabel("ms", fontsize=7)
    n_cap = int(np.sum(rows[:, 1] > 0.98 * ceiling))
    fig.suptitle(f"Hot sub run: {n_cap} of {len(rows)} loud tones peak at the same level, {ceiling:.3f} (dashed), whatever their frequency", fontsize=9.5)
    save(fig, "17_hot_sub_run", "Real recording (subtest-hot.wav), loud pass. The same peak on every tone from 31.5 to 71 Hz is what a limiter or a capped input does; a resonance or a rattle would not behave the same at eight frequencies. "
         "The 50 and 71 Hz waveforms are clean sines that just reach the cap, while 40 and 56 Hz are visibly distorted. This recording cannot say whether the limit is in the sub path or the capture chain; a quieter run with the mic farther away would show. The distortion figures (fig 06) were taken at -14 dBFS, below this cap, but that does not prove the capture chain is linear up to it.")
    return rows, ceiling


# ------------------------------------------------------------------------------------------------ dialogue
def dialogue_figure(path):
    DL = load("dlgan", sib("theater-measurement", "tools", "dialoguetest", "analyze-dialoguetest.py"))
    txt = run_report(DL, path, ["--out=" + os.devnull])
    lines = txt.splitlines()
    i = next(k for k, l in enumerate(lines) if l.strip().startswith("Hz") and "FC-FLFR" in l)
    resp = []
    for l in lines[i + 1:]:
        v = nums(l)
        if len(v) != 3 or (resp and v[0] <= resp[-1][0]):
            break
        resp.append(v)
    resp = np.array(resp)
    sti = {}
    for l in lines:
        for key, lab in (("noise-free", "IR, no noise"), ("with the measured noise", "IR + noise"), ("direct, from the recorded", "direct, centre"), ("same signal on FL+FR", "direct, phantom")):
            if key in l and ":" in l:
                sti[lab] = nums(l.split(":")[-1])[0]
    j = next(k for k, l in enumerate(lines) if "octave band (Hz)" in l)
    bands = nums(lines[j])
    noi = nums(lines[j + 1].split(":")[1])
    dia = nums(lines[j + 2].split(":")[1])
    c50 = [float(v) for v in re.findall(r"C50 \(dB\):\s+(.*)", txt)[0].split()]
    rt = [float(v) for v in re.findall(r"RT60 \(s, T20\):\s+(.*)", txt)[0].split()]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    ax = axs[0]
    ax.axhspan(-3, 3, color=GREY, alpha=0.15, lw=0)
    ax.semilogx(resp[:, 0], resp[:, 1], color=GREEN, marker="o", ms=3, lw=1.8, label="FC re its own 500-1000 Hz level")
    ax.semilogx(resp[:, 0], resp[:, 2], color=BLUE, marker="o", ms=3, lw=1.2, label="FC re the mean of FL and FR")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylim(-8, 15)
    logticks(ax, [100, 200, 500, 1000, 2000, 5000], 90, 9000)
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB, 1/3 octave")
    ax.set_title("Centre speaker, speech-band response")
    ax.legend(fontsize=7.5, loc="upper right")
    ax = axs[1]
    labs = list(sti)
    vals = [sti[k] for k in labs]
    ax.axhspan(0.75, 1, color="#e8f3ec", lw=0)
    ax.bar(range(len(vals)), vals, color=["#9bc4e2", "#4b9acb", GREEN, BLUE][:len(vals)], width=0.6)
    for k, v in enumerate(vals):
        ax.text(k, v + 0.01, f"{v:.2f}", ha="center", weight="bold")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_ylim(0.4, 1.0)
    ax.set_ylabel("STI (STIPA-style)")
    ax.set_title(f"Intelligibility; C50 {np.mean(c50[:3]):+.1f} dB, RT60 {min(rt):.2f}-{max(rt):.2f} s")
    ax.text(-0.4, 0.955, "green: excellent (> 0.75)", fontsize=7.5, color="#3a7")
    ax = axs[2]
    ax.plot(range(len(bands)), dia, color=GREEN, marker="o", lw=2, label="dialogue at the seat")
    ax.plot(range(len(bands)), noi, color=GREY, marker="s", lw=2, label="room noise floor")
    ax.fill_between(range(len(bands)), noi, dia, color="#e8f3ec")
    for k in range(len(bands)):
        ax.text(k, (dia[k] + noi[k]) / 2, f"{dia[k] - noi[k]:.0f}", ha="center", va="center", fontsize=8, weight="bold")
    ax.set_xticks(range(len(bands)))
    ax.set_xticklabels([f"{b:g}" for b in bands])
    ax.set_xlabel("octave band, Hz")
    ax.set_ylabel("dBFS (uncalibrated)")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Dialogue to noise (dB shown in the fill)")
    save(fig, "07_dialogue", "Real recording (dlg1.wav, one seat, one mic position; the recording stopped before the end chirps). Differences under about 2 dB per band or 0.03 STI are within repeatability. "
         "STI is a STIPA-style estimate without auditory masking, not a certified measurement; the 'IR, no noise' bar is the room alone and is not a listening condition. Noise-floor values above 4 kHz may be the capture chain's own floor. The state of the projector fan during the noise measurement was not recorded. Boom 100-200 Hz +5.7 dB and presence 2-4 kHz -3.3 dB re 500-1000 Hz.")
    return sti


# ------------------------------------------------------------------------------------------------ film clips
def welch_db(x, fs=FS, nper=1 << 16):
    f, p = welch(x, fs, nperseg=nper, noverlap=nper // 2)
    return f, p


def third_bands(f, p, centres):
    out = []
    for c in centres:
        m = (f >= c * 2 ** (-1 / 6)) & (f < c * 2 ** (1 / 6))
        out.append(10 * np.log10(p[m].sum() + 1e-30) if m.any() else np.nan)
    return np.array(out)


def align_pair(a, b):
    """Offset (samples) that best aligns b to a, from the >500 Hz band (the part the EQ does not change)."""
    sos = butter(4, 500, btype="high", fs=FS, output="sos")
    ha, hb = np.abs(sosfiltfilt(sos, a)), np.abs(sosfiltfilt(sos, b))
    ha, hb = ha[::48], hb[::48]
    ha, hb = ha - ha.mean(), hb - hb.mean()
    r = fftconvolve(ha, hb[::-1], mode="full")
    return (int(np.argmax(r)) - (len(hb) - 1)) * 48


def tenet_figure(p_direct, p_drone):
    d, e = mono(p_direct), mono(p_drone)
    off = align_pair(d, e)
    if off > 0:
        d = d[off:]
    else:
        e = e[-off:]
    n = min(len(d), len(e))
    d, e = d[:n], e[:n]
    lo = butter(4, [25, 130], btype="band", fs=FS, output="sos")
    hi = butter(4, 500, btype="high", fs=FS, output="sos")
    rms = lambda y: 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-12)
    sec = np.arange(n // FS)
    bl_d = [rms(sosfiltfilt(lo, d)[s * FS:(s + 1) * FS]) for s in sec]
    bl_e = [rms(sosfiltfilt(lo, e)[s * FS:(s + 1) * FS]) for s in sec]
    hf_d = [rms(sosfiltfilt(hi, d)[s * FS:(s + 1) * FS]) for s in sec]
    hf_e = [rms(sosfiltfilt(hi, e)[s * FS:(s + 1) * FS]) for s in sec]
    s0 = max(0, n - 15 * FS)
    cent = np.array([25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250])
    fd, pd_ = welch_db(d[s0:])
    fe, pe = welch_db(e[s0:])
    delta = third_bands(fe, pe, cent) - third_bands(fd, pd_, cent)
    pred = np.array([sum(SE.peaking_db(c, f0, g, q) for _, f0, g, q in SE.FILTER_SETS["drone2"]) for c in cent])
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    ax = axs[0]
    ax.plot(sec, bl_d, color=GREY, lw=1.6, label="direct, 25-130 Hz")
    ax.plot(sec, bl_e, color=ORANGE, lw=1.6, label="drone2, 25-130 Hz")
    ax.plot(sec, hf_d, color="#bbb", lw=1, ls=":", label="direct, above 500 Hz")
    ax.plot(sec, hf_e, color="#f0b27a", lw=1, ls=":", label="drone2, above 500 Hz")
    ax.set_xlabel("s")
    ax.set_ylabel("dBFS rms per second")
    ax.set_title(f"Level over time (peaks {20 * np.log10(np.abs(d).max()):.1f} / {20 * np.log10(np.abs(e).max()):.1f} dBFS)")
    ax.legend(fontsize=7.5)
    ax = axs[1]
    ax.semilogx(cent, pred, color=ORANGE, lw=2, label="predicted (drone2 filters)")
    ax.semilogx(cent, delta, color=BLUE, marker="o", lw=1.4, label="recorded: last 15 s, drone2 minus direct")
    ax.axhline(0, color="k", lw=0.5)
    logticks(ax, [25, 40, 63, 100, 160, 250], 22, 280)
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB")
    ax.set_title(f"Band change: rms mismatch {np.sqrt(np.mean((pred - delta) ** 2)):.1f} dB")
    ax.legend(fontsize=7.5, loc="lower right")
    ax = axs[2]
    m = (fd >= 30) & (fd <= 130)
    ax.plot(fd[m], 10 * np.log10(pd_[m] + 1e-30), color=GREY, lw=1.2, label="direct")
    ax.plot(fe[m], 10 * np.log10(pe[m] + 1e-30), color=ORANGE, lw=1.2, label="drone2")
    for fq in (48, 56, 64):
        ax.axvline(fq, color="#f59e0b", lw=0.8, ls=":")
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB (arbitrary reference)")
    ax.set_title("Last 15 s, fine spectrum (dotted: 48, 56, 64 Hz)")
    ax.legend(fontsize=7.5)
    save(fig, "03_drone2_predicted_vs_recorded", "Real recordings: Tenet 'freeport', direct against drone2, aligned on the >500 Hz band (which the EQ does not change). The recorded change in the last 15 s is compared with the change the drone2 filters predict. "
         "One film scene; the last 15 s hold most of the bass energy, so the comparison is only as broad as that scene. Neither recording clips. Raw recordings of copyrighted film audio are not in the repository.")
    return cent, pred, delta


def amaze_figure(path):
    x = mono(path)
    lo = butter(4, [25, 80], btype="band", fs=FS, output="sos")
    env = np.abs(sosfiltfilt(lo, x))
    sm = np.convolve(env, np.ones(2400) / 2400, mode="same")[::480]
    from scipy.signal import find_peaks
    pk, _ = find_peaks(sm, distance=150, height=np.percentile(sm, 90))
    top = sorted(pk, key=lambda i: -sm[i])[:5]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    ax = axs[0]
    ff, tt, Sx = spectrogram(x, FS, nperseg=2 ** 15, noverlap=2 ** 15 - FS // 4, window="hann")
    mm = (ff >= 30) & (ff <= 200)
    Z = 10 * np.log10(Sx[mm] + 1e-20)
    pm = ax.pcolormesh(tt, ff[mm], Z, vmin=Z.max() - 55, vmax=Z.max(), shading="auto", cmap="viridis")
    fig.colorbar(pm, ax=ax, label="dB re the loudest cell (uncalibrated)", pad=0.01)
    ax.axhline(100, color="white", lw=0.7, ls=":")
    ax.set_xlabel("s")
    ax.set_ylabel("Hz")
    ax.set_title("Dolby Amaze recording: bass hits, 30-200 Hz (dotted: 100 Hz)")
    ax = axs[1]
    cols = plt.cm.viridis(np.linspace(0, 0.9, len(top)))
    lines = []
    for c, i in zip(cols, sorted(top)):
        t = i * 0.01
        seg = x[int((t - 0.15) * FS):int((t + 0.65) * FS)]
        f, p = welch(seg, FS, nperseg=len(seg), noverlap=0)
        m = (f >= 25) & (f <= 220)
        pd = 10 * np.log10(p + 1e-30)
        ref = pd[m].max()
        ax.plot(f[m], pd[m] - ref, color=c, lw=1.1, label=f"hit at {t:.0f} s")
        fund = f[m][np.argmax(pd[m])]
        k100 = (f >= 97) & (f <= 103)
        lines.append((t, fund, pd[k100].max() - ref))
    ax.axvline(100, color=RED, lw=0.8, ls=":")
    ax.set_xlabel("Hz")
    ax.set_ylabel("dB re each hit's strongest component")
    ax.set_ylim(-70, 3)
    ax.set_title("Spectrum of five bass hits: the 100 Hz line")
    ax.legend(fontsize=7.5)
    save(fig, "18_amaze_buzz", "Real recording (Dolby Amaze, the loud-scene buzz), 25-200 Hz. The left panel shows the bass hits, mostly 35-65 Hz, and one sustained tonal passage near 100 Hz at the end (58-62 s). "
         "The right panel overlays the spectra of five hits: none shows a line at 100 Hz that stays put whatever the note, which is what a rattle or a ringing room mode would look like. "
         "So this clip does not by itself locate the buzz; the stepped-tone rattle hunt (fig 16) found nothing either.")
    return lines


def presets_figure(p_direct, p_thump, p_tight):
    d, a, b = mono(p_direct), mono(p_thump), mono(p_tight)
    n = min(len(d), len(a), len(b))
    cent = np.array([25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250])
    fd, pd_ = welch_db(d[:n])
    base = third_bands(fd, pd_, cent)
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    rows = {}
    for key, x, col in (("thump20x", a, BLUE), ("tight20x", b, ORANGE)):
        f, p = welch_db(x[:n])
        rec = third_bands(f, p, cent) - base
        pred = np.array([sum(SE.peaking_db(c, f0, g, q) for _, f0, g, q in SE.FILTER_SETS[key]) for c in cent])
        ax.semilogx(cent, rec, color=col, marker="o", lw=1.4, label=f"{key}: recorded")
        ax.semilogx(cent, pred, color=col, lw=1.2, ls="--", label=f"{key}: predicted")
        rows[key] = (rec, pred)
    ax.axhline(0, color="k", lw=0.5)
    logticks(ax, [25, 40, 63, 100, 160, 250], 22, 280)
    ax.set_xlabel("Hz")
    ax.set_ylabel("change vs direct (dB), whole clip")
    ax.set_title("Two earlier presets: recorded against predicted change")
    ax.legend(fontsize=8)
    save(fig, "19_presets_recorded_vs_predicted", "Real recordings (direct2, thump20x, tight20x, 51 s clips, band energy over the whole clip). Differences also include any playback-level change between files. tight20x follows its prediction closely; thump20x "
         "falls 4-6 dB below its prediction at 25-35 Hz (the mic and the sub's low end are not reliable there) and is close elsewhere. Treat this as rough.")
    return rows


def main():
    ap = argparse.ArgumentParser()
    for k in ("sweep1", "sweep2", "sub", "hot", "dlg", "tenet-direct", "tenet-drone2", "amaze", "direct", "thump", "tight"):
        ap.add_argument("--" + k)
    a = ap.parse_args()
    if a.sweep1 and a.sweep2:
        sweep_figures(a.sweep1, a.sweep2)
    if a.sweep2:
        reflection_figure(a.sweep2)
    if a.sub:
        sub_figures(a.sub)
    if a.hot:
        hot_figure(a.hot)
    if a.dlg:
        dialogue_figure(a.dlg)
    if a.tenet_direct and a.tenet_drone2:
        tenet_figure(a.tenet_direct, a.tenet_drone2)
    if a.amaze:
        amaze_figure(a.amaze)
    if a.direct and a.thump and a.tight:
        presets_figure(a.direct, a.thump, a.tight)


if __name__ == "__main__":
    main()
