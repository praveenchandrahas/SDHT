# Changelog

## 2026-10-23
- `tools/dialoguetest/` (dialogue test kit: FC response, phantom vs real centre, C50/RT60/STI, noise) and `tools/reflecttest/` (early-reflection analysis and panels A/B method).
- `set-eq.py`: `--heights` (LR4 high-pass on the heights, their bass summed into the LFE), `--heights-hp/-lfe/-delay/-invert`,
  `--heights-tone` (fitted tone filters and trim), and the standing profile (no arguments or `--default`).
- `theater-route`: `eq ensure` (starts CamillaDSP and the router if down); `eq status` reports the heights processing.
- `scripts/make-default.sh`; `mpv-atmos` calls `eq ensure` first.
- `tools/sweeptest/`, `tools/subtest/`: measurement through CamillaDSP (alignment, heights fit, sub range, rattle hunt).
- Docs: alignment verification, heights section, sub range and the Amaze buzz investigation, decisions D14-D17.

## 2026-10-24
- Reboot test on the real system: services and standing profile up at boot; routing showed no links in one `eq status` (docs/status.md), under investigation.
- `make-subtest.py --boost=X` (+X dB on sweeps and tones, refused above -1 dBFS), `phone-to-wav.sh`, second hot-run procedure in tools/subtest/README.md.

## 2026-10-21 (later)
- Added `docs/omniphony-debugging.md`, `docs/technical-writeup.md`, a whole-system diagram, and README credits for Omniphony, harletty-bridge and truehdd.

## 2026-10-21
- Bass presets `drone1`, `drone2`, `drone3` (punch20x plus narrow cuts at 72 and 84/88 Hz); `drone2` adopted.
- `set-eq.py`: `--align`, `--align=bed` (per-speaker delay and level trim from the 2026-10-21 chirp test) and `--invert=`.
- `make-delaytest.py`, `tools/analyze-delaytest.py`: chirp-based arrival-time and level measurement.
- `make-bedtest.py`: 5.1 bed listening test (channel order, phantom centre, pans, clicks, polarity pairs, dialogue).
- `rec.sh`: measurement-mic recorder with a clipping check.
- `theater-route` + `install-autoroute.sh`: automatic mpv -> CamillaDSP routing, `eq` on/off switch. Tested against a
  simulated PipeWire graph only.
- First version of the documentation and architecture diagram.

## 2026-10-19 to 21 (earlier work, same week)
- First REW sweeps (L R C LFE BL BR SL SR) and the flat-target filter set (`rew`), judged too lean.
- Hump and thump variants (`hump8..20`, `thump14/20`, `punch20`, `thump20x`, `punch20x`, `tight20x`) fitted to the measured seat response.
- `route-mpv.sh`, `tone-test.sh`: manual routing and tone testing through CamillaDSP.
