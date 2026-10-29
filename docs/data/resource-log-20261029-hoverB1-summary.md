# resource-log 20261029-200945 hover-B1-without-CamillaDSP

58 samples, 1 s apart; the load tables cover the 58 samples while mpv was running.
CPU is % of one core (200 = two cores busy). RSS is resident memory. Counters are totals added during the run.

## Problems: look at these first

- CamillaDSP log, while mpv was running (61 s): buffer-empty/underrun lines 0, overrun lines 0, clipping lines 0, ERROR/WARN lines 61
- CamillaDSP log, while mpv was not running (0 s): buffer-empty/underrun lines 0, overrun lines 0, clipping lines 0, ERROR/WARN lines 0
- most frequent problem messages while mpv was running: "#-#-# #:#:# WARN [camillalib::pipewire_backend::device] <src/pipewire_backend/device.rs:#> Capture: waited #s " x61
- CamillaDSP clipped samples added during the run: 0
- CamillaDSP processing load: mean 0.0 %, p95 0.0 %, max 0.0 %; buffer level: min 0, mean 0, max 0 samples
- PipeWire xruns added (pw-top ERR column, best effort): 0
- mpv frames added during the run: dropped by the display path 0, dropped by the decoder 0, delayed 0, mistimed 0; audio/video sync offset mean 0.0 ms, max 0.0 ms (absolute)
- CPU temperature: mean 46.4 C, p95 48.0 C, max 49.0 C; clock: mean 1169 MHz, p95 1395 MHz, max 1497 MHz; thermal-throttle events added: 0
- Stalls (share of the last 10 s with a task waiting, PSI): CPU mean 1.4 %, p95 2.6 %, max 2.6 %; I/O mean 4.4 %, p95 17.3 %, max 18.3 %; memory mean 0.0 %, p95 0.0 %, max 0.0 %
- Network received by this computer: mean 154.3 Mbit/s, p95 473.0 Mbit/s, max 485.6 Mbit/s

## Load per component

| component | CPU % (of one core) | RSS MB (mean / max) | processes seen |
|---|---|---|---|
| mpv | mean 25.2, p95 32.5, max 37.3 | 1007 / 1112 | 1 |
| camilladsp | mean 0.5, p95 1.9, max 1.9 | 13 / 13 | 1 |
| pipewire | mean 0.9, p95 1.9, max 1.9 | 44 / 44 | 2 |
| wireplumber | mean 0.4, p95 1.0, max 1.9 | 34 / 34 | 1 |
| pipewire-pulse | mean 0.2, p95 1.0, max 1.0 | 28 / 28 | 1 |
| router | mean 0.4, p95 1.0, max 1.9 | 9 / 9 | 1 |
| upmix-engine | not seen | | 0 |
| omniphony-studio | not seen | | 0 |
| harletty | not seen | | 0 |
| theater-ctld | mean 0.0, p95 0.0, max 0.0 | 22 / 22 | 1 |
| seekthumbs | not seen | | 0 |
| ffmpeg | not seen | | 0 |

## mpv threads (CPU % of one core, by thread name)

| thread | mean | max | mean while mpv is above 80 % (0 samples) |
|---|---|---|---|
| lua/uosc | 6.8 | 13.4 | n/a |
| vo | 8.8 | 12.4 | n/a |
| demux | 1.3 | 6.7 | n/a |
| mpv | 3.3 | 4.8 | n/a |

## Whole computer

- CPU: mean 14.4 %, p95 31.3 %, max 33.5 % (100 % = all threads busy)
- RAM in use: mean 6366 MB, p95 6481 MB, max 6518 MB
- GPU (intel_gpu_top (sudo)): Render/3D busy mean 44.7 %, p95 50.0 %, max 54.3 %; Video (decode) engine busy mean 5.7 %, p95 7.3 %, max 8.9 %; clock mean 569 MHz, p95 645 MHz, max 665 MHz; power mean 3.2 W, p95 3.4 W, max 3.5 W; an integrated GPU's memory is part of the RAM figure above

Not measured: end-to-end audio latency (environment.txt lists the configured settings only).
