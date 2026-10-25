# Things only the owner can fill in

Search the docs for `TODO(owner)`. Checklist:

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
