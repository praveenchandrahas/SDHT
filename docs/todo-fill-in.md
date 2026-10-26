# Things only the owner can fill in

Search the docs for `TODO(owner)`. Checklist:

- [ ] **Split the repository into one repo per sub-project** (prepared 2026-10-25, see [repo-split.md](repo-split.md)): run `publish-split.sh` from the bundle (creates the four new repos on GitHub and pushes them; needs `gh auth login`), then merge the branch `split-umbrella` of this repository; check names first (linux-theater-dsp, mpv-object-audio, seekthumbs, theater-measurement)
- [ ] **Seek-bar thumbnails (`tools/seekthumbs`, see [seekthumbs.md](https://github.com/praveenchandrahas/seekthumbs#readme)), when at the laptop:** give the library path (the rclone mount) and the local store path and run the setup block in that document; send the `rclone mount` command line (or run `scripts/preflight` and send the new "mpv scripts and the library" section); `sudo apt install python3-av`; run `seekthumbs.py probe` on one film (it prints seconds and MB per thumbnail for each extractor and the projected time for 100 films); build one film (`scan --max-films 1`), play it in `mpv-object-audio` after `install-viewer` and check the log for "seek thumbnails: ..." and the hover picture; then `seekthumbs.py scan` overnight for the whole library, then `install-service --enable`

- [ ] **With the Vantec connected (the installer, the router update and a first Atmos and DTS:X play were done on 2026-10-25 without it):** play the Atmos clip with `mpv-object-audio`, then run `scripts/preflight playing` in a second terminal and send the report (does the new player go through CamillaDSP? are its ports named FL..SR?); run `scripts/preflight compare "<Atmos clip>"` and send the diff (engine version, layout, room ratios, **dialogue normalisation -8 dB**); then play the same clip on `mpv-atmos` and `mpv-object-audio` and compare level and bass by ear. Record the versions from `~/.local/opt/mpv-object-audio/VERSIONS` in [installation.md](installation.md) and decide when `mpv-atmos` is retired

- [x] Laptop model, OS and kernel version; PipeWire and WirePlumber versions: recorded 2026-10-24 in [installation.md](installation.md#2-player-stack)
- [x] `systemctl --user cat camilladsp.service`: collected (ExecStart `/usr/local/bin/camilladsp %h/.config/camilladsp/config.yml`); the example unit still needs to be compared with it
- [x] The exact `mpv-atmos` command: collected (and it is older than the repository copy, see installation.md). There is no `mpv.conf`
- [ ] Omniphony config: `~/.config/omniphony/config.yaml` contents (build steps are covered by `scripts/object-audio-install.sh`)
- [x] harletty-bridge and Omniphony install: now `scripts/object-audio-install.sh` (prebuilt releases; only mpv is built). Remaining: run it on the rig and record the versions it prints
- [ ] `pw-link -o | grep mpv` while Atmos plays and while a 5.1 file plays (see [status.md](status.md))
- [ ] Z906 sub-level and master-volume reference positions (photo in `docs/img/`)
- [ ] Exact room dimensions (notes from 2026-10-19 said about 10 x 11 ft; later 10 x 10 ft) and a floor plan with seat and speaker positions
- [ ] Add the Omniphony and mpv configuration to the backup list in [runbook.md](runbook.md#backups): `~/.config/omniphony/` (config.yaml, overlay-prefs.conf), `~/.config/mpv/` (input.conf, script-opts, scripts), `~/.local/bin/mpv-atmos`
- [ ] Decide what to keep out of a public repository (library mount details, personal details)
- [ ] Bill of materials with sources and prices
- [ ] CPU and latency of the live decode and render chain (the 4 % / 21 ms figures are for the upmix engine only)
- [ ] Whether DTS:X works on this rig
- [ ] Where the remux files come from, and a copyright note
- [x] Microphone calibration file: provided, in `data/mic/` (belongs to one Dayton iMM-6S; not applied by the recording analysers, see data/README.md)
- [ ] Mic position and playback level of the tests; projector fan state during the noise measurement
- [ ] The licence of each dependency
- [ ] Which scripts predate the 2026-10-20 to 24 working sessions
- [ ] Re-run `./scripts/collect-versions.sh --redact` with the USB interface plugged in and a film playing (loaded plugin, live links, audio devices)
- [ ] Copy `scripts/mpv-atmos` to `~/.local/bin/mpv-atmos` on the laptop (the installed one has no `eq prepare` and no IPC socket)

From the end-to-end review of 2026-10-26 (what would most raise the project's quality; see the reply in the session):
- [ ] Re-run one measurement without AI-written analysis: check one headline number (for example the FL early reflection, or the bass before/after) by hand in REW, and apply the microphone calibration file to the recording analysers
- [ ] Repeat the key measurements on a second day (re-seat the mic) to get a real repeatability figure, and add one blind A/B listening comparison for the upmix and the heights tone-match
- [ ] Separate room data from code: move the delay, trim and EQ constants out of `set-eq.py` into one config file, so another room only edits data
- [ ] Add automatic checks (a CI job running `scripts/test-all.sh`, plus a check that the installed scripts match the repositories)
- [ ] Decide what is public: the copyright and legal note for decoding Atmos/DTS:X and the source of the remux files
- [ ] Review the repository count after a month (five now; the upmixers sit in `linux-theater-dsp`, the drift tracker in `theater-measurement`)
- [ ] Re-run the analysers on the real recordings now that the microphone calibration file is applied (`tools/miccal.py`, default on), then update `docs/status.md`, the README numbers and the graphs; the published numbers were produced without it
- [ ] Correct the calibration history in `data/README.md` and `docs/measurement.md`: on 2026-10-21 Claude asked for the iMM-6S file ("I can apply it myself") and applied it in the F1/Godzilla/Tenet band-energy analysis (the `drone2` verification in `docs/status.md`); the 2026-10-24 note that the recording analysers do not apply it is right only for the sweep, sub, delay, dialogue and reflection analysers. The one-off `rec_an.py` code of that analysis is not in the repo; if you still have those recordings, re-run them through `tools/miccal.py` too
- [x] `play-through-camilla.sh` is now in `theater-measurement/scripts/` (it was written on 2026-10-23 and had never been committed; four READMEs pointed at it). Autocal plays through CamillaDSP with the same method
- [ ] **Test DTS:X detection on a real DTS:X file** (`eq source` while mpv plays it should say "DTS:X: object rendering, no upmix"); the router now matches "DTS:X" in mpv's codec profile (ffmpeg names it "DTS-HD MA + DTS:X"), tested only with simulated profile strings
- [ ] **Decide the CamillaDSP websocket** (status page and no-restart config changes): add `-p 1234 -a 127.0.0.1` to `ExecStart` of `camilladsp.service`; local only; one-line undo. Decision pending the owner
- [ ] **Decide whether a LAN listener is wanted for the status/control page** (default: no; the couch is covered by the Bluetooth keyboard and mouse)
- [ ] **Autocal decisions (2026-10-26):** measure through CamillaDSP as the baseline; keep the 20 dB hump and the `drone2` cuts as the standing target; offer both single-position and five-position runs (mic stand repeatable to about 1.5 ft; mic-adapter gain fixed at the 60 % setting); heights matched to the bed above 5 kHz only if it adds real value; no SPL app; build before the desktop move and the T670; level ramp from -50 dBFS, hard cap -20 dBFS (the owner's earlier runs were -30 to -12 dBFS at Z906 knob 50 %); see the plan in the autocal tool's README
- [ ] **Try autocal at the rig** (built and tested only against a simulated room, 2026-10-26; see `theater-measurement/autocal/README.md`): first `python3 -m autocal check` (preflight, noise floor, level ramp, channel ID: plays quiet sounds, changes nothing), then `python3 -m autocal.web` and a single-position run, compare with the hand-derived ALIGN numbers (delays within about 0.3 ms, trims within about 1.5 dB), then try five positions. Nothing is applied until you type APPLY (60 s trial, backup, `autocal rollback`)
- [ ] **autocal unknowns only the rig can settle:** real SNR and clipping margins, the `pw-record` / `pw-play --target camilladsp-capture` details (untested on hardware), the restart-and-relink path of `apply`, every pass/fail threshold (guesses), whether the 3 dB rms-to-target line is reachable (the simulation lands at about 3.8 dB), and whether it sounds right
- [ ] **Install the updated router** (`linux-theater-dsp/scripts/install-autoroute.sh`) so the installed `set-eq.py` honours the live `~/.config/camilladsp/room.json` and DTS:X is recognised; `scripts/check-installed.sh` says when it is out of date
- [ ] Possible later: status/control GUI (plan in `docs/plans/gui-plan.md`: `theater-ctld` daemon, `eq status --json`, optional mpv overlay; needs the CamillaDSP websocket decision above)
- [ ] Confirm the licences of harletty-bridge and mpv-omniphony (not verified) before redistributing anything built from them
- [ ] Try the CI and `scripts/check-installed.sh` once the repositories are on GitHub (CI runs only on GitHub's servers; the check is read-only)
- [ ] **Update the hand-installed `mpv-atmos`** (2026-10-26 preflight): the installed wrapper has no `--input-ipc-server` and does not call `eq prepare`, so the router cannot see Atmos/DTS:X in the codec profile when films start from it, and the DTS:X fix does nothing there. The repository copy has both and otherwise matches the installed one flag for flag. `check-installed.sh --diff` first, then `install -m 755 <workspace>/mpv-object-audio/scripts/mpv-atmos ~/.local/bin/mpv-atmos`
- [ ] **Install the updated router and `set-eq.py`** (`linux-theater-dsp/scripts/install-autoroute.sh`) and then `systemctl --user restart theater-router`, because `enable --now` does not restart a service that is already running. Do it when nothing is playing
- [ ] Which bridge does the engine's shared config use? `~/.config/omniphony/config.yaml` points at `~/HomeTheatre/Omniphony/libharletty_bridge.so` (the file exists, dated 29 Jul); both wrappers pass their own bridge paths on the command line. Check with `mpv-object-audio --oa-check` which one loads
- [ ] Seen on 2026-10-26 and explained: `mpv 2ch: USB interface not found` in the router log on 24 and 25 Oct was the rig tested without the Vantec connected; nothing to fix
- [ ] Set the GitHub topics ("tags") on the five repositories: `./scripts/github-topics.sh` (dry run) then `./scripts/github-topics.sh --apply` after `gh auth login`; also pin the main repository
