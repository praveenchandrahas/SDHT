# Alignment: delays, level trims, polarity

Goal: every speaker's sound arrives at the listening seat at the same moment and level, so phantom images between
speakers are stable and surrounds do not pull towards the nearest speaker.

## Method

1. `scripts/make-delaytest.py` writes `delaytest.wav`: eight channels, a 30 ms chirp (400-8000 Hz) on each speaker
   in turn in 0.25 s slots, repeated 12 times; the LFE slot is silent.
2. Play it straight to the USB sink (bypassing CamillaDSP):
   `pw-play --target alsa_output.usb-0d8c_USB_Sound_Device-00.analog-surround-71 --channel-map FL,FR,RL,RR,FC,LFE,SL,SR delaytest.wav`
3. Record at the seat with `scripts/rec.sh` (mic at ear height, opposite the centre speaker).
4. `python3 tools/analyze-delaytest.py recording.wav` finds every chirp with a matched filter and fits
   `t = a + s*slot + d_channel`. The slope `s` absorbs the clock difference between playback and capture;
   `d_channel` is each speaker's delay relative to FL. The `+- ms` column is the scatter of the 12 repeats.

The analyser was checked against a simulated recording with known delays and recovered them to about 0.002 ms.
On real recordings the `+- ms` column is the honest error bar: do not act on differences smaller than it.

Why not REW's impulse responses: the sweeps were recorded "with no timing reference" on a separate capture device,
so REW's arrival times are unreliable, and its overlay aligns each impulse at its own peak.

## Result (2026-10-21, second run: mic opposite the centre, centre speaker the right way up)

The reference is the **farthest** speaker (FR): delays only ever add to nearer speakers, so nothing has to wait for the heights.

| Speaker | Delay added | Closer than FR by (343 m/s) | Level trim | Measured level vs FL before trim |
|---------|------------:|-----------------:|-----------:|-----:|
| FL | 0.20 ms | 7 cm | 0 | 0 |
| FR | 0 (reference) | 0 | -1.9 dB | +1.9 dB |
| FC | 0.97 ms | 33 cm | -0.8 dB | +0.8 dB |
| LFE | 0.20 ms | (kept in step with FL) | 0 | n/a |
| SL | 3.00 ms | 1.03 m | -4.4 dB | +4.4 dB |
| SR | 2.72 ms | 0.93 m | -0.7 dB | +0.7 dB |
| RL (height) | 4.60 ms | 1.58 m | -0.6 dB | +0.6 dB |
| RR (height) | 4.70 ms | 1.61 m | -0.3 dB | +0.3 dB |

The first run was discarded: the centre speaker was upside down and the mic was not opposite it, which produced
implausible asymmetric delays. The table above is from the corrected run. Levels are from band energy of each chirp slot
(peak height is unreliable).

These numbers are in the `ALIGN` table in `scripts/set-eq.py`. **`--align=bed` applies all rows except the heights**:
the owner wanted the 5.1 bed correct first and is fine with heights running slightly hot. `--align` (no value) also applies the height delays.

## Verification (2026-10-23, sweep run 1, CamillaDSP and `--align` active)

Arrival at the seat relative to FL (mic at the cushion, first 300-4000 Hz rise of each sweep): FR -0.18, RL +0.06, RR -0.15,
FC -0.08, SL +0.08, SR -0.12 ms. All within 0.2 ms, inside the measurement scatter and far inside the seating tolerance
(1 ft = about 0.9 ms). The delay table is therefore correct as applied, heights included (`--align`, not `--align=bed`).

The heights need 4.6 ms although the tape measure puts them about as far as FR. Untested explanation: the Z906 digital path
adds about 4.5-5 ms that the analog Salcon path to the heights lacks.

## Heights (2026-10-23): bass management and tone

The heights (Samsung SWA-8500S on the Salcon amplifier) do not reproduce bass: 11 dB down at 125 Hz, 27 dB down at 100 Hz,
essentially nothing under 90 Hz. Every bed speaker, by contrast, feeds the sub at the same level as the LFE input (the Z906
does that bass management itself). `set-eq.py --heights` gives the heights the same treatment: LR4 high-pass at 140 Hz on
RL/RR, their sum low-passed at 140 Hz and added to the LFE channel at 0 dB. Sweep run 2: at 40-63 Hz a height channel now
plays 1.1-1.4 dB above a bed channel, at 100-125 Hz within 0.5-2.5 dB below.

`--heights-tone` adds filters fitted to what both heights agree on, against the mean of the five bed speakers: -7.5 dB at
310 Hz (Q 1.0), -7.0 dB at 1.7 kHz (Q 2.5), +2.5 dB high shelf at 6 kHz (Q 0.8), trim +1.0 dB. The 310 Hz and 1.7 kHz humps
appear in three independent measurements (REW sweeps, pan test, sweep run 1). Narrow features that differ between RL and RR
(500 Hz, 10 kHz) are left alone: one seat and one microphone position cannot support them. Moving the mic between runs changed
single 1/6-octave bins by 3-7 dB.

## Tone differences noticed (not corrected yet)

Before trims, SL measured brighter than FL (about +3 dB at 300-1000 Hz, +6 dB at 4-8 kHz); SR a little duller at 4-8 kHz.
This is a tone-matching job (see [roadmap.md](roadmap.md)).

## Polarity

Check with the pair test in the bed test (T6): two speakers play the same noise, in phase then with the second speaker
inverted. In phase should be louder and more solid. Result: in phase was louder for every pair (FL+FC +2.6 dB,
FR+FC +2.9 dB), so there is **no evidence of an inverted speaker**; `--invert` exists but is unused.

A lesson recorded here so it is not repeated: an earlier analysis said the centre looked inverted (correlation r = -0.86
at 250-900 Hz). That method flips sign when two speakers are misaligned by about 1 ms, so it is not a polarity test. The
pair test is.

## Verification status

The delay and level numbers have **not** been confirmed by an after-recording. A recording of the bed test through the
aligned chain was made; the level check on it was inconclusive (single-position noise bursts, low recording level, and a
different method from the chirp test). The clean check, still open, is in [status.md](status.md): record the same
14 seconds of the bed test with alignment off and then on, and confirm the difference matches the table.
