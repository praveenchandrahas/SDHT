# Changelog

## 2026-10-27
- **seekthumbs web page** (`./seekthumbs.py serve`): one row per film (releases grouped), tick films, queue, **Start / Pause / Resume / Stop / Stop after this film**, with panels for the film being read (wake, probe, read, save), thumbnails per second, network use of the whole computer, time per film, coverage, store size and the queue; light and dark, phone width, a Table view for every chart. Listens on 127.0.0.1 only; a token on every request, a Host check, and it can only queue films it listed itself. Tested with a synthetic library (unit tests and a headless browser); the owner ran it on the real mount in the evening.
- **seekthumbs, cold files on a debrid mount:** a wake read before probing, a `probe_timeout` setting (a hung `ffprobe` no longer counts as a failure: the film goes to the back of the queue and is tried again), wake-ahead of the next films, per-film wake/probe/read timings in the log, and a progress line every 60 s.
- **What the mount measured** (the owner's, one evening): the first touch of a cold file 24 s to 4 min; reads elsewhere in the file about 1.5 s per 4 MB; streaming 11.6 MB/s on a 200 Mbps line; 8 parallel reads only 1.1-2 times faster than serial; one 4K remux built in 18.3 min in a batch pass (0.5 thumbnails/s, 8 decode retries). The `probe` command projected under a minute per film and was far too optimistic (it samples 6 thumbnails). Earlier assumption that parallel reads would hide the latency was wrong.
- **seekthumbs viewer:** `install-viewer` run on the rig (uosc already present); hover preview on the seek bar confirmed working in real mpv for a finished film. The on-play build trigger is still untested in real mpv.
- **mpv-shelf:** installed on the rig (635 files = 195 entries); a dropped TLS handshake no longer ends the TMDB fetch (3 retries, a title that still fails is skipped, give up after 3 in a row). Ctrl+b confirmed working in real mpv; the mpv overlay `c` key confirmed working after the installer fix.
- **theater-ctld autostart:** the installer already enables the page (`enable --now`, WantedBy default.target) so it starts with the desktop session; `install-ctld.sh` now prints the autostart and linger state (and the one command for starting at boot without a login), and `scripts/check-installed.sh` reports whether the unit is enabled.
- READMEs: sibling lists in every repository now name all six; mpv-object-audio gained a short "optional companions" section; seekthumbs gained the web page, the measurements, the new settings and a note on its tests.

## 2026-10-26 (evening)
- **Roomtone control page:** live sound field (per-speaker levels of the 8 outputs on a 5.1.2 plan, after EQ, from CamillaDSP at 20 Hz), a redesigned page, and an **autocal page** (live run, prompts, stop, start from a fixed list of runs, apply with confirmations; never changes the safety limits). Checked against a simulated CamillaDSP and, for the levels, on the rig.
- **autocal:** a 20 s silent recording before and after every position is the noise reference for the 40 Hz SNR (kept in `raw/`); the sub second-harmonic stop needs 0.6 s of persistence (or -6 dBc at once) and saves the last 2 s of the mic when it stops. Limit (-20 dBc) and the -20 dBFS cap unchanged. An open question: the new reference and the in-sweep estimate disagree by about 11 dB on one run (22 vs 11 dB).
- **mpv overlay installer:** fixed a bug that wrote the terminal height (`42`) into input.conf instead of the key line (a bash variable named LINES).
- **seekthumbs:** builds when you play a film (`build FILE`, started by the viewer), one set shared by releases of a film (aliases), `skip_tv` / `exclude`, decode errors on a flaky mount count as failed reads (retried), `verify --deep`. On the owner's debrid mount PyAV read 9.8 MB per thumbnail against 62.7 MB for the ffmpeg command.
- **mpv-shelf** (new repository): film browser for mpv over the library folder. Version 1, tested against a mocked mpv only.

## 2026-10-26: Roomtone
- `theater-measurement` renamed **Roomtone** on GitHub (history kept, old address redirects). The status page (`theater-ctld`, `web/`) moved in from linux-theater-dsp as `gui/`, the mpv overlay from mpv-object-audio as `overlay/`; the router and the CamillaDSP generator stay in linux-theater-dsp.
- mpv overlay: one **C** key opens the status and the controls together; each control row shows its current value.
- autocal: `mic --spectrum` (noise floor per octave band, strongest narrow tone); the sub sweep starts at 35 Hz; a bass gate stops runs whose 40 Hz signal-to-noise is too low.
- Status page: the buffer-empty count is shown only while something plays (CamillaDSP logs it about every 21 ms when idle).
- Profile switches reload CamillaDSP in place (no restart).

## 2026-10-25: repository split
- Split into five repositories (sdht, linux-theater-dsp incl. the upmixers, mpv-object-audio, seekthumbs, theater-measurement incl. the drift tracker) with history preserved; see docs/repo-split.md.
- `scripts/clone-all.sh`, `scripts/test-all.sh`; `preflight` and the figure scripts now read the sibling repositories.

## 2026-10-23
- `tools/dialoguetest/` (dialogue test kit: FC response, phantom vs real centre, C50/RT60/STI, noise) and `tools/reflecttest/` (early-reflection analysis and panels A/B method).
- `set-eq.py`: `--heights` (LR4 high-pass on the heights, their bass summed into the LFE), `--heights-hp/-lfe/-delay/-invert`,
  `--heights-tone` (fitted tone filters and trim), and the standing profile (no arguments or `--default`).
- `theater-route`: `eq ensure` (starts CamillaDSP and the router if down); `eq status` reports the heights processing.
- `scripts/make-default.sh`; `mpv-atmos` calls `eq ensure` first.
- `tools/sweeptest/`, `tools/subtest/`: measurement through CamillaDSP (alignment, heights fit, sub range, rattle hunt).
- Docs: alignment verification, heights section, sub range and the Amaze buzz investigation, decisions D14-D17.

## 2026-10-24
- README review (blind reviewer plus a reviewer with the project context): at-a-glance block, glossary, uncertainty paragraph, safety note, authorship moved up and made explicit about the AI-written analysers; claims reworded to "measured at one seat"; sub arrival, dialogue and reflection wording corrected.
- Figures: 01 annotations on the true peaks, 10 right panel split, 11 says synthetic and defines its metric, 15 levels, 06 compression panel, 18 colour scale; `06_sub_and_room_modes.png` renamed `20_room_modes.png`.
- `tools/make-recording-graphs.py`: redraws the recording-based figures (03, 06 range, 07, 08/08b, 12 to 19) from the raw recordings; `make-graphs.py` no longer draws 03, 07, 08.
- `tools/subtest/analyze-subtest.py`: placement falls back to the loudest sweep when the sync chirps are faint or doubled.
- `docs/status.md`: dialogue kit now measured in the room; sub arrival measured (about 7 ms after FL, not compensated); Amaze/hot-run findings revised.
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
