# Status and control surfaces for the theatre rig: plan

Planning only. Nothing in the repos was changed. Facts below come from reading `theater-route`, `set-eq.py`, `mpv-atmos`, `mpv-object-audio`, `thumbfast.lua`, `preflight`, `check-installed.sh`, `architecture.md`, `runbook.md`, `decisions.md`. Anything I could not check is marked UNVERIFIED. (I could not fetch the CamillaDSP websocket docs; the command names below are from memory and must be checked against the 4.1.3 `websocket.md`.)

## 1. What the code constrains (read this first)

1. **No machine-readable status.** `eq status` only prints text (`status()` in `theater-route`). Everything downstream needs a `collect_status()` refactor that returns a dict, with `status()` printing from it, plus `eq status --json`.
2. **CamillaDSP's websocket is not on.** The unit runs `camilladsp ~/.config/camilladsp/config.yml` with no `-p/-a`. Enabling it means editing the unit (`-p 1234 -a 127.0.0.1`). Every profile switch restarts the service (`set-eq.py`), so the socket drops each time and clients must reconnect.
3. **Bass preset is not state.** The router calls `set-eq.py --default` or `--upmix=...`, and both start from `DEFAULT_ARGS` (drone2). A bass set chosen by hand is lost at the next automatic profile switch. A "bass preset" control needs a new state file (`bass-set`) and `run_seteq()` passing `--set=`. That is a router change, not a UI task.
4. **Some requested controls do not exist.** There is no dialogue boost anywhere. The Z906 sub and master are analog knobs (D12: do not change the sub level without re-measuring). A software "sub level" would mean a new LFE trim in `set-eq.py`, and D3 says cuts only. Recommendation: show these as read-only or leave them out. No night preset (D13).
5. **Profile switches are not free.** Until 2026-10-26 each one restarted CamillaDSP (about 1 s of silence, rate-limited to 8 s); `set-eq.py` now reloads it in place with SIGHUP and falls back to a restart if the ports or links change (untested on the rig at the time of writing). Running `bed` or `stereo` into an Atmos film is wrong (runbook). `eq off` is louder (D3). A stray phone tap mid-film is a real surprise, so risky actions need guards (section 4).
6. **`classify()` only knows "Atmos".** A 6-channel DTS:X track would be treated as plain 5.1 and get the bed upmix. The UI should show the codec profile it really sees, and the classifier should learn DTS:X.
7. **Object-audio detail is thin.** Over mpv IPC we can read `current-ao`, `audio-codec-name`, `current-tracks/audio` (profile, channels), `audio-params`, `audio-out-params`, `audio-delay`, `pause`, `time-pos`. Bed/object count and active speakers exist only in Omniphony's OSC stream (`--ad-orender-osc`, not enabled in the wrappers). Its message schema is not in any repo. UNVERIFIED.
8. **Two mpv builds, two config folders.** `mpv-atmos` uses `~/.config/mpv`; `mpv-object-audio` uses `~/.config/mpv-object-audio` (a snapshot copy that will drift). Both share one IPC socket path, so only one runs at a time. Any Lua script must be installed in both. The seekthumbs viewer is still untested in real mpv/uosc, so overlay and uosc behaviour on this rig is unproven.
9. **Underruns are not a number anywhere.** CamillaDSP logs "buffer empty" to the journal. `GetClippedSamples`, processing load and buffer level should be on the websocket. Underruns would have to come from counting journal lines or `pw-top` ERR, which is fragile and best-effort.

## 2. Comparison

| | Effort | State source | Control | Main risk | Fit |
|---|---|---|---|---|---|
| (a) mpv OSD (Lua) | M. Lua in two config dirs, uosc menu | Daemon pushes `script-message` over the existing mpv IPC socket (Lua has no sockets, polling is awkward) | uosc menu or keys, calling the daemon through an async `subprocess` with fixed argv | Only visible while mpv plays; untested uosc; text via `mp.create_osd_overlay` (ASS), not `overlay-add` (that is for bitmaps like thumbfast) | Good for a read-only glance at the projector. Poor as the main control (no pointer on a couch) |
| (b1) Plasmoid | M-L. QML, Plasma 5.27 vs 6 API differences | QML cannot use a Unix socket, so it needs localhost HTTP. The `executable` data engine runs shell strings: avoid | XHR to 127.0.0.1 | Breaks on Plasma upgrade; laptop only | Nice but replaceable by a web page in a window |
| (b2) KDE Connect | XS. Run-command entries in its config | None (fire and forget) | Phone buttons run fixed commands; pairing is encrypted and LAN-only | No live status; Android only (iOS app is weak) | Best zero-new-listener option for a few buttons |
| (c) Local web (page + API) | M | Daemon | Same API for all clients | The only one that opens a LAN port | Best fit for phone, laptop and projector browser |
| (d) TUI (Textual) | S | Daemon API | Keys | Terminal only; adds a pip dependency | Cheap, good dev tool. Not for the phone |
| (e) Home Assistant / MQTT | L. Broker, HA, auth, discovery | Bridge from the daemon | HA automations can act unattended | A new always-on system, credentials, automations that act by themselves: the opposite of "no surprises" | Only if HA already exists (open question). Later, thin bridge |
| (f) camillagui | S to install, high risk | CamillaDSP websocket | Edits the whole live config | See below | Reject as control; at most a read-only meter |

**Why (f) is rejected.** `current_profile()` reads the `# theater-profile:` comment on line 1 of `config.yml`. A GUI save re-serialises YAML and drops comments, so the router would believe the profile is `film` and start making wrong switches. The GUI can also push boosts or gain that break the cut-only rule (D3), and it has no auth by default. It also fights `set-eq.py`, which regenerates the file.

**Why the web page uses SSE, not WebSocket.** The router is stdlib-only. Live status is one-way, so Server-Sent Events plus `POST` for actions is enough, needs no dependency, and works in every phone browser. FastAPI is not required; a stdlib `asyncio` server of about 300 lines is enough, so there is no venv to maintain (Ubuntu 24.04 blocks system pip).

**PWA.** Installable PWAs need HTTPS. Plain HTTP on the LAN supports "Add to Home screen" as a shortcut only. Real PWA means a local CA or Tailscale certs. Not worth it for v1.

## 3. Recommended architecture

```
 phone / laptop browser / projector browser ---HTTP(LAN, opt-in)--+
 uosc OSD (Lua)  <--script-message--+                              v
 TUI / CLI / KDE Connect cmds --Unix socket--> theater-ctld  --(argv, no shell)--> eq <cmd>   (router stays the only actuator)
                                                  |  reads: state files, eq status --json, mpv IPC,
                                                  |         CamillaDSP ws (read-only cmds), journal (rate-limited)
```

- **New process `theater-ctld`** (`linux-theater-dsp/scripts/theater-ctld`, plus `web/index.html`, unit `configs/systemd/theater-ctld.service`). Separate from `theater-route` on purpose: the router is what guarantees "never silent". The control plane must never sit on the audio-critical path, so if `theater-ctld` dies audio is unaffected.
- **API** on `$XDG_RUNTIME_DIR/theater-ctl.sock` (mode 0600): `GET /v1/status`, `GET /v1/events` (SSE, 1 Hz and on change), `POST /v1/action`. The daemon caches a snapshot for about 1 s so ten clients do not spawn ten `pw-link` runs. The LAN listener serves the same routes.
- **Status schema** (one JSON object, each block has `ok` and `age_s` so stale or unreachable data is visible, never silently blank):
  - `eq` {switch, router, camilla, verdict}
  - `dsp` {profile, pmode (pinned flag), flavours, engine {state, service, linked}, bass_set, alignment, heights, rate, chunk, est_latency_ms (labelled estimate, not measured), load, buffer, clipped, underruns_60s (best-effort)}
  - `source` {mpv up, codec, codec_profile, channels, kind, why, ao, in/out sample rate}
  - `objects` {available:false until the OSC schema is known}
  - `routing` {via, direct, out_to_usb, usb_up, apps[]}
- **Actions**: a fixed table, enum-validated, never concatenated. Argv list, no shell, 30 s timeout, one at a time under a lock, idempotent (no-op if already set):
  - `eq.on|off`
  - `mode` in auto|film|stereo|bed
  - `flavour` {kind in stereo|bed, name in the FLAVOURS table}
  - `engine` in on|off
  - `bass` in {drone1, drone2, drone3}, only after item 3 above is built
  - A `refresh` action (re-run `eq` apply) only if wanted.
  - There is no `run`, no path argument, and `eq prepare FILE` is never exposed.
- **Guards** (the answer to "no surprises"):
  - Restart-causing actions (mode, flavour, engine, bass) while mpv is playing need `confirm:true`, and the UI shows "about 1 s of silence".
  - `pmode` pinned to something other than `auto` is a persistent banner.
  - `eq off` shows "will be louder".
  - Every remote action calls `notify-send` on the laptop ("Phone: EQ off") and is written to the journal.
- **Auth and exposure**:
  - Unix socket by default. The LAN listener is off until the owner turns it on (`theater-ctld --lan` via a systemd drop-in). It binds to one LAN IP, never 0.0.0.0, and should be paired with `ufw allow from <lan>/24 to port`.
  - Writes need a random bearer token (file mode 0600, entered once on the phone, shown as a QR code in the terminal). Reads without a token show only coarse status (no film file names).
  - Check the `Host` header (DNS rebinding) and `Origin` on `POST`, and require the `Authorization` header, which browsers cannot send cross-origin without a preflight.
  - Plain HTTP means the token can be sniffed on the Wi-Fi. That is acceptable only on a trusted home LAN; say so in the docs.
  - If exposed wrongly the worst case is nuisance, not code execution: someone with the token could toggle EQ or restart CamillaDSP. Without a token they see coarse status. Never forward the port to the internet.
- **CamillaDSP websocket**: read commands only, enforced by an allow-list in code (`GetState`, `GetCaptureRate`, `GetBufferLevel`, `GetClippedSamples`, `GetProcessingLoad`, `GetSignalPeaks`, `GetConfigFilePath`). Bound to 127.0.0.1. All config changes stay with `set-eq.py`, so the file and the `# theater-profile:` header remain the single truth.

## 4. Phases

0. **`eq status --json`** (`collect_status()` refactor, text output unchanged) with a golden-file test. Value on its own: `watch -n1 'eq status --json | jq'`.
1. **`theater-ctld` on the Unix socket**, read-only plus `eq on/off`, `mode`, `engine`, `flavour`, a CLI `theater-ctl`, the unit, and a row in `check-installed.sh`. No network.
2. **Web page** (one static file, no build step: status cards, buttons, confirm dialogs). Localhost first, then LAN read-only for a week, then LAN writes with the token and notifications. Add the CamillaDSP websocket here (needs the unit edit and the owner's agreement).
3. **mpv status overlay**: a Lua script (`theater-status.lua`) toggled by a key, daemon-pushed, ASS text, read-only. Install into both mpv config dirs. Add a uosc menu only if the owner wants projector control.
4. **Bass preset** (router `bass-set` state, tests), **DTS:X classification**, and OSC object status once the schema is captured at the rig.
5. Optional, only on request: KDE Connect command list (it can come earlier, since it costs nothing), TUI, plasmoid, MQTT bridge.

**Recommended minimal first version**: phases 0 and 1 plus a localhost web page, with no LAN listener and no websocket. It answers "what is the rig doing" on the laptop, changes no audio behaviour, and touches only `theater-route`'s printing. LAN and phone come only after he has used it for a while.

## 5. Testing

**In the sandbox with fakes** (extend `tests/run.sh`; the existing `tests/fake-pw-link` and `THEATER_STATE_DIR`/`THEATER_PW_LINK`/`THEATER_MPV_SOCK` env hooks already allow it):
- fake `systemctl` and `camilladsp`;
- a fake mpv IPC server returning canned Atmos, DTS:X, 5.1 and stereo tracks;
- a fake CamillaDSP websocket with canned replies, including a mid-test disconnect;
- `eq status --json` golden files;
- the API: allow-list rejection, bad enums, no shell metacharacters reaching argv, token and Host/Origin checks, the lock and rate limit, confirm guards, SSE reconnect;
- the Lua script under a mocked mpv API (lupa, as seekthumbs did).

**Only at the rig**:
- real PipeWire names and the Chrome node name (still unverified per the runbook);
- the CamillaDSP 4.1.3 websocket field names and whether `-p` changes startup;
- real restart timing and silence when a profile is switched;
- uosc and `create_osd_overlay` on the projector;
- the Omniphony OSC schema;
- phone Wi-Fi behaviour (SSE through sleep and wake);
- firewall rules and KDE Connect pairing;
- Plasma version differences;
- the real latency number (the repo only has an estimate).

## 6. Open questions for the owner

1. Phone: Android or iPhone? (KDE Connect and "Add to Home screen" differ.)
2. How do you control the projector laptop from the couch: keyboard, air mouse, or only the phone? This decides whether projector control is needed at all, or read-only OSD plus phone is enough.
3. Do you already run Home Assistant or an MQTT broker? If not, I would drop (e).
4. May I edit `camilladsp.service` to add `-p 1234 -a 127.0.0.1`? Without it there is no load, clipping or buffer data.
5. Should a manually chosen bass set survive automatic profile switches (item 3)? That changes router behaviour.
6. Is a LAN listener acceptable at all, given plain HTTP and a token? If not, the phone path is KDE Connect (buttons) only.
7. Which actions may the phone do mid-film: only EQ on/off, or also mode and flavour (which silence audio for about a second)?
8. Should the project live in `linux-theater-dsp` (shared fakes and installer) or a new repo? I suggest the former.
9. Is "bed/object count and active speakers" worth capturing Omniphony OSC at the rig, or is codec/profile/channels from mpv enough?
10. Is the DTS:X classification gap worth fixing now?
