# Software-defined home theatre (Linux, Atmos 5.1.2)

A home theatre built from free software: live object-audio (Atmos) rendering with **mpv + Omniphony**, routed
through **PipeWire** and **CamillaDSP** (bass EQ, per-speaker delay and level), out through a **7.1 USB interface**
to a **Logitech Z906** (5.1 bed) plus two height speakers on a separate amp. Everything is tuned from
measurements taken at the listening seat with a calibration microphone, and every change can be repeated or undone.

Room: 10 x 10 ft, no space behind the seat, so **5.1.2 is the largest sensible layout** (7.1.4 / 5.1.4 are
deliberately not used).

![System overview, every component](docs/img/system-overview.png)

*Every component, hardware and software. Dashed boxes are items to confirm (see [todo-fill-in](docs/todo-fill-in.md)).*

![Architecture](docs/img/architecture.png)

*(Vector version: [architecture.svg](docs/img/architecture.svg). Text versions of the diagrams are in
[docs/architecture.md](docs/architecture.md).)*

## What is in here

| Part | What it does | Where |
|------|--------------|-------|
| **Auto-routing** | Starts with the system, links mpv -> CamillaDSP -> USB interface by itself, falls back to a direct route if CamillaDSP is not ready | `scripts/theater-route`, `scripts/install-autoroute.sh` |
| **EQ switch** | `eq off` / `eq on` / `eq toggle` / `eq status`: bypass all DSP instantly, mid-film | same script, installed as `eq` |
| **Preset switcher** | Writes the CamillaDSP config for a named bass preset plus speaker alignment, validates it, restarts the service and relinks | `scripts/set-eq.py` |
| **Measurement kit** | Recorder for the measurement mic, delay-test signal and analyser, 5.1 bed listening test | `scripts/rec.sh`, `scripts/make-delaytest.py`, `tools/analyze-delaytest.py`, `scripts/make-bedtest.py` |
| **Tests** | Router and config generator tests that need no audio hardware | `tests/run.sh` |
| **Docs** | Architecture, runbook, install, tuning history, measurement method, troubleshooting, decisions | `docs/` |

## Daily use

You do nothing. Start mpv (or `mpv-atmos`); within half a second its channels are linked through CamillaDSP.

```bash
eq status    # what is routed where right now, which preset is loaded
eq off       # bypass: bass EQ, delays and level trims all off (mpv goes straight to the speakers)
eq on        # back to the tuned sound
eq toggle    # flip, handy on a keyboard shortcut
```

More in [docs/runbook.md](docs/runbook.md).

## Current tuning (as of 2026-10-21)

- **Bass preset `drone2`**: cut-only EQ voiced for strong bass "thump" with the boomy 63-92 Hz drone in some
  scores tamed with narrow cuts at 72 and 84 Hz. See [docs/tuning-log.md](docs/tuning-log.md).
- **Alignment `--align=bed`**: per-speaker delays so all five bed speakers arrive together at the seat, and level
  trims; heights are left alone for now. See [docs/alignment.md](docs/alignment.md).
- Run `./scripts/set-eq.py --set=drone2 --align=bed` to (re)apply it.

## How much is verified?

Honest status, claim by claim, in [docs/status.md](docs/status.md). In short:

| Verified by measurement and recording | Measured but not confirmed afterwards | Not yet tested on the real system |
|---|---|---|
| Bass voicing (`drone2`) | Speaker delays | Auto-routing and the `eq` switch (only simulated) |
| | Centre-speaker polarity | Lip-sync with CamillaDSP in the path |
| | Level trims (post-trim check inconclusive) | Dialogue clarity |

## Hardware

Hardware list and the channel map are in [docs/architecture.md](docs/architecture.md#hardware). The short version:
a Linux laptop, a 7.1 USB audio interface (C-Media chipset), Logitech Z906 (5.1 satellites and sub, fed over analog
direct inputs), two height speakers on their own amplifier, a Dayton iMM-6S measurement microphone on a second
USB audio device.

## Repository layout

```
scripts/     things you run: theater-route (+ `eq`), install-autoroute.sh, set-eq.py, route-mpv.sh (manual routing),
             rec.sh (mic recorder), tone-test.sh, make-delaytest.py, make-bedtest.py
tools/       analysis: analyze-delaytest.py, make-architecture-diagram.py
configs/     example generated CamillaDSP config, systemd unit files
data/        small REW measurement exports (see data/README.md)
tests/       tests/run.sh: router + config tests, no hardware needed
docs/        the documentation (start with architecture.md and runbook.md)
```

## Quick start on a new machine

See [docs/installation.md](docs/installation.md). The two commands that matter once everything is installed:

```bash
./scripts/set-eq.py --set=drone2 --align=bed     # write + load the config
./scripts/install-autoroute.sh                   # start-at-login router + the `eq` command
```

## Still to fill in

Parts of the setup were built before this repo existed and only the owner knows them (the exact `mpv-atmos`
command and `mpv.conf`, Omniphony install steps, library mount). They are marked `TODO(owner)` in the docs
and listed in [docs/todo-fill-in.md](docs/todo-fill-in.md).

## Credits

This project is mostly glue and measurement. The hard part, decoding and rendering Atmos objects live on Linux, is the
work of others, and everything here stands on it:

- **[Omniphony](https://github.com/mgth/Omniphony)** by mgth: the object renderer (VBAP to any speaker layout), Omniphony
  Studio and the OSC control layer. **[mpv-omniphony](https://github.com/mgth/mpv-omniphony)** is the mpv integration
  used here. Thank you for building it and for merging the packaging fix so quickly.
- **[harletty-bridge](https://github.com/harletty/harletty-bridge)** by harletty: the decoder plugin (TrueHD and E-AC-3
  Atmos objects; its repository also carries DTS and DTS:X input support) that feeds Omniphony its objects.
- **[truehdd](https://github.com/truehdd/truehdd)** by Rainbaby, the open-source TrueHD Atmos decoder that the `harletty` decoder
  (inside harletty-bridge) is a fork of, per harletty's README. Without that work, none of this would be possible.
- Also used: [mpv](https://mpv.io), [libplacebo](https://code.videolan.org/videolan/libplacebo), [PipeWire](https://pipewire.org),
  [CamillaDSP](https://github.com/HEnquist/camilladsp), [Room EQ Wizard](https://www.roomeqwizard.com), and
  [Cavern](https://github.com/VoidXH/Cavern) (used for offline rendering before the live path existed).

How the Omniphony stack was built and debugged on this machine is in [docs/omniphony-debugging.md](docs/omniphony-debugging.md).

## Authorship and licence

The tuning decisions, measurements, listening tests and the build itself are the owner's. The scripts, analysis code
and first drafts of these documents were written with Claude (Anthropic) during a working session on
2026-10-20/21. Licensed under the [Apache License 2.0](LICENSE). The projects credited above have their own licences.
