# autocal: an automated room-calibration run for the SDHT rig (plan, not built)

Honest framing: this room's numbers already exist and are verified (ALIGN, drone2, heights tone). autocal's value is **repeatability when something changes** (desktop PC, moved speaker, T670, the next room), not better sound today. Success test: in the current room it must rediscover the hand-derived numbers within scatter (delays +-0.3 ms, trims +-1.5 dB, heights tone within ~3 dB rms).

## 1. Reuse vs new

| Need | Existing | New / change |
|---|---|---|
| Stimulus, sync chirps, 8-ch sweeps | `theater-measurement/tools/sweeptest/make-sweeptest.py` (+cues json) | `autocal/stimulus.py`: per-channel band and level limits, pilot chirp before each sweep, repeat-FL slot |
| Placement, drift fit, deconvolution, arrival, level, complex H | `analyze-sweeptest.py` (`placement`, `deconv`, `arrival`, `spectrum`, `thirds`); `analyze-delaytest.py` fit | `autocal/ir.py`: copied out as an importable library (the scripts are hyphenated CLIs with `load_mono`/`chirp` duplicated 5 times); golden tests prove identical output before the old tools are touched |
| Mic cal; drift | `tools/miccal.py`; `drifttest/drift.py` (phase 4 only) | none |
| Height bass/tone study | `design()` in analyze-sweeptest | `autocal/heights.py` (same search, emits data not a command) |
| Recording | `scripts/rec.sh` | `autocal/audio.py`: `pw-record` piped to python for live metering and instant abort |
| Config generation, restart, relink | `set-eq.py` `build_config`, `relink` | refactor: ALIGN, HEIGHT_TONE and filter lists passed in (today module globals), loaded from one `room.json`; matches the open to-do "separate room data from code"; `test_seteq.py` must keep passing |
| Fake PipeWire | `tests/fake-pw-link` (links only) | `autocal/sim/` (section 7) |
| EQ fitter | **none in the repos**: the hump/drone sets are pasted results, their fitting code was not kept | new `autocal/eqfit.py` |
| `play-through-camilla.sh` | **referenced by 4 READMEs, not in any repo** | locate or rewrite (needed for verify) |

New CLI `autocal {check,run,report,apply,keep,rollback,verify}`, living in `theater-measurement/autocal/` (no sixth repo). It finds `set-eq.py` via the sibling-workspace convention of `test-all.sh`.

## 2. Measurement sequence

Measure **raw hardware**: `pw-play --target <USB sink>` as in alignment.md, bypassing CamillaDSP. This needs no config swap; it needs mpv/Chrome idle (abort if any other stream is on the sink).

1. Preflight (10 s): mic found, no other streams, CamillaDSP profile noted, noise floor 8 s (projector fan ON: viewing condition).
2. Level ramp (about 30 s): FL pink bursts from -60 dBFS in 6 dB steps until the mic peaks near -20 dBFS; hard cap -20 dBFS generator level (the proven sweep level).
3. Channel ID (16 s): quiet chirp per speaker. Catches swapped or dead channels and wrong mic.
4. Main run (about 100 s): start sync block, 8 sweeps of 7 s + 2 s tail, FL repeated, end sync block.

**One position: about 3 min.** **Five positions: about 15 min.** Layout: seat centre (weight 2) plus 20 cm left, right, fore, aft, at ear height. Prompt: terminal text ("Move mic 20 cm LEFT, press Enter") plus a beep. The script checks the move happened: arrival deltas of FL/FR/SL/SR should shift about 0.3-0.6 ms; none, or over ~1.2 ms, prompts a retry (direction is not verified). Positions 2-5 skip ramp/ID but keep a clipping check. Audyssey's 8 positions serve several seats; 5 around one head is the compromise. Fewer than 3 is one-point tuning, as today.

## 3. Algorithms

- **IR/arrival/delay.** Sync-chirp placement with linear clock fit (abort above 300 ppm disagreement, existing rule), log-sweep deconvolution, 300-4000 Hz envelope 50% crossing. Delay = arrival minus the farthest speaker's (delays only added, as now). A per-slot pilot chirp checks for xruns. Existing method agreed within 0.2 ms.
- **Level.** 500-2000 Hz band energy of the gated response (not peak). Trims <= 0 against the loudest bed speaker. Sub knob untouched; sub-to-main level is reported only.
- **Polarity.** Never from one lobe or correlation (lesson in alignment.md). Predict the in-phase and inverted sums from two time-referenced complex IRs, 150-800 Hz; propose inversion only if inverted wins by >=3 dB at >=3 of 5 positions. Otherwise report only.
- **Sub vs mains: limited by the Z906.** Every Z906 channel and the LFE feed the same internal sub through fixed internal filters. Delaying a satellite delays its sub feed too, so sat-to-sub phase cannot be adjusted. What we can do: measure and report the 6-7 ms sub lag and group delay (status.md), tune LFE-vs-bed delay/polarity where they sum in the sub, and tune the heights' bass path (`design()`; already shown to matter little). A real crossover alignment exists only for the T670 (phase 4).
- **Bass EQ (common to all Z906 channels, as `CHANNELS` is today).** Spatial average below ~100 Hz is power average; 100-250 Hz uses the **consensus cut**: cut = 25th percentile across positions of (response minus target), clamped >= 0. Greedy fit on 1/6-octave data: cut at the largest peak, Q from its -3 dB width, recompute; stop at peaks < 2 dB or < 0.3 dB rms gain per filter. Limits: cut only (max boost 0, optional +3 dB, Q<=2, off by default), max cut -15 dB per filter, Q <= 5 (6 above 100 Hz), <= 8 filters, nothing above ~250 Hz (Schroeder estimate for this room, unmeasured). A null is skipped when depth > 6 dB below the neighbours' smoothed level, or if it moves between positions. Taste cuts (drone2's 72/84 Hz) live in an overlay list that autocal carries over unchanged and cannot rediscover.
- **Target.** Flat: tried, "lean and hollow" (tuning-log). House curve (gentle +3 to +6 dB LF rise): sane default for a new room. **Owner voicing** (hump of H dB over mids at 45-90 Hz, default 20 as hump20): default here, being the verified choice. All selectable.
- **Heights tone.** Fit the error of (RL+RR)/2 against the bed power mean, 170 Hz-5 kHz, 1/3 octave, <=3 filters, Q<=3, cuts to -8 dB, HF shelf <=+4 dB. Only features both heights share and >=3 of 5 positions show. Trim from 300 Hz-4 kHz mean. Above 5 kHz is optional: elevation cues make "match the bed" questionable.
- **Hysteresis.** Changes under 1 dB or 0.15 ms keep the current value.

## 4. Safety

Generator asserts <= -20 dBFS; heights start at 100 Hz (small drivers; today's sweeps run them from 20 Hz), satellites 40 Hz, LFE 25-200 Hz; -12 dB below 35 Hz (undone in deconvolution); no steady tones. One sweep per `pw-play` call; the live meter kills it within ~250 ms on mic peak > -6 dBFS, clipped samples, sub 2nd harmonic > -20 dBc, or Ctrl-C. Abort if SNR at 40 Hz < 25 dB. The mic's capture volume acts after the clip point (tuning-log), so playback level is the only protection.

`--dry` prints the timeline and levels and plays nothing; `check` does steps 1-3 only.

**Never auto-applies.** Output `runs/<ts>/`: `report.html`, `room.proposed.json`, `config.proposed.yml` (checked with `camilladsp -c`), predicted before/after curves, raw WAVs. `autocal apply <run>` copies the live `config.yml` to `backups/` first, applies with a 60 s trial that reverts unless `autocal keep` is typed. `autocal rollback` restores the last backup via `set-eq`'s relink.

## 5. Verification and overfitting

`autocal verify` (about 2 min, after apply) re-measures through CamillaDSP at the centre **and one position not in the fit set**. Pass/fail (thresholds initial, from repo history): arrival spread <= 0.3 ms; bed level spread <= 2 dB; heights within 2 dB; 30-250 Hz rms to target <= 3 dB; no peak > 4 dB over target; prediction vs measured rms <= 2.5 dB (the repo's own noise floor is 2.3-3.0 dB across days); FL repeat <= 1 dB; no clipping. Output: PASS/WARN/FAIL table plus before/predicted/measured graphs in the style of `docs/graphs/`.

Overfitting guards: leave-one-position-out (held-out gain under half the training gain means fewer, lower-Q filters), consensus cut, Q/count caps, hysteresis, verification at an unfitted position, and comparison with the last accepted run (warn if a speaker shifts > 1.5 ms or 6 dB: mic moved, or a cable). A one-position run stays a one-point fit; the report says so.

## 6. Dumb-hardware risks

| Risk | Handling |
|---|---|
| Mic clock vs DAC | Sync chirps, linear fit; abort at > 300 ppm; `drift.py` only for T670 |
| No timing reference | In-band sync chirps (already in sweeptest) give relative delays, which is all alignment needs. Absolute distances are not needed. An electrical loopback would need a spare DAC output (none: 8 of 8 used); not planned |
| Gain/level mismatch, no SPL | Relative levels only; adapter gain after the clip; owner-supplied SPL offset optional |
| Latency / xruns | Pilot chirps and the repeat FL slot flag glitches; PipeWire quantum logged |
| Noise, fan, neighbours | Floor logged, SNR gate, sweep repeated once if SNR < 30 dB |
| Mic/adapter roll-off below ~20 Hz | No EQ below 30 Hz |
| Unknown | Z906 standby on silence; PipeWire volume on the Vantec (pin to 100%) |

## 7. Testing without hardware

`autocal/sim/room.py`: ground-truth rooms with per-channel delay, gain, polarity, modal resonators (as `room_ir` in `test_drift.py`), a Z906 sub lagging 6-7 ms, nulls, noise, +-50 ppm mic clock, clipping, a dead channel. A `Backend` interface (`SimBackend`, `PipewireBackend`) plus fake `pw-play`/`pw-record` extend `fake-pw-link` to subprocess and abort paths. Tests: recover truth; flipped speaker caught; null untouched; prediction matches simulated correction; abort on injected clipping; apply/rollback on a temp config. `data/rew/*-2026-10-19.txt` regression-tests the fitter; real recordings are not in the repo.

## 8. Phases

| Phase | What | Sandbox | Needs rig | Effort |
|---|---|---|---|---|
| 0 | Extract `ir.py`, `room.json`, parameterise `build_config`, golden tests | yes | no | 1 day |
| 1 **(minimal v1)** | Single position: preflight, ramp, ID, run, delay/trim/polarity-flag, report, proposed profile, apply/keep/rollback | yes | 1 session (1 h) to compare with ALIGN | 3 days |
| 2 | Bass EQ fitter, targets, heights tone, LFE alignment, prediction | yes | 2 sessions | 4 days |
| 3 | Multi-position, move prompts, consensus cut, verify | yes | 2 sessions (1.5 h) | 3 days |
| 4 | T670 delay/polarity/level, drift, HDMI latency | partly | yes, unknowns dominate | 3+ days |

Only the owner can validate: real SNR and clipping margins, trial/rollback across a live CamillaDSP restart, the pass/fail thresholds, and whether it sounds right.

**Recommended minimal v1: phases 0-1.** It reuses validated code, has a ground-truth check, and delivers apply/rollback and the report.

## 9. Compared with the field

Audyssey XT32 and Dirac use 8-9+ positions and FIR/mixed-phase filters, ship level-calibrated mics and have tuned psychoacoustic targets (Dirac adds sub optimisation, REW users get MSO). REW + miniDSP is manual measurement with IIR auto-fit, like ours.

We would **not** match: FIR/phase correction, Dynamic EQ and loudness psychoacoustics, many-position robustness, calibrated reference level, a GUI, years of field tuning. We can beat them on transparency, cut-only caution, an honest verify step and keeping the owner's voicing. For the T670, check whether REW/MSO already solves it before building.

## 10. Open questions

1. Raw-hardware measurement (stop the router first) or through CamillaDSP? Where is `play-through-camilla.sh`?
2. Is -20 dBFS at your usual Z906 knob acceptable for the neighbours and at what hours?
3. Keep the 20 dB hump and the drone cuts as the standing target?
4. Is 5 positions acceptable, or single position only?
5. Should heights match bed above 5 kHz?
6. Can the mic stand be moved repeatably; is the SPACETOUCH gain fixed?
7. Want an SPL reference (phone app)?
8. Build before or after the desktop move and T670?
