# Tuning log: what was done and why

Newest decisions are at the top of each section. Every preset is defined in `scripts/set-eq.py`; nothing here depends on
files outside the repository except recordings.

## Room and baseline

- Room: 10 x 10 ft. The first axial mode of a 10 ft dimension is at about 56 Hz (343 / (2 x 3.05 m)); if two dimensions
  are both about 10 ft their modes coincide and the peak is stronger. The measured seat response shows strong peaks at
  56-68 Hz and a narrow null near 72 Hz; the second axial mode (about 113 Hz) is near the 107-110 Hz cut in the presets.
  Consistent with the room, not proven against exact dimensions.
- REW sweeps (2026-10-19) of all eight outputs (`data/rew/`). All Z906-fed channels (L, R, C, LFE, SL, SR) share the same bass
  "mountain" below about 100 Hz, peaking near 60 Hz and roughly 30-35 dB above the mids: the Z906 sub plus room
  modes, because the Z906 hands each channel's bass to its sub. The heights are 25-45 dB lower below 90 Hz (small
  speakers, no sub).
- EQ can cut peaks but cannot fill nulls; so every preset is **cut-only**, never boosting.

![Predicted effect of drone2 at the seat](img/bass-response-drone2.png)

*Top: measured response at the seat (left speaker plus sub path) and the predicted result with `drone2`. Bottom:
what `drone2` changes. The absolute height includes the sub's high level: read the shape and the change.*

## Bass voicing (2026-10-19 to 21)

Aim: strong bass "thump" and a room-shaking feel, with accuracy elsewhere. A fully flat correction was tried first
and judged **lean and hollow**.

| Step | Preset(s) | Idea | Outcome |
|------|-----------|------|---------|
| 1 | `rew` | REW auto-EQ to a flat target (8 cuts) | Much too lean, discarded as the target |
| 2 | `hump8`, `hump14`, `hump20` | Fit the measured response to a deliberate hump 8 / 14 / 20 dB above the mids, Q capped at 5 so it is less sensitive to small mic or head movement | The 20 dB family was the one developed further |
| 3 | `thump14`, `thump20` | Lift about 63 Hz (where 808-style thump lives) | Added weight near 63 Hz |
| 4 | `punch20`, `thump20x`, `punch20x`, `tight20x` | Variants of weight at 47 and 61 Hz, 85 Hz and 107 Hz | `thump20x` "closest, thump almost back but so did some boominess"; `punch20x` keeps thump but the F1 title drone is boomy |
| 5 | `drone1`, `drone2`, `drone3` | Keep `punch20x` and cut the **drone** with narrow cuts at 72 Hz and 84/88 Hz | **`drone2` chosen**: removes the drone note, thump stays |

Why the drone and the thump can be separated with static EQ: in the F1 title music the opening drone sits at 63-92 Hz
(spectral lines near 65.9, 67.7, 73.2 and 87 Hz) while the loud-section thump sits at 56-63 Hz (60.4 Hz line). So a
cut at 72 and 84 Hz removes the drone and leaves 56-63 Hz alone.

`drone2` = `punch20x` (8 peaking cuts, Q about 5) plus two more:

| Filter | Freq | Gain | Q |
|--------|-----:|-----:|--:|
| `d2_1` | 72 Hz | -6 dB | 8 |
| `d2_2` | 84 Hz | -6 dB | 4 |

Checked by recording at the seat and comparing with no DSP:
F1 title music (opening and loud section), Godzilla, Tenet "freeport" (last 15 s). In each, `drone2` reduced the
boominess and kept the thump; predicted changes matched the recorded changes within about 1-2 dB wherever the
microphone did not clip.

Limits to remember: tuned for one seat; the loud trailers clip the mic (see [measurement.md](measurement.md));
a narrow cut at 72 Hz sits close to the D2 bass note (about 73 Hz), so music may show it (the owner mostly watches films).

## Alignment (2026-10-21)

See [alignment.md](alignment.md). Delays and trims measured, `--align=bed` adopted, heights left alone.
Centre polarity checked and found fine; the owner chose not to invert anything.

## Lessons (mistakes made and corrected)

- **Mic clipping:** loud clips hit a ceiling in the recording (about +-0.3876 after capture gain). The mic's capture volume
  control is applied after the point where the signal clips, so lowering it did not prevent clipping. Quiet material (Tenet) recorded clean.
- **Wrong capture device:** the mic is on a separate USB adapter, not on the 7.1 interface; check `./scripts/rec.sh list`.
- **Peak height is a poor level measure:** use band energy over the whole slot.
- **Correlation-based polarity is unreliable** under about 1 ms misalignment: use the pair test.
- **A recording labelled with the wrong preset** produced a misleading comparison: name recordings by the preset actually loaded.
- **Timing tolerances:** the analyser's block-detection tolerance had to be widened to 15 ms to cope with +-5 ms channel delays.
