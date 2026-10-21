# Runbook: using and looking after the system

## Everyday

| I want to... | Do this |
|--------------|---------|
| Watch something | Start mpv or `mpv-atmos`. Nothing else. |
| Hear it without any DSP | `eq off` (all EQ, delays and trims bypassed). `eq on` to come back. |
| See what is happening | `eq status` |
| Change the preset | `./scripts/set-eq.py --set=drone2 --align=bed` (see list below) |
| Look at the router's log | `journalctl --user -u theater-router -f` |
| Look at CamillaDSP's log | `journalctl --user -u camilladsp -n 50 --no-pager` |

`eq status` prints the switch state, whether the router and CamillaDSP services are active, which preset is on
disk, and per-channel routing counts. "audio goes through CamillaDSP (EQ active)" is the healthy line while a film plays.

A brief burst of `PipeWire playback: buffer empty, outputting silence` warnings in the CamillaDSP log when a stream
starts or stops is normal. A continuous stream of them is not (see [troubleshooting.md](troubleshooting.md)).

### Remember when comparing EQ on and off

EQ on is quieter, mostly in the bass (every filter is a cut and the trims are negative). Louder sounds better, so
raise the Z906 knob slightly with EQ on before judging, or judge at matched level.

## Presets

`./scripts/set-eq.py [<scale> <max_freq_hz>] [--set=NAME] [--skip=a,b] [--align|--align=bed] [--invert=FC,...] [--dry]`

| Set | What it is |
|-----|------------|
| `drone2` | **In daily use.** `punch20x` plus cuts at 72 Hz (-6 dB, Q 8) and 84 Hz (-6 dB, Q 4). |
| `drone1`, `drone3` | Gentler / stronger versions of the same idea. |
| `punch20x`, `thump20x`, `tight20x`, `punch20`, `thump20` | Bass-forward sets 20 dB above the mids with different weight at 47 / 61 Hz (history in [tuning-log.md](tuning-log.md)). |
| `hump8`, `hump14`, `hump20`, `thump14` | Earlier fits at 8 / 14 / 20 dB above the mids. |
| `rew` | The flat-target REW fit. Too lean for this room and taste. |

`--align=bed` adds the per-speaker delays and trims for FL FR FC LFE SL SR and leaves the heights alone.
`--invert=FC` flips a speaker's polarity (not needed: pair tests showed all speakers in phase).
Each run validates the config first, then restarts CamillaDSP and relinks. If anything fails, the router falls back to the direct route.

## Z906 rules

- **Do not change the sub level** without re-measuring the Z906 channels: all bass tuning assumes the sub as it is.
- The master volume can be changed freely: it scales all channels equally.
- Record the knob positions here: TODO(owner): sub-level position and master volume reference position (photo in `docs/img/`).

## Starting, stopping, services

```bash
systemctl --user status camilladsp.service theater-router.service
systemctl --user restart camilladsp.service     # links are rebuilt by the router within a second
systemctl --user stop theater-router.service    # stop auto-routing (mpv then plays direct, no EQ)
./scripts/route-mpv.sh status                   # manual routing helper (only while the router is stopped)
```

`route-mpv.sh on|off` is the older manual tool. While the router runs it will undo `route-mpv.sh off` within a
second: use `eq off` instead.

## After a reboot

Nothing to do. To confirm: start a film, run `eq status`. It should say audio goes through CamillaDSP. If the
USB interface enumerated under a different name, see [troubleshooting.md](troubleshooting.md).

## Backups

The tuning lives in a few small files. Keep them in this repository and push regularly:
`scripts/set-eq.py` (presets and alignment table), `configs/`, `docs/`.
Outside the repository, back up `~/.config/camilladsp/config.yml` (regenerable with set-eq.py), the mic calibration
file, `mpv.conf`, and the Omniphony configuration. TODO(owner): paths of the last two.

## Re-tuning checklist

Redo measurements if any of these change: speaker positions, listening seat, Z906 sub level or placement, room furniture,
USB interface, or CamillaDSP chunk size. Method: [measurement.md](measurement.md). Order of work: bass voicing,
then delays, then levels, then tone, then heights.
