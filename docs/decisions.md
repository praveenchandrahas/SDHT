# Design decisions

Short records of why things are the way they are. Format: decision, reason, what would change it.

## D1. 5.1.2 and nothing bigger
10 x 10 ft room with no space behind the seat, so rear and extra height speakers (7.1.4, 5.1.4) are not practical.
Side-surround placement for SL/SR. *Revisit* if the room changes (a new room is planned later; see roadmap).

## D2. DSP is CamillaDSP inside the PipeWire graph
CamillaDSP exposes `camilladsp-capture` / `camilladsp-playback` as PipeWire nodes, so mpv, the DSP and the hardware
stay independent and rewireable (qpwgraph shows it). *Cost:* links to CamillaDSP are lost on every restart, which is
why a router exists.

## D3. EQ is cut-only
Nulls cannot be filled by boosting; boosting also eats headroom and risks clipping. All presets only cut, and the
alignment trims only lower levels. *Consequence:* EQ on is quieter than EQ off.

## D4. Bass is voiced above flat, on purpose
A flat correction sounded lean and hollow for a listener who wants thump. Presets target a deliberate hump (8-20 dB above
the mids), then trim the boomy part by frequency (`drone` sets). *Revisit* if the speakers or the seat change.

## D5. Separate drone from thump with narrow cuts
In film scores the boomy drone (63-92 Hz) and the thump (56-63 Hz) occupy different frequencies, so static narrow cuts
at 72 and 84 Hz work without a dynamic processor. *Limit:* it also dents any music note at those frequencies.

## D6. Align to the farthest speaker
Delays can only be added, so every speaker is delayed to match the farthest (FR); the heights end up with the largest
delays but nothing else depends on them. (First idea, delaying the whole bed for the heights' sake, was rejected: get the 5.1 bed right first.)

## D7. `--align=bed` leaves the heights alone
The owner is fine with heights slightly hot and mostly relies on the bed for imaging. The height delay and trim numbers
are measured and stored (`ALIGN`) but only applied with `--align` (no value).

## D8. Do not invert the centre
An early analysis suggested it was inverted; the proper pair test showed all speakers in phase. `--invert` is kept as a tool.

## D9. Measure with a separate mic device, remove clock drift in the fit
The mic is on a different USB device than playback, so timing uses a chirp train and a least-squares fit that separates
clock drift from speaker delay. REW's own arrival times (no timing reference) are not used.

## D10. The router polls instead of using WirePlumber rules
CamillaDSP is a *stream* in PipeWire, not a sink, so a rule that points mpv at it would leave mpv silent whenever CamillaDSP
is down. A small poller with make-before-break and an automatic direct fallback makes "never silent" a property of the
design. *Cost:* up to half a second of direct (un-EQ'd) sound when mpv starts.

## D11. `eq off` bypasses everything
Off means mpv goes straight to the USB interface: no bass EQ, and no delays or trims either. A "bass EQ off but keep
alignment" mode would need CamillaDSP to reload its config live while keeping its ports, which has not been verified. *Revisit* if that is wanted.

## D12. Z906 knobs are fixed references
The tuning assumes the Z906 sub level as it is. Change the master volume freely; change the sub level only with a re-measurement.
