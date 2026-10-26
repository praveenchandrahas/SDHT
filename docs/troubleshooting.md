# Troubleshooting

Start with `eq status`, then `systemctl --user status camilladsp.service theater-router.service`.

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| No sound at all | Both routes missing, or USB interface not found | `eq off`; if still silent `pw-link -i \| grep usb` to see if the sink exists; replug; check the interface name ([installation.md](installation.md#3-configure-the-interface-name)) |
| `eq status` says "mpv: not playing" while a film plays | mpv's PipeWire ports are not named `mpv:output_*` | Run `pw-link -o \| grep -i mpv` and compare; the router looks for node name `mpv`. TODO(owner): record the port names for Atmos and for 5.1 files |
| Sound but no EQ effect | EQ switch off, router stopped, or routed direct as fallback | `eq status` shows which; `eq on`; `systemctl --user start theater-router` |
| "mixed or unfinished routing" | CamillaDSP restarting, or a manual `route-mpv.sh` fighting the router | Wait one second and re-run; do not use `route-mpv.sh off` while the router runs |
| Sound is direct after `set-eq.py` | CamillaDSP ports did not appear in time (the script says so) | `systemctl --user status camilladsp`; read the journal; fix the config error; `systemctl --user restart camilladsp` |
| `set-eq.py` says "Config check FAILED" | YAML or filter problem; nothing was changed | Read the printed message; the old config is still in place |
| Continuous `buffer empty, outputting silence` warnings | CamillaDSP running with a stalled or unconnected stream | Check `eq status`; restart CamillaDSP; if it persists note whether mpv is playing and add the journal to the issue |
| Bass boomy or lean again | Different preset loaded, or speakers/seat moved | `eq status` (shows the preset); re-run `set-eq.py --set=drone2 --align=bed`; if the room changed, re-measure |
| Surround sounds too loud / bright | SL measured brighter than FL (not yet corrected) | Expected until tone matching is done ([roadmap.md](roadmap.md)) |
| Everything is quieter after a change | EQ cuts and negative trims | Normal; raise the Z906 knob slightly ([runbook.md](runbook.md)) |
| Music or a quiet scene sounds hollow at one bass note | The narrow 72 Hz cut | Try `--set=drone1` (gentler), or `eq off` for music |
| After reboot nothing routes | `camilladsp.service` not enabled, or user services not started at boot | Re-run `install-autoroute.sh` and read its "Start at boot" section |

Reading logs: `journalctl --user -u theater-router -n 50 --no-pager`. Each routing change prints a line such as
`[EQ on] mpv 8ch via CamillaDSP`.
