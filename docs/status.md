# Status: what is verified and what is not

Updated 2026-10-23. "Verified" means measured **and** confirmed by a recording or by the owner's listening on real material.

| Claim | Evidence | Level |
|-------|----------|-------|
| `drone2` removes the boomy drone and keeps the thump | Recordings at the seat vs no DSP on F1, Godzilla, Tenet; band-energy deltas matched predictions within about 1-2 dB; owner's listening agrees | **Verified** |
| Speaker delays (table in [alignment.md](alignment.md)) are right | Chirp test, two runs (the first discarded for a setup error); after-recordings, then sweep run 1 (2026-10-23, CamillaDSP in the path): the seven full-range speakers arrive within 0.2 ms of FL (the sub, 6-7 ms later, is not compensated) | **Verified** |
| All speakers are in phase (no inversion) | Pair test T6, in phase louder for every pair | Measured |
| Level trims bring the speakers to the same level | Sweep run 1: bed speakers within about 2 dB of FL at 500-2k (FR -0.5, SL +0.9, SR +1.7); repositioning the mic moves such numbers by 1-2 dB | Measured (+-2 dB) |
| Heights are bass-managed into the sub and tone-matched to the bed | Sweep run 2 with the profile on: heights + sub within 2.6/2.7 dB rms of the bed over 40-400 Hz (was 41 dB for the heights alone, per bin; about 27 dB with 1/6-octave smoothing); tone deviation 3.1/3.5 dB rms (was 4.5/4.1); heights ran 2-3 dB hot with the first trim, lowered to +1.0 dB (not re-measured) | Measured |
| Sub range | Sweeps at 3 levels: clean to about 40 Hz, usable 36 Hz, audible but 15%+ distortion at 25-31 Hz, nothing usable under 22 Hz; no compression | Measured |
| A rattle/buzz in loud bass scenes | Praveen: it is the sub cabinet rattling at particular frequency/amplitude combinations (heard in the room). Not reproduced by steady tones at -14 dBFS (6-12 dB quieter than the film's bass). Re-analysis of the Amaze recording (fig 18) shows bass hits at 35-65 Hz and no 100 Hz line that stays put across hits, so the clip does not locate the buzz. In the hot run (fig 17) eight tones from 31.5-71 Hz peak at the same recorded level, which points at a limit in the chain; unresolved. Next: the same tone kit at -8/-3 dBFS with hand-on-cabinet checks | Open |
| Standing profile (`./make-default.sh`, `eq ensure` in mpv-atmos) survives reboot and starts the services | 2026-10-24 cold boot away from the rig (Vantec not connected): `eq status` = EQ ON, router active, CamillaDSP active with `drone2, bed alignment: yes, heights: bass to sub + tone-match`; `mpv-atmos` started Atmos 8 ch into PipeWire. A later `eq status` showed 0 links, expected with no USB interface | **Services and profile verified at boot**; routing to the rig after a reboot not testable without the Vantec, **still to do at the rig** |
| Auto-routing starts with the system and handles mpv, stereo, 5.1 and 8 channels | Simulated PipeWire graph only (`tests/test_router.py`) | **Not yet tested on the real system** |
| The `eq` switch works mid-film | Simulated only | **Not yet tested** |
| Lip-sync is fine with CamillaDSP in the path | Owner: no lip-sync issue at all on real material; not measured (estimated added delay was 20-45 ms) | Owner-verified (listening) |
| Dialogue is clear and anchored to the screen | Praveen: dialogue is fine. `tools/dialoguetest/` run in the room on 2026-10-24 (dlg1.wav): STI 0.79-0.83, dialogue 13-18 dB above the noise, phantom centre 0.81 vs real 0.79, FC flat to 1.3 dB rms | Measured and owner-verified |
| First-reflection panels (FL, FC, FR, heights) work | `tools/reflecttest/` on sweep run 2 (panels in place, no baseline): FC and FR OK against ITU-R BS.1116 (every reflection 10 dB under the direct sound); FL one reflection at 5.1 ms, -8 dB; both heights a reflection near -1 dB at 3.6-3.8 ms. A/B with panels covered not yet done | Measured (state), **effect untested** |

## Order of work (2026-10-25)

**Now, in this order** (each is quick and tells us what is actually broken):
1. `scripts/preflight` and the reboot test with the USB DAC connected (checks 0-1 below).
2. The bass-rattle hot run ([measurement.md](measurement.md); the owner's cabinet diagnosis is recorded above).
3. Vantec checks: whether the optical input and a second digital stream work alongside the 7.1 outputs (`preflight` lists the profiles and sources; `preflight capture SOURCE` is the Fire Stick decode test).
4. Nearfield sweeps of the spare HW-T670 soundbar and its sub (usable band, crossover, distortion), only once 1-3 are done.

**Later**: the second-sub feed (band-limited to about 50-100 Hz; the apartment rules out the JBL; clock drift is checked with `tools/drifttest/`), upmix flavours by ear (checks 6-8), Stremio via an M3U handler for `mpv-atmos` (`eq prepare` must cope with a playlist or URL).

**Parked, no cost to waiting**: 5.1 fly-over detector, SDHT Calibrate (one-command measurement to filters), planetarium sound design (sky-window test on the ceiling comes first), projector automation (RS-232 or IR, lamp-hour log), per-film memory of upmix choices.

## Checks still to do

0. **Run `scripts/preflight` at the rig** (USB DAC connected, ideally after a fresh boot) and send the report. It is read-only: it checks tools, services, the DAC's profiles and inputs, links, xruns, real-time priority and the live mpv options. `preflight --tests` adds the repository tests; `preflight capture SOURCE` is the Fire Stick optical-in decode test.

1. **Reboot test at the rig.** Services and profile came up at boot (2026-10-24, laptop away from the rig). Still to do with the Vantec connected: start a film, run `eq status`, expect "audio goes through CamillaDSP"; then stop CamillaDSP and confirm the direct fallback.
2. **Port names.** While Atmos content plays, then a 5.1 file, record `pw-link -o | grep mpv` in [architecture.md](architecture.md).
   The router handles any port subset, but `route-mpv.sh` reported 8 channels linked while a 6-channel FLAC played: write down why.
3. **Lip-sync.** Watch a clear-speech clip with `eq on` and `eq off`; adjust `--audio-delay` if a difference is visible.
4. **Alignment proof.** The bed-off versus bed-on recording in [measurement.md](measurement.md#proof-of-the-alignment-still-open).
5. **Real films.** A few non-trailer films (dialogue-heavy, quiet) with the final settings.
6. **Upmix by ear.** Measured offline only. At the rig: a YouTube clip (speech, then music) in `stereo:voice|balanced|wide`, and a 5.1 film in `bed:subtle|balanced|wide`; note the flavour you prefer. 
7. **Automatic profile at the rig.** (a) Play a YouTube video in Chrome: `eq status` should show "Google Chrome: playing, 2/2 channels patched" and `Profile: stereo:balanced`; if it says nothing about Chrome, send `pw-link -o | grep -i chrome`. (b) Start an Atmos film, then a 5.1 file, then a stereo file with `mpv-atmos`: `eq source` and `eq status` should say film / bed / stereo. (c) Chrome playing while a film starts: the film wins and Chrome must go back to normal sound (untested: relies on WirePlumber re-linking it). (d) Plain `mpv` needs `input-ipc-server` in mpv.conf.
8. **Adaptive engine at the rig.** Never run against real PipeWire (the DSP, latency and CPU are tested offline only). Re-run `install-autoroute.sh`, play a YouTube video, then `eq status`: expect "Adaptive engine: on, service active, ports up, linked into CamillaDSP" and `Profile: stereo-ad:balanced`. Unverified: the pw-cat flags and port names (`theater-upmix-in:input_FL`, `theater-upmix-out:output_AUX0..3`; check with `pw-link -io | grep theater`), whether the engine gets real-time priority (watch for clicks in the rear/ceiling feeds; `journalctl --user -u theater-upmix`), and the real end-to-end delay of the rear feeds (the sweep tools can measure it). If it falls back to the fixed matrix, send me `journalctl --user -u theater-upmix -n 30`. Judge adaptive vs fixed by ear: `eq engine off` / `eq engine on` mid-clip.

## Sub arrival (measured 2026-10-24 from sweep1/sweep2)

The sub (LFE) arrives about 6 to 7 ms after the front left at the seat, with a group delay near 15 ms at 50 to 100 Hz. The LFE delay is still 0.20 ms (kept in step with FL), so this has not been compensated.
Whether to delay the bed or to leave the sub late is open; at 60 Hz one period is 16 ms, so the phase against the bed matters more than the arrival time.
