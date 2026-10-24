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
- `tools/make-graphs.py` and `docs/graphs/` (eleven graphs, index in its README); README appendix with the seven main ones. Curves that need the raw recordings are not redrawn (the recordings are not in the repo).
- README brought up to date (verification table, standing profile, heights, upmix, automatic profile, tool layout); `tools/make-verification-figures.py` and `docs/graphs/10_verification_summary.png`, `docs/graphs/11_upmix_adaptive_vs_fixed.png` drawn from the values recorded in status.md and the upmixtest README (raw sweep recordings are not in the repo).
- Reboot test on the real system: services and standing profile up at boot, run away from the rig (no Vantec), so routing is still to be checked at the rig (docs/status.md).
- `eq status` now says "USB interface not connected" instead of "mixed or unfinished routing" when the Vantec is absent.
- `make-subtest.py --boost=X` (+X dB on sweeps and tones, refused above -1 dBFS), `phone-to-wav.sh`, second hot-run procedure in tools/subtest/README.md.

- `scripts/upmix.py`, `set-eq.py --upmix=stereo|bed[:flavour]`: stereo -> 5.1.2 (real centre, Haas-delayed decorrelated surrounds and heights) and 5.1 -> 5.1.2 bed (ambience heights, dialogue stays front). Three flavours each. `tools/upmixtest/` measures them offline with the real CamillaDSP. Tests extended.
- `theater-route`: automatic profile. Chrome playing -> stereo upmix and Chrome patched into CamillaDSP FL/FR; mpv source read over IPC (Atmos -> film, 5.1 -> bed, stereo -> stereo upmix); idle -> film. `eq mode|flavour|source|prepare`; `mpv-atmos` selects the profile before mpv starts and opens the IPC socket. `set-eq.py` writes a `# theater-profile:` header into the config. Router tests extended (51 checks).
- Adaptive stereo upmix: `scripts/upmix_engine.py` (streaming STFT ambience extractor, 4 % of a core, 21.3 ms) feeding the surrounds and heights through a new `stereo-ad` profile in `upmix.py`; router starts/stops it as `theater-upmix.service`, links it, and falls back to the fixed matrix if it does not come up (`eq engine on|off`). Installer now also installs `set-eq.py`, `upmix.py`, `upmix_engine.py` (without them the router could not switch profiles). tests/test_engine.py; 148 checks in total.
- Decorrelators rebuilt (group-delay construction): the first version was a near plain delay (0.95-0.99 correlated below 2 kHz).

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
