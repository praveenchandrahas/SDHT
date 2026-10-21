# Installation

This repository covers the audio routing, DSP and measurement parts. The player stack (Omniphony, harletty-bridge,
mpv-omniphony) and the media library were set up before this repository existed; their steps are TODO(owner) in
section 2. Everything else below has been used on the real system, except the auto-router, which has only been
tested in simulation (see [status.md](status.md)).

## 1. Requirements

- Linux with **PipeWire** and WirePlumber (user services), and `pw-link`, `pw-record`, `pw-play`, `pactl`.
- **CamillaDSP 4.x** at `/usr/local/bin/camilladsp`, run as the user service `camilladsp.service` (an example unit:
  `configs/systemd/camilladsp.service.example`).
- **Python 3** with `numpy`, `scipy`, `pyyaml` (tools and tests) and `matplotlib` (diagram script only); `ffmpeg` for the bed test.
- A 7.1 USB audio interface exposed to PipeWire as an 8-channel sink.
- For measurements: a calibrated measurement microphone on a second audio device, and REW (V5.31.3 used).

Debian/Ubuntu-style packages: `pipewire-bin wireplumber pulseaudio-utils ffmpeg python3-numpy python3-scipy python3-yaml python3-matplotlib`.

## 2. Player stack (TODO(owner))

TODO(owner): document these, with links to the upstream projects and the versions used:

- Omniphony (liborender ABI 0.6 / 0.3.0, commit 6ffaf21, built 2026-07-24) and where it is installed
  (`~/.local/share/omniphony/lib/liborender.so.0` was seen in mpv's startup output).
- harletty-bridge version, how it is wired to mpv.
- mpv-omniphony v0.4.2 build steps (built from source; the prebuilt binary was broken).
- The `mpv-atmos` alias or script: exact command line and the `--ad-orender-library` option.
- `mpv.conf` (video side: gpu-next, tone-mapping, hardware decode).
- Media library mount (decide how much to document).

## 3. Configure the interface name

The USB interface's PipeWire name is hard-coded in four places. Check it with `pw-link -i | grep usb`:

| File | Setting |
|------|---------|
| `scripts/set-eq.py` | `USB = "..."` near the bottom |
| `scripts/route-mpv.sh` | `USB=...` at the top |
| `scripts/tone-test.sh` | `USB=...` at the top |
| `scripts/theater-route` | `THEATER_USB` environment variable, default in the file |

Default: `alsa_output.usb-0d8c_USB_Sound_Device-00.analog-surround-71`.

## 4. CamillaDSP config and service

```bash
mkdir -p ~/.config/camilladsp
./scripts/set-eq.py --set=drone2 --align=bed        # writes ~/.config/camilladsp/config.yml, restarts the service
```

(Needs `camilladsp.service` to exist first: copy the example unit to `~/.config/systemd/user/`, run
`systemctl --user daemon-reload && systemctl --user enable --now camilladsp.service`.)
`configs/camilladsp/example-drone2-bed.yml` is what this generates.

## 5. Auto-routing and the `eq` command

```bash
./scripts/install-autoroute.sh
```

This copies `theater-route` to `~/.local/bin`, links `eq` to it, writes and enables
`~/.config/systemd/user/theater-router.service`, starts it, makes sure `camilladsp.service` is enabled, and prints
`eq status`. It reports the lingering state: if the machine does not auto-login to the desktop, run
`loginctl enable-linger $USER` once so user services start at boot. Remove everything with `./scripts/install-autoroute.sh remove`.

## 6. Check it

```bash
tests/run.sh          # no hardware needed
eq status             # with a film playing
```

Then follow the reboot test in [runbook.md](runbook.md).
