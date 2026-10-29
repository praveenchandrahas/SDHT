# resource-log 20261029-185907 hover-A

58 samples, 1 s apart; the load tables cover the 58 samples while mpv was running.
CPU is % of one core (200 = two cores busy). RSS is resident memory. Counters are totals added during the run.

## Problems: look at these first

- CamillaDSP log, while mpv was running (61 s): buffer-empty/underrun lines 120, overrun lines 0, clipping lines 0, ERROR/WARN lines 0
- CamillaDSP log, while mpv was not running (0 s): buffer-empty/underrun lines 0, overrun lines 0, clipping lines 0, ERROR/WARN lines 0
- most frequent problem messages while mpv was running: "#-#-# #:#:# WARN [camillalib::pipewire_backend::device] <src/pipewire_backend/device.rs:#> PipeWire playback: " x120
- CamillaDSP clipped samples added during the run: 0
- CamillaDSP processing load: mean 5.0 %, p95 6.7 %, max 8.6 %; buffer level: min 0, mean 0, max 0 samples
- PipeWire xruns added (pw-top ERR column, best effort): 140
- mpv frames added during the run: dropped by the display path 21, dropped by the decoder 0, delayed 0, mistimed 0; audio/video sync offset mean 0.0 ms, max 0.8 ms (absolute)
- CPU temperature: mean 48.5 C, p95 53.0 C, max 53.0 C; clock: mean 1504 MHz, p95 2617 MHz, max 2753 MHz; thermal-throttle events added: 0
- Stalls (share of the last 10 s with a task waiting, PSI): CPU mean 1.4 %, p95 3.1 %, max 3.1 %; I/O mean 0.2 %, p95 0.5 %, max 0.8 %; memory mean 0.0 %, p95 0.0 %, max 0.0 %
- Network received by this computer: mean 75.5 Mbit/s, p95 221.6 Mbit/s, max 246.3 Mbit/s

## Load per component

| component | CPU % (of one core) | RSS MB (mean / max) | processes seen |
|---|---|---|---|
| mpv | mean 45.4, p95 81.2, max 90.0 | 994 / 1105 | 1 |
| camilladsp | mean 7.0, p95 8.6, max 9.6 | 17 / 17 | 1 |
| pipewire | mean 1.3, p95 1.9, max 4.8 | 44 / 44 | 2 |
| wireplumber | mean 0.8, p95 1.0, max 14.4 | 34 / 34 | 1 |
| pipewire-pulse | mean 0.4, p95 1.0, max 4.8 | 28 / 28 | 1 |
| router | mean 0.4, p95 1.0, max 1.9 | 9 / 9 | 1 |
| upmix-engine | not seen | | 0 |
| omniphony-studio | not seen | | 0 |
| harletty | not seen | | 0 |
| theater-ctld | mean 0.0, p95 0.0, max 0.0 | 22 / 22 | 1 |
| seekthumbs | not seen | | 0 |
| ffmpeg | mean 0.0, p95 0.0, max 0.0 | 7 / 59 | 2 |

## mpv threads (CPU % of one core, by thread name)

| thread | mean | max | mean while mpv is above 80 % (6 samples) |
|---|---|---|---|
| worker | 12.6 | 41.1 | 30.4 |
| lua/uosc | 8.8 | 18.3 | 15.8 |
| vo | 10.5 | 16.6 | 14.5 |
| mpv | 4.2 | 6.8 | 5.4 |
| av:hevc:df3 | 1.3 | 3.9 | 2.7 |
| av:hevc:df2 | 1.3 | 3.8 | 2.7 |
| av:hevc:df0 | 1.5 | 4.9 | 2.7 |
| av:hevc:df1 | 1.3 | 4.8 | 2.5 |

## Whole computer

- CPU: mean 22.0 %, p95 41.6 %, max 43.9 % (100 % = all threads busy)
- RAM in use: mean 6089 MB, p95 6304 MB, max 6319 MB
- GPU (intel_gpu_top (sudo)): Render/3D busy mean 44.3 %, p95 50.1 %, max 54.3 %; Video (decode) engine busy mean 5.9 %, p95 7.6 %, max 8.5 %; clock mean 528 MHz, p95 609 MHz, max 628 MHz; power mean 3.3 W, p95 3.9 W, max 4.0 W; an integrated GPU's memory is part of the RAM figure above

Not measured: end-to-end audio latency (environment.txt lists the configured settings only).
