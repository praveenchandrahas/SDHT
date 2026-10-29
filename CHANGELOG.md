# Changelog

## 2026-10-28
- **seekthumbs daily read budget:** counts the data received while reading and pauses the queue at `daily_budget_gb` (default 150 GB; day ends at midnight Europe/Berlin, matching Decypharr's midnight-CET reset as far as one log line shows). Added after Decypharr stopped serving at about 452 GB of daily usage; it is a guard against an assumed cap, not a measured one. Overshoots by up to one film; on-play builds are counted but not blocked.
- **First resource-log measurements on the rig** (Atmos, idle and DTS:X runs, one small local file, about a minute each): no clipping or xruns, CamillaDSP load under 4.5 %, mpv 19 % and 48 % of one core, 5.9 to 6.4 GB RAM in use, 55 C without throttling, no dropped frames. Caveats recorded in docs/status.md: constant-zero buffer-level and A/V-sync probes (untested), 41 buffer-empty lines in the DTS:X run (cause not yet checked), an unexplained I/O stall in two runs, an unattributed idle CPU load of 29 %, and GPU data in only one run. Not yet measured: a 4K remux, long runs, end-to-end latency.
- **seekthumbs, two fixes after the Real-Debrid `bytes_limit_reached` stop (written and tested locally; not yet run on the rig):** over HTTP, PyAV reads through a bounded range reader (`http_chunk_kb`, 1 MiB; about 3.2 MB asked for per thumbnail against about 53 MB open-ended, on a synthetic test film; the real saving is unmeasured), and a run of `server_error_stop` (12) server errors in a row pauses all work instead of being treated as slowness. The ffmpeg-command fallback is still unbounded.
- **seekthumbs reads over the debrid server's WebDAV address (`read_url_base`) instead of the FUSE mount.** One film, the same 300 reads: 101 failed through the mount (303 s), none over HTTP (206 s; one pair of runs, HTTP second, so it may have been warmer). In the live queue 4K remux films then took about 3 to 4 minutes each, with no failed reads in the films whose logs were checked (earlier: 13 to 18 minutes), memory 0.8 to 1 GB. A film whose address answers 5XX is read through the mount instead; one Master and Commander release did exactly that (WebDAV `500` in under a millisecond on every try, the mount served it; it came after the account was disabled at 10:34). One film, Magadheera, took 17 minutes with a long stall: Decypharr's log shows 503s from 10:27 and, at 10:34, Real-Debrid refusing with `bytes_limit_reached`, after which Decypharr disabled the account. The queue's volume (about 65 MB received per thumbnail, measured once) is the likely cause of reaching the limit; not verified, and the limit itself is not known.
- **seekthumbs memory:** the guard now respects a cgroup `MemoryMax` (a 5 GiB limit killed the page at 07:40; the guard had only looked at the whole computer); a reference-cycle leak after failed reads is fixed (collect and `malloc_trim` when a decoder is dropped); `tools/memtest.py` measures a film's memory; zram swap (7.7 GB, zstd) set up by the owner. **11:11: the page was killed again** by its 5 GiB limit with `--workers 10 --worker-mem-mb 300`, a setting I recommended from a figure measured over HTTP only. Advice now: default 1000 MB per worker and a 7 GiB limit (about 6 readers) until HDR and mount memory is measured.
- **seekthumbs:** the thumbnail width default is now 400 px (was 240; sets already built keep their width, `refine` re-reads rather than stretching narrower ones; the size per film at 400 px is estimated at 1.7 to 3.6 MB, not yet measured); `refine` fills in a finer interval later from a coarse first pass; a film being read when the page stops goes back to the top of the queue; ffprobe errors are readable (no path); PyAV-to-ffmpeg fallbacks are logged, and the `built` line gives the network received per thumbnail.
- **mpv-shelf:** the owner reports it fully set up and working (TMDB key in his config, `shelf-index scan` run, tests run); the details were not recorded here.
- Docs: the sub's 6 to 7 ms late arrival is now described as judged inaudible as a delay at the seat (reasoned from thresholds and the room, not listening-tested), with the open question restated as how the sub and bed sum around the crossover (README, status.md, stack-vs-frontier.md).

## 2026-10-27
- **seekthumbs memory guard:** the terminal running the web page was stopped twice by the kernel's out-of-memory killer (15 GB laptop, 512 MB swap, 16 parallel readers at the second one). Each parallel read keeps an open decoder (about 180 MB each for 4K 10-bit HEVC without HDR tone-mapping, measured on a synthetic clip; HDR not measured). The number of readers is now cut to what the free memory allows (`worker_mem_mb` 600, `mem_reserve_mb` 3000), and seekthumbs raises its own OOM score so the kernel picks it first. Recommended on a machine like this: run the page in its own memory-capped systemd scope.
- **docs/script-ages.md** (new): which scripts predate the 2026-10-20 to 24 sessions. Result: none can be shown to; the README authorship paragraph now says so, with the limits (shallow or squashed history, no pre-10-20 chats found).
- **`scripts/resource-log`** (new, in Roomtone): records what the chain costs during a film and whether anything drops out. Problems first: CamillaDSP "buffer empty" log lines while mpv was running (and the idle baseline), clipped samples, processing load and buffer level (read-only websocket), PipeWire xruns, mpv dropped and mistimed frames and A/V sync (IPC socket), CPU temperature, clock and thermal throttling, PSI stalls, network rate. Then CPU and RAM per component and the whole-computer CPU, RAM and GPU (Intel via `intel_gpu_top --gpu-sudo`: Render/3D and Video-decode busy, clock, power; AMD and NVIDIA too). Tested against stand-in processes and fake sources (`tests/test_resource_log.py`), not on the rig. It does not measure end-to-end latency.
- Docs: versions of the new player stack recorded in the README (engine v0.7.0, harletty-bridge v0.9.0, Omniphony 55af2c5); DTS:X entry corrected (a clip played on 2026-10-25, decoding as objects not yet confirmed); to-do entries removed for the bill of materials, the mount, the HDMI path, mic position/level and projector fan state.
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
