# Status: what is verified and what is not

Updated 2026-10-21. "Verified" means measured **and** confirmed by a recording or by the owner's listening on real material.

| Claim | Evidence | Level |
|-------|----------|-------|
| `drone2` removes the boomy drone and keeps the thump | Recordings at the seat vs no DSP on F1, Godzilla, Tenet; band-energy deltas matched predictions within about 1-2 dB; owner's listening agrees | **Verified** |
| Speaker delays (table in [alignment.md](alignment.md)) are right | Chirp test, two runs (the first discarded for a setup error); owner's listening "alignment seems solid"; no after-recording | Measured |
| All speakers are in phase (no inversion) | Pair test T6, in phase louder for every pair | Measured |
| Level trims bring the speakers to the same level | Pre-trim levels from band energy; a post-trim check on the recorded bed test was inconclusive (different method, low level, one position) | Partial |
| Auto-routing starts with the system and handles mpv, stereo, 5.1 and 8 channels | Simulated PipeWire graph only (`tests/test_router.py`) | **Not yet tested on the real system** |
| The `eq` switch works mid-film | Simulated only | **Not yet tested** |
| Lip-sync is fine with CamillaDSP in the path | Not checked; estimated added delay 20-45 ms | **Not yet tested** |
| Dialogue is clear and anchored to the screen | Not tested | **Not yet tested** |

## Checks still to do

1. **Reboot test.** Reboot, start a film without touching anything, run `eq status`: expect "audio goes through CamillaDSP".
2. **Port names.** While Atmos content plays, then a 5.1 file, record `pw-link -o | grep mpv` in [architecture.md](architecture.md).
   The router handles any port subset, but `route-mpv.sh` reported 8 channels linked while a 6-channel FLAC played: write down why.
3. **Lip-sync.** Watch a clear-speech clip with `eq on` and `eq off`; adjust `--audio-delay` if a difference is visible.
4. **Alignment proof.** The bed-off versus bed-on recording in [measurement.md](measurement.md#proof-of-the-alignment-still-open).
5. **Real films.** A few non-trailer films (dialogue-heavy, quiet) with the final settings.
