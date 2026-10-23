# Status: what is verified and what is not

Updated 2026-10-23. "Verified" means measured **and** confirmed by a recording or by the owner's listening on real material.

| Claim | Evidence | Level |
|-------|----------|-------|
| `drone2` removes the boomy drone and keeps the thump | Recordings at the seat vs no DSP on F1, Godzilla, Tenet; band-energy deltas matched predictions within about 1-2 dB; owner's listening agrees | **Verified** |
| Speaker delays (table in [alignment.md](alignment.md)) are right | Chirp test, two runs (the first discarded for a setup error); after-recordings, then sweep run 1 (2026-10-23, CamillaDSP in the path): all eight arrive within 0.2 ms of FL | **Verified** |
| All speakers are in phase (no inversion) | Pair test T6, in phase louder for every pair | Measured |
| Level trims bring the speakers to the same level | Sweep run 1: bed speakers within about 2 dB of FL at 500-2k (FR -0.5, SL +0.9, SR +1.7); repositioning the mic moves such numbers by 1-2 dB | Measured (+-2 dB) |
| Heights are bass-managed into the sub and tone-matched to the bed | Sweep run 2 with the profile on: heights + sub within 2.6/2.7 dB rms of the bed over 40-400 Hz (was ~40 dB); tone deviation 3.1/3.5 dB rms (was 4.5/4.1); heights ran 2-3 dB hot with the first trim, lowered to +1.0 dB (not re-measured) | Measured |
| Sub range | Sweeps at 3 levels: clean to about 40 Hz, usable 36 Hz, audible but 15%+ distortion at 25-31 Hz, nothing usable under 22 Hz; no compression | Measured |
| A rattle/buzz in loud bass scenes | Not reproduced by steady tones at -14 dBFS (6-12 dB quieter than the film's bass); a fixed ~100 Hz component in the Amaze recording matches a +5 dB room peak at 100 Hz | Open |
| Standing profile (`./make-default.sh`, `eq ensure` in mpv-atmos) survives reboot and starts the services | Config file persistence and tests only | **Not yet tested on the real system** |
| Auto-routing starts with the system and handles mpv, stereo, 5.1 and 8 channels | Simulated PipeWire graph only (`tests/test_router.py`) | **Not yet tested on the real system** |
| The `eq` switch works mid-film | Simulated only | **Not yet tested** |
| Lip-sync is fine with CamillaDSP in the path | Owner: no lip-sync issue at all on real material; not measured (estimated added delay was 20-45 ms) | Owner-verified (listening) |
| Dialogue is clear and anchored to the screen | Owner: dialogue is fine; `tools/dialoguetest/` built (checked against a simulated room) but not yet run in the room | Owner-verified (listening), not measured |
| First-reflection panels (FL, FC, FR, heights) work | `tools/reflecttest/` on sweep run 2 (panels in place, no baseline): FC and FR OK against ITU-R BS.1116 (every reflection 10 dB under the direct sound); FL one reflection at 5.1 ms, -8 dB; both heights a reflection near -1 dB at 3.6-3.8 ms. A/B with panels covered not yet done | Measured (state), **effect untested** |

## Checks still to do

1. **Reboot test.** Reboot, start a film without touching anything, run `eq status`: expect "audio goes through CamillaDSP".
2. **Port names.** While Atmos content plays, then a 5.1 file, record `pw-link -o | grep mpv` in [architecture.md](architecture.md).
   The router handles any port subset, but `route-mpv.sh` reported 8 channels linked while a 6-channel FLAC played: write down why.
3. **Lip-sync.** Watch a clear-speech clip with `eq on` and `eq off`; adjust `--audio-delay` if a difference is visible.
4. **Alignment proof.** The bed-off versus bed-on recording in [measurement.md](measurement.md#proof-of-the-alignment-still-open).
5. **Real films.** A few non-trailer films (dialogue-heavy, quiet) with the final settings.
