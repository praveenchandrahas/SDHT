# Roadmap

Ordered by payoff for effort. Nothing here is required for the system to work.

| Item | Why | Needs |
|------|-----|-------|
| Verify and document the auto-router on the real machine | Everything else depends on it | Reboot test, `eq status` output, journal excerpt |
| Back up and publish this repository | The know-how currently lives in one folder | `git init`, a remote |
| Make-up gain for EQ on | EQ on is quieter than off; fairer A/B | A few dB of Gain in CamillaDSP, checked on a loud scene for clipping |
| Height high-pass (about 100-120 Hz) | Small drivers, no sub, protect against loud low-frequency objects | A filter on channels 2 and 3, then height alignment with `--align` |
| Centre trim | Dialogue anchoring, if it bothers | Centre sweep export, listening |
| Tone matching of the five bed speakers | SL is brighter than FL (about +3 dB mids, +6 dB at 4-8 kHz before trims) | REW sweeps of FL FR FC SL SR at the final seat position, exported as text |
| Reference level | Know what knob position equals film level | Mic + test tone at a fixed Z906 position |
| Dynamic loudness / volume in CamillaDSP | Quiet listening without losing bass | CamillaDSP Loudness filter docs; keep Z906 at the fixed reference |
| CamillaDSP GUI | Visual editing | Decide how it coexists with `set-eq.py` (it writes its own config) |
| Move to the planned desktop PC | More headroom, same software | Re-check interface names, channel order, re-run `tests/run.sh` |
| Documentation for the next room | A larger room later would be a clean second build | This repo as the template |

Deliberately not planned: rear or extra height speakers in the current room (see D1), multi-seat averaging (tuned for one seat).
