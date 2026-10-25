# Live VBAP (Omniphony) or pre-baked files (Cavern/Cavernize)?

Research note, 25 October 2026. Written for this rig: Kubuntu laptop, `mpv-omniphony` with `harletty-bridge`, Omniphony 5.1.2 on a
measured layout, PipeWire, CamillaDSP, Vantec 7.1 USB, Z906 plus two ceiling heights, 10 x 10 ft room, bass-forward taste.

**Evidence tags.** Every important claim carries one:

- **[src]** verified by reading source or docs in the cloned repositories (`/home/claude/mgth/omniphony`, `/home/claude/mgth/mpv-omniphony`,
  `/home/claude/voidxh/Cavern`, and a read-only clone of `harletty/harletty-bridge` in the scratchpad). Source says what the code does, not
  how it sounds.
- **[author]** a claim by a project author or a project's own documentation. Not independent evidence.
- **[3rd]** a report by an independent forum poster. Anecdote, not a measurement.
- **[owner]** from this repository's own docs (the rig owner's measurements and statements).
- **[infer]** my reasoning from the above. Could be wrong.
- **[calc]** arithmetic I did here; the numbers are reproducible.

**No independent listening comparison or measurement of Omniphony against Cavern exists that I could find** (searches of Doom9, AVForums,
general web; see Sources). Nothing below about which one *sounds* better is established. What can be established is mechanics, practicalities
and risk, and how to settle the sound question in your room.

---

## 1. Verdict (short)

The question hides two independent choices, and they should not be argued together:

- **Axis A, the panner:** how an object position becomes speaker gains. Omniphony: VBAP (optionally MDAP spread). Cavern: its own
  "balance" (box interpolation) or "directional" (angle power law) renderer. Neither is Dolby's renderer, so neither is ground truth.
- **Axis B, the timing:** render at playback (live) or once, in advance (baked). Both renderers are, at heart, time-varying gain matrices
  [src]; computing them live costs almost nothing, so baking buys **no fidelity**, only reproducibility and independence from the player stack.
  Omniphony can also bake (`orender render ... --output-backend file`, raw float or CAF) [src], so "baked" does not imply "Cavern".

**In general.** Live rendering is better when layouts, trims or the renderer are still being tuned, when you want normal seek and streaming from a
remote library, and when the format coverage you need (TrueHD, DD+ JOC, DTS:X fixed 7.1.4) exists in the live decoder. Baking is better when you
want a frozen, portable, player-independent artifact, when the live stack is fragile or its version churn is a problem, or when a stage is too
expensive for real time (neither renderer has one by default). For plain object panning to speakers the two timings should sound identical if the
bake is 24-bit or float and level-matched [infer, high confidence].

**For this setup: keep Omniphony live as the primary path. Confidence about 75%.** The decision hinges on, in order:
1. Your layout is custom and measured; only Omniphony takes arbitrary measured positions as a first-class feature, per speaker, live [src].
   Cavernize's preset targets use fixed canonical positions; a custom layout reaches it only through the "Cavern Driver" target [src].
2. You change the rig often (delays, trims, heights, second sub, a new room in about 2030). Live re-tuning takes seconds; a bake means re-rendering
   every title [infer].
3. Cavernize's offline render is not usable on your OS as shipped: the GUI is WPF (`net8.0-windows`), its TrueHD path hard-codes `truehdd.exe`
   and a Windows download, and in the cloned tree `CavernizeCLI`'s render method is `throw new NotImplementedException(); // TODO` [src].
   Baking on Linux means your own port of the Cavernize CLI around the Cavern libraries (your Cavernize Linux project) plus a manual TrueHD
   decode step with `harletty` or `truehdd` [infer].
4. Your files sit on a debrid FUSE mount [owner]. Extracting an audio track from a 60-100 GB MKV means reading essentially the whole file; at
   200 Mbps, 80 GB is about 53 minutes of transfer per title [calc, infer], before any decode or render time.
5. DTS:X: Cavern has no DTS decoder at all [src]; Omniphony's DTS bridge decodes DTS-HD with DTS:X as a fixed 7.1.4 presentation, not dynamic
   objects [src, author] (and needs a newer stack than the one documented as installed; section 4).

What would change my mind: a blind, level-matched A/B (section 6) in which you reliably (9 of 10 trials) pick the Cavern render on at least two of
three clip types *and* prefer it. That would justify a **hybrid**, not a switch (section 5.3).

| Question | Answer | Confidence |
|---|---|---|
| Is live VBAP the better default for this rig? | Yes, mostly for practical reasons | 75% |
| Does VBAP on your measured layout image better than Cavern's 5.1.2 preset on canonical positions? | Probably slightly, unproven | 55-60% |
| Would a 24-bit/float bake from the *same* panner sound different from live? | No audible difference expected | 90-95% |
| Is a Cavern bake worth building as a second path on Linux? | Not now; only as a test instrument | 70% |
| Is Omniphony the riskier dependency (age, churn, bus factor)? | Yes, clearly | 80% |

---

## 2. What each method does (mathematics)

### 2.1 Do not conflate the two meanings of "Cavernize"

| Meaning | What it is | Where |
|---|---|---|
| **Cavernize as upmixer** (original, 2018-2019) | Creates height from ordinary channel content. A crossover (250 Hz default) keeps lows on the ground; a crude envelope/pitch measure on each channel's high band estimates "height", smoothed over time, and moves a second copy of the channel upward by `Height * EnvironmentSize.Y`. Heuristic, no metadata. | `Cavern/Filters/Cavernize.cs`, `Cavern/Remapping/CavernizeUpmixer.cs` [src]. Changelog 1.3: "Cavernize Lite is now open source" [src] |
| **Cavernize as Atmos renderer** (Oct 2022 onward) | A converter: decodes E-AC-3 JOC (and TrueHD via an external decoder, from Aug 2025) into beds plus objects, renders them with Cavern's object renderer to a chosen layout, writes a file. It also *contains* the upmixer as an option for object-less tracks. | `CavernSamples/CavernizeGUI`, `CavernizeCLI`, `Reusable/Cavernize.Logic` [src]. Changelog 1.6: "Decoding of E-AC-3 (JOC) into objects" [src]. Forum reports TrueHD added Aug 2025 [3rd] |

Cavern also has other upmixers (`SurroundUpmixer`, `SpectralDisassembler`, `PairBasedUpmixer`, `NearestUpmixer`) [src]. The Atmos rendering path does not use
any of them when the track has objects: `SetupUpmixer` only applies matrix upmixing `if (MatrixUpmixing && !Renderer.HasObjects)` [src].
Omniphony has its own analogue of the upmixer: optional "synthetic objects" (phantom extraction, broadband or per-band, and a height generator) that
are off by default and only act on fixed-channel sources without height [src: `docs/channel-render-modes.md`, `phantom-extraction-methods.md`].
The per-band mode adds about 21 ms on the whole bed when active [src, author-stated]. This note is about the Atmos renderer meaning.

### 2.2 Omniphony: VBAP

- **Layout to geometry.** Each non-LFE speaker becomes a unit direction from the listener. The speaker set is triangulated by a convex hull
  (Delaunay on the sphere); triplets are the faces [src: `spatial_vbap/vbap_native.rs`, ported from SAF's `saf_vbap.c` and Politis' VBAP library].
- **Gains.** For a source direction p inside a face of speakers l1, l2, l3: g = p^T * L^-1, then negatives clamped and the three gains
  normalised to unit power [src]. This is Pulkki's 3-D VBAP (Pulkki 1997, Eq. 18-19: [3rd-party paper, read]). In a pair it reduces to the
  tangent law [paper]. Constant power, image direction tied to **angles**.
- **Spread.** `spread_deg` > 0 turns it into MDAP: a ring of virtual sources around the direction, each panned, summed, renormalised [src]. Object
  `size` metadata (width, depth, height) is reduced to one spread value by `max` (default), `mean` or a projection rule [src: `size_to_spread.rs`].
  Streams tested by the bridge author carried size 0 [author: `OBJECT_SIZE_NOTES.md`], so spread is usually moot for film content [infer].
- **Layouts that do not close.** Where the speakers do not surround the listener (no floor speakers, no rears, only two heights) VBAP has an
  "out of hull" problem. Default mode `VirtualPoles` adds virtual speakers at uncovered poles and downmixes their gain at 1/sqrt(n) over adjacent
  real speakers (BS.2127 style); `Blend` and `Fade` are alternatives [src]. Coplanar faces (for example a ceiling quad) get a virtual centre speaker
  so a four-speaker face is not split along an arbitrary diagonal [src]. The author's own validation report says full level over the whole sphere
  is required and that the earlier fade-out was non-standard [author: `dsp-validation-report.md`].
- **Room model.** Atmos positions are room-relative cube coordinates. Omniphony scales them with room ratios (`room_ratio`, rear, lower, centre
  blend) into effect space, then pans by direction from the listener [src: `room_transform.rs`, `docs/volumetric-backend.md`]. Optional
  `volumetric`, `barycenter` and `hybrid` backends add depth (an object inside the room fades toward "central" distribution); a Lua or Rust
  backend can replace the panner [src]. Default VBAP ignores distance except through the shared attenuation decorators [src].
- **Fixed channels (beds).** Beds are *virtualised* by default: each bed channel is placed per source family as Room (a cube corner, so `L` is
  at 45 degrees, not ITU 30), Sphere (a stated angle) or Manual, then VBAP-panned. `spatialize: false` routes a channel one-to-one to the speaker of
  the same label; LFE is direct by default [src: `docs/placement.md`, `channel-render-modes.md`]. So a bed channel only plays from "its" speaker
  when your layout puts a speaker where the placement model puts that channel.
- **Bass management and per-speaker processing.** Each speaker may carry `freq_low`/`freq_high`; the engine builds LR4 crossover bands and pans each
  band only over the speakers that can reproduce it [src: `crossover/bands.rs`]. A band with no capable speaker is a coverage gap and content there is
  dropped [src]. Each output may also carry a FIR correction filter, gain and delay, applied after the mix [src: `docs/output-correction.md`]. This rig
  does none of that in Omniphony: delays, trims, EQ and height bass management live in CamillaDSP [owner: D14, home-theater note].
- **Time behaviour.** Gain changes ride a constant-rate slew (20 ms full-scale) [src: `channel-object-contract.md`]. A clock servo holds an
  end-to-end `latency_target` against the device clock [src: `docs/latency-regulation.md`].

### 2.3 Cavern: the object renderer

Cavern is a toolkit that began as a Unity audio engine; Cavernize is a sample application of it [src: `CavernSamples/*`, README].

- **Which renderer.** `Listener.ReplaceChannels` selects `BalanceBasedRenderer` if the layout is left-right symmetric, otherwise
  `DirectionalRenderer` [src: `Cavern/Listener.cs`, `Channels/SymmetryCalculator.cs`]. So your measured layout, if asymmetric, silently changes
  the algorithm.
- **BalanceBasedRenderer (symmetric layouts).** Box interpolation in cube space. Find the nearest speaker layer below and above the object's
  height, then in each layer the nearest front/back pair and the nearest left/right pair, and weight them by linear ratios on each axis; the
  gain applied to each speaker is `sqrt(product of ratios)`, so power sums to one (constant power) [src]. An exact hit snaps to the speaker. If a
  layer is incomplete the missing corner is copied from the other side, and if no layer exists above, the ground layer is reused [src:
  `FixIncompleteLayer`, "copy the bottom layer"]. Consequence for 5.1.2: all height energy goes to the two top speakers regardless of the object's
  depth, crossfaded against the ground layer by height ratio [src, infer].
- **DirectionalRenderer (asymmetric layouts).** Per speaker, `match = (pi - angle(object, speaker))^8`; in `Perfect` quality all speakers get a
  weight, otherwise the top three; the vector is normalised to unit power [src]. Far speakers keep a small gain: at 45 degrees off, `0.75^8` is
  about -20 dB; at 90 degrees, about -48 dB [calc]. This is a smooth angle-weighted law, not triplet VBAP. Cavernize runs `AudioQuality =
  Perfect`, update rate 64 samples [src: `ConversionEnvironment.cs`].
- **Size.** `Source.Size` exists and both renderers use it, but I found no place where the Atmos readers set it from object metadata [src by grep
  absence, infer]. Cavern most probably renders every Atmos object as a point source.
- **Panning law, side by side [calc].** Front-wall object between speakers placed at +-45 degrees (cube corners), by cube x position:

  | Object x (azimuth) | VBAP L/R gains, ratio | Cavern balance L/R gains, ratio |
  |---|---|---|
  | 0 (0 deg) | 0.707 / 0.707, 0 dB | 0.707 / 0.707, 0 dB |
  | -0.25 (14 deg) | 0.857 / 0.514, 4.4 dB | 0.791 / 0.612, 2.2 dB |
  | -0.50 (27 deg) | 0.949 / 0.316, 9.5 dB | 0.866 / 0.500, 4.8 dB |
  | -0.75 (37 deg) | 0.990 / 0.141, 16.9 dB | 0.935 / 0.354, 8.5 dB |

  Both are constant power. VBAP pushes the image toward the nearer speaker faster because it is built on the tangent law of *angles*; Cavern is
  linear in *position* and therefore moves more slowly toward the speaker. Neither is "right" in the abstract: VBAP is right if the speakers really
  stand at the assumed angles, and Cavern's law is right if listener-to-speaker geometry matches the cube. This is one concrete reason VBAP on a
  measured layout is attractive and Cavern on canonical positions is not.
- **Heights and presets.** Cavernize's presets use fixed positions (`ChannelPrototype.AlternativePositions`); the "5.1.2 side" preset uses
  *TopRear* positions for the pair "for smooth height transitions and WAVEFORMATEXTENSIBLE support"; "5.1.2 front" renders 5.1.4 and folds the
  rear heights to the ground; "matrix" variants fold through a wiring trick [src: `RenderTarget.Targets`]. Hidden `-heightsqueeze` moves overhead
  speakers toward the centre of the room [src]. A **custom** layout is only available as the "Cavern Driver" target, which reads whatever the Cavern
  configurator saved [src]. Ceiling speakers that are not at the cube's top corners therefore mean a mismatch between assumed and real geometry
  [infer].
- **LFE and bass.** With `LFESeparation = true` (set for object content) object audio is never sent to the LFE channel; only LFE-tagged bed
  content reaches it [src]. The LFE output gets a 120 Hz low-pass (class documented as "simple first-order"; its exact slope I did not verify)
  unless `DirectLFE` is set [src]. **There is no crossover that redirects object bass to a sub**: bass management is the playback system's job.
  A room-correction convolution filter can be applied at render time [src], which bakes the EQ in.
- **Gain safety.** Layouts with fewer than four overhead channels are rendered at 0.707 gain (-3 dB) "to prevent clipping" [src: `GetSafeGain`].
  Relevant for level matching: a 5.1.2 bake is 3 dB lower than the same panner without that factor.
- **Spatial remapping.** `SpatialRemapping.GetMatrix(contentChannels, outputLayout)` simulates each content channel as a source and renders it on
  the target layout with the Cavern renderer, returning a mixing matrix; exportable to Equalizer APO or XML [src]. This is how one would fold a
  7.1.4 file onto 5.1.2 later. It is a second panning stage (section 3).

---

## 3. Fidelity

| Aspect | Omniphony VBAP | Cavern / Cavernize | Basis |
|---|---|---|---|
| Ground truth | None (Dolby's renderer is proprietary) | None | [infer]. A Dolby patent describes a "center of loudness" cost-function panner and explicitly contrasts it with VBAP's triangulation [3rd: US 9,712,939]; that is a patent, not proof of what ships |
| Image law | Tangent/energy law on real angles | Linear in cube position (balance) or angle^8 weighting (directional) | [src] |
| Phantom quality | Sharp on a speaker, softer between; image width varies with direction (inherent to VBAP; MDAP spread exists but is size-driven) | Same variation, different shape; no spread from metadata in practice | [src, infer] |
| Non-standard / measured layout | First-class: any positions, triangulated automatically, edited live | Preset canonical positions; custom only via Driver target; asymmetric layouts switch algorithm | [src] |
| Two ceiling speakers, no rears, seat near rear wall | Hull faces with out-of-hull handling; rear ear-level objects land on the side pair plus heights; behaviour depends on your angles (not in the repo) | Heights get all overhead energy; rear objects fall back to the nearest layer corners | [src, infer]. Neither can create a rear image you have no speakers for |
| Object size | Mapped to MDAP spread | Likely ignored | [src, infer] |
| Beds | Virtualised through VBAP unless `spatialize: false` | Bed channels are sources at preset positions; on the preset layout they land on matching speakers | [src] |
| LFE | Direct; no object bass redirection unless speakers are band-limited | Bed LFE only, 120 Hz low-pass; no redirection | [src] |
| Bass management | Optional per-speaker bands (LR4) | None | [src] |
| Elevation cue | Level panning only; no spectral height cues in either | same | [infer, well known] |
| Decoding accuracy (JOC objects, TrueHD) | harletty: E-AC-3 decoder history shows noise bugs fixed in May 2026 notes, later state unverified | Cavern's JOC applier was criticised for artifacts on some objects in a 2022-23 thread | [author notes: `EAC3_PATCH_NOTES.md`, `eac3-coupling-debug.md`], [3rd: Doom9 thread, "some objects had distortion or artifacts"]. Neither decoder has an independent null test against Dolby's reference in anything I found |
| TrueHD | Own decoder lineage from `truehdd` (Apache-2.0); 5.1/7.1 outputs "very similar" to Dolby's reference player after normalisation | Delegates to `truehdd`, then reads DAMF | [3rd: tebasuna51 on Doom9, about truehdd] |
| Object count / level | Unlimited in engine | 16 for home cinema by Cavern's own guideline | [src, author] |

Two points deserve emphasis:

1. **Most of the audible "Atmos" in your room comes from the bed and from how you handle bass**, which both renderers leave to you. Your measured
   result (heights and sub within 2.6-2.7 dB rms of the bed, 40-400 Hz) was produced in CamillaDSP, downstream of either renderer [owner: status.md].
2. **A baked 7.1.4 then remapped to 5.1.2 is a double panning** (objects panned to 12 speakers, then each speaker signal panned again onto 8).
   A phantom of a phantom is expected to be softer than a direct render [infer]. If you bake at all, bake straight to your layout.

---

## 4. Practical comparison

| Topic | Live (Omniphony through mpv) | Baked (Cavern, or Omniphony file backend) | Basis |
|---|---|---|---|
| Latency / A/V sync | Decoder look-ahead plus render plus CamillaDSP chunks; host uses the reported latency for sync; you hear no lip-sync issue | No renderer latency at playback; same CamillaDSP delay; `--audio-delay` if needed | [src, owner] |
| Seeking | Engine resets on seek; no independent reports either way | Plain mpv seeking | [infer] |
| Subtitles, video | Untouched (original MKV plays) | Best practice: keep the original video and add the bake with `mpv --audio-file=baked.flac film.mkv`. Cavernize's own MKV merge via ffmpeg maps video and subtitles as copy; the direct Matroska PCM writer carries video tracks only, subtitle handling there not verified | [src, infer] |
| Codec: TrueHD Atmos | Yes (harletty dolby bridge) | Via `truehdd`/`harletty` to DAMF, then Cavern. In Cavernize this is Windows-only (`truehdd.exe`, `x86_64-pc-windows-msvc.zip`) | [src] |
| Codec: DD+ JOC | Yes | Yes, natively (`EnhancedAC3Renderer` with `JointObjectCodingApplier`) | [src] |
| Codec: DTS:X | DTS-HD MA/HRA with DTS:X decoded as a **fixed 7.1.4** presentation (the four heights reconstructed); every tested track was fixed, none carried extra objects | **None**: no DTS decoder in `Cavern.Format/Decoders` | [src, author] |
| Intermediate storage | None | TrueHD path writes `.atmos.audio` (reported about 14 GB) plus metadata beside the file, then the bake | [3rd: tebasuna51], [src: cleanup list] |
| Bake size, 8 ch, 48 kHz PCM | n/a | 16-bit 6.9 GB, 24-bit 10.4 GB, float32 13.8 GB for a 2.5 h film; FLAC typically about half (typical ratio, not measured) | [calc, infer] |
| Default bit depth | float through mpv/PipeWire | **16-bit PCM unless "force 24-bit" is set**; no dithering code in the library | [src: `MainWindow.Rendering.cs` line 75; grep for "dither" found nothing] |
| Export formats | Raw float or CAF (file backend) | AC-3 (6 ch), E-AC-3 (8), Opus, FLAC (8), PCM 16/float, ADM BWF, DAMF, LAF | [src] |
| Lossless-ness | Live path: float end to end | PCM or FLAC (24-bit): lossless relative to the render. **E-AC-3 export is a second lossy generation** (and 7.1 only); avoid. WAV over 4 GB is split into segments; a Doom9 user reported segments rejoined as 16-bit with no channel mask | [src, 3rd] |
| Re-render time | None | Not published; Perfect quality at 64-sample blocks is the slowest setting. **Unknown; time one title** | [src, unverified] |
| Change layout / trims later | Live, per speaker, seconds | Re-render every title. EQ, delays, trims in CamillaDSP survive a bake (your design), but anything in the renderer does not | [src, owner] |
| Use one file elsewhere | n/a | Only if the target matches your layout. A 5.1.2 8-channel WAV uses TopRear mask slots; how a given AVR maps it was not verified. A 7.1.4 bake is portable to bigger rigs but implies the double panning above | [src, unverified] |
| Robustness | Moving parts: mpv fork pinned to 0.41.0, `liborender`, three bridge libraries, PipeWire. Needs matching versions (below) | Playback is trivial; the render pipeline is the fragile part | [src] |
| Network / FUSE | Streams as you watch | Needs a full read of the container to extract audio | [infer] |
| Fire Stick | Bypasses everything | Bypasses everything | [owner] |

### Version coupling and how breakage shows up (Omniphony)

- The compatibility table in the README: v0.5.0-0.5.2 pair with `liborender` ABI 0.6-0.7 and bridge API 0.3.x; v0.6.0 with ABI 0.8 and bridge
  0.4.x; **v0.7.0 with ABI 0.12 and bridge 0.6.x** (harletty v0.9.0). A bridge loads only in a host built against the **same bridge_api minor**; an
  older or newer one is refused [src: README, `BRIDGE_API.md`]. In about five months that is three bridge-API minors.
- `liborender` has a stricter handshake: major mismatch means mpv refuses the library; minor additions are probed by symbol so older players keep
  working [src: `ABI.md`].
- **Breakage appears as**: a log error naming both versions (bridge/host mismatch) and `orender check-bridges` listing nothing loaded; or, if no
  engine loads, mpv decoding natively **without** spatial rendering, which for you would look like silent or missing height channels [src:
  `mpv-omniphony.md` fallback text; infer for your symptom]. Your `preflight` script already checks this.
- **Your installed stack looks old relative to upstream.** Your docs record `liborender` 0.3.0 and bridge API 0.3.0 (Studio 0.4.2), in other
  places "ABI 0.6 (0.3.0, commit 6ffaf21)"; the docs disagree with each other [owner]. Upstream today is v0.7.0 with a bridge that carries DTS and
  IAMF [src]. DTS:X support in your July research was "not covered" [owner]. Reaching DTS:X means upgrading engine, three bridge libraries and the
  player together, i.e. paying the churn cost.

---

## 4b. Maintenance and risk

| | Omniphony stack | Cavern / Cavernize | Basis |
|---|---|---|---|
| Age | First forum announcement 20 May 2026; releases v0.5.x to v0.7.0 since | Copyright 2016-2026; Cavern 1.0 in 2018; Atmos decode since Oct 2022 | [3rd: Doom9 thread dates], [src] |
| Activity | Repo HEAD 2026-10-21 (Omniphony), 2026-10-14 (mpv-omniphony), PR numbers in the hundreds (#785); harletty-bridge HEAD 2026-10-21 (PR #164) | Repo HEAD 2026-10-23; `CHANGELOG.md` stops at "2.0, April 2023" so it is stale as a status source; TrueHD arrived Aug 2025 | [src] |
| Bus factor | Appears to be one primary author (the only commit author in the shallow clones; contributors cannot be counted from a depth-1 clone). The decoder is a fork of another person's project | One primary author (all visible commits `VoidX`); `CONTRIBUTORS.md` lists very few outside contributors | [src, infer] |
| License | Omniphony and mpv-omniphony GPL-3.0; bridges GPL-3.0-or-later; `harletty` CLI Apache-2.0; `truehdd` Apache-2.0 | Custom Cavern licence: free, no selling, must link the repository, **public use such as screenings needs the creator's permission**; not an OSI licence. Fine for home use | [src] |
| Legal grey area | Format decoders are reverse-engineered ("No public spec exists for TrueHD") | Depends on the same external decoders | [3rd: truehdd author on Doom9] |
| ABI churn | High, with explicit policy, CI baseline tests and a documented version matrix | Low for files; library API changes with .NET releases | [src] |
| Project docs quality | Detailed, frank (the DSP report contains retractions, reverted attempts) | User docs live on a web page I could not fetch; source docs are thin | [src] |
| Linux status | First-class: PipeWire output, AppImage, AUR packages | Libraries are cross-platform; the GUI is Windows-only; CLI render unimplemented in the clone | [src] |
| Failure signature | Version mismatch error or silent fallback to native decode | Channel-order/mask mistakes (your July 2026 silent-heights bug is the case study) | [src, owner] |

Note for your own records: `CavernizeGUI`, `CavernizeCLI` and `Cavernize` are not separate public repositories (unauthenticated clones failed);
their sources are in `Cavern/CavernSamples` of the `VoidXH/Cavern` repository [src]. The assumption in the Cavernize Linux notes that the tooling is
closed source does not match what is in this clone. I could not list the VoidXH organisation (the sandbox blocked the API).

---

## 5. For your setup

### 5.1 Which is better, and why

**Omniphony live**, for these reasons in order of weight:

1. **Measured layout as input.** You measured positions from the seat and want them in the renderer (home-theater note) [owner]. VBAP uses the
   directions from the listener; Cavern's presets do not.
2. **Tuning velocity.** Layout, per-speaker gains and the object test can be changed live (`/omniphony/control/object_test`, orbit mode, speaker
   test; meters over OSC) [src]. Nothing comparable exists for a bake.
3. **CamillaDSP downstream already carries what a bake would otherwise freeze.** Because EQ, delays, trims and height bass management are not in
   the renderer, a bake would still be re-tunable at the DSP stage. This *reduces* baking's main drawback, but does not remove the need to
   re-render for any layout change.
4. **Wayland and PipeWire** are not a differentiator: the live path outputs through PipeWire and your router already handles any channel
   count; a baked file played in mpv uses the same path. The only stack-specific hazard is channel negotiation for a baked 8-channel file
   (your July silent-heights bug), which needs the index-based `channelmap` workaround again [owner: `omniphony-debugging.md` item 6].
5. **Content.** Mostly Atmos files, TrueHD and DD+ JOC, from a streamed library [owner]: live avoids the full-file read.

**What favours Cavern/baking for you, honestly:** (a) decoupling from Omniphony's version churn; (b) a frozen reference that you can archive and
A/B repeatedly; (c) offline settings you cannot get live. For (c), Cavernize's "Perfect" quality and room-correction convolution at render exist [src], but a
gain-matrix panner gains no fidelity from offline compute, and room correction baked in contradicts your live CamillaDSP workflow [infer].

**Live-room-correction changes.** Because the DSP is downstream, changing EQ never requires a re-render. This is the same for both methods as
long as you do not enable Cavernize's render-time room correction.

**Two heights.** Both methods can only place height energy on two ceiling speakers. VBAP does it by hull face and elevation angle, Cavern by a
vertical crossfade between bed layer and top layer, with all depth collapsed. Which sounds better for your seat against the back wall is exactly
what the A/B settles (section 6) [infer].

### 5.2 A thing you may be missing: Omniphony's native bass management

Omniphony can band-limit speakers (`freq_low`) and pan each frequency band only over speakers that can reproduce it [src]. In your chain the
heights are bass-managed bluntly in CamillaDSP (D14: RL+RR low-passed at 140 Hz LR4 and added to the LFE at 0 dB). A native alternative would pan
low-band object energy over the *bed* speakers (and their sub) with VBAP, keeping direction, rather than summing the heights' bass to the sub
[infer]. Costs: it changes a tuned, verified chain; the "coverage gap drops content" rule needs care; I have not seen anyone test it. Worth a
single A/B on height-heavy bass scenes, not a recommendation to change now.

### 5.3 Hybrid options and cost of switching

| Option | What | Cost | Verdict |
|---|---|---|---|
| H1: Omniphony live for everything | Status quo | Version-matching discipline; pin versions and keep the installer script | Recommended |
| H2: Omniphony bake as test instrument | `orender render FILE --output-backend file --output-file X.f32 --output-file-format raw-f32` with your own `config.yaml` layout (flags per the QUICKSTART; confirm with `orender render --help` on your version), then `ffmpeg -f f32le -ar 48000 -ac 8 -i X.f32 -c:a flac` | An hour to set up; per clip, seconds | Use it to prove live and baked are the same (null test) and to archive reference clips |
| H3: Cavern bake for specific titles | Decode to DAMF with `harletty`/`truehdd`, render with your Linux Cavernize CLI to a custom or 5.1.2 target, 24-bit FLAC, play with `--audio-file` | Needs the CLI render finished (upstream is a TODO), then full-file read, about 14 GB intermediate, unknown render time, router profile forced (`eq mode film`) | Only if the A/B shows a consistent Cavern preference |
| H4: Cavern 7.1.4 bake then remap to 5.1.2 | Portable master | Double panning, extra stage, 12 channels (13.8 GB float) | Not recommended |
| H5: Switch fully to baked | | Rebuild the workflow around a pipeline that is unfinished on Linux; lose live tuning; DTS:X unsupported | Not recommended |

Reversibility: H1 and H2 cost nothing to undo. H3 is additive. The expensive failure is H5.

---

## 6. A/B test protocol for your room

Goal: answer three separate questions, cheapest first. (1) Does live equal baked for the same panner? (2) Do the two panners put objects where
they should, on paper? (3) Can you hear a difference in your room, blind, and which do you prefer? Your existing tools carry most of it:
`scripts/rec.sh`, `scripts/make-bedtest.py`, REW, `eq` commands, the Dayton mic [owner].

**Ground rules (apply to every step).**
- Same speakers, same seat (the stool with wedge, ear at about 2 ft), same Z906 knob positions (D12), same CamillaDSP preset. Force the profile so
  the router cannot choose differently: `eq mode film` before the test, `eq mode auto` after [owner: runbook].
- Same excerpts for every candidate. Cut a 30-40 s clip from the source with stream copy and play *that* in every case:
  `ffmpeg -ss HH:MM:SS -t 40 -i film.mkv -map 0:v:0 -map 0:a:N -c copy clip.mkv` (check stream index N with `ffprobe`).
- **Level match first, to within 0.5 dB.** Cavern's 5.1.2 render is at 0.707 gain unless you compensate; Omniphony has its own master gain.
  Measure each candidate's playback: record at the seat (`./rec.sh gain` once, then `./rec.sh NAME 45`), then
  `ffmpeg -i NAME.wav -af ebur128=peak=true -f null -` and compare integrated loudness (LUFS) and, for bass-heavy clips, the 20-120 Hz band in REW.
  Trim the louder candidate down (in CamillaDSP or with `mpv --volume`). Never trim up; D3 (cut-only) still holds.
- Check the mic does not clip (peak under about -12 dBFS; `./rec.sh check FILE`).
- Expect single-seat, single-mic repeatability of 1-2 dB [owner]. Any difference smaller than that is noise.

**Step 0. Channel mapping proof for the baked file (15 min).** Run `make-bedtest.py` T1 through `mpv-atmos` to remind yourself of the
order. For a baked 5.1.2 file whose layout is FL FR FC LFE SL SR TBL TBR (WAV order for Cavern's "5.1.2 side" [src]), remap to your DAC order
(FL FR Height-L Height-R FC LFE SL SR) before playing, for example `-af "channelmap=map=0|1|6|7|2|3|4|5:channel_layout=7.1"` (derived from the same
trick that fixed July's bug; confirm with a per-channel tone, because I did not run it). Pass if every channel lands on the speaker you expect.

**Step 1. Live vs baked, same panner (null test, 30 min).** Bake one clip with Omniphony itself (H2) using the same `config.yaml`. Play live and baked,
record both at the seat, or better, record the digital output with `pw-record` on the monitor of the sink if you have one. Compare level and, if the
two digital captures are sample-aligned, subtract them and report the residual in dB. **Expected** (not guaranteed): residual near or below -60 dB
re full scale, apart from a constant offset and an alignment shift [infer]. If it is much worse, there is a hidden difference (ramps, `decode_thread`,
latency regulation) worth understanding before judging Cavern. This is the step that tells you whether "baked vs live" is a real axis at all.

**Step 2. Room-free gain comparison (1-2 h, no mic).** For a fly-over clip, get per-speaker gains over time from each renderer: Omniphony's meters
over OSC (or the gains it logs) and the per-channel RMS from the baked Cavern file. For each time step compute the Gerzon energy vector
`rE = sum(g_i^2 * u_i) / sum(g_i^2)` using **your measured speaker unit vectors**; report image direction error against the object's own
direction and `|rE|` (focus). Higher `|rE|` and lower angle error mean a tighter, more accurate image [model-based]. Plot both. This costs nothing in
the room and shows where the two methods differ, notably in the zone between bed and heights. Caveat: it assumes you know the object's intended
direction in your own angles, which depends on how the room cube is anchored to an off-centre seat (unverified, section 7).

**Step 3. Object sweep with the mic (45 min).**
- Live: use Omniphony's object test: pink noise placed at a position, with `/omniphony/control/object_test` and the orbit command
  (`/control/object_test/rotation`, axis, diameter, period) [src]. Run one horizontal orbit (axis z, diameter 2, period 20 s) and one rising path
  (a slow `free` orbit). Record at the seat.
- Baked: a Cavern render of the *same* motion needs an authored object file; Cavern can read ADM BWF and has a sample for writing one
  (`docs/Code samples/ADM creation.md`) [src]. If that is too much work, skip this arm and keep the live arm as a smoothness check.
- Read: (a) level versus time with the 1/3-octave or SPL log in REW. A constant-power panner should hold loudness within about 2 dB around the
  orbit; a deeper dip between speakers or at a bed-to-height transition marks a weak spot; (b) by ear, walk through the orbit with eyes closed and
  note where the image jumps, collapses to a speaker, or goes inside your head (typical at the rear with no rear speakers).

**Step 4. Blind, level-matched listening (1-2 h).**
- Candidates: L = Omniphony live (or H2 bake, identical by Step 1), C = Cavern bake at "5.1.2 side" on the preset, optionally C2 = Cavern via
  the Driver target with your measured layout, which is the fair comparison for your room.
- Clips (30-40 s each, ones you own): a helicopter or aircraft fly-over (trajectory test), a rain/ambience scene (bed and diffuse height),
  a dialogue-plus-score scene (centre anchoring, no height needed), and one bass-forward action scene (the F1 / Godzilla / Tenet class you already
  used [owner]) to check heights plus bass management.
- Blinding: have a script, or a helper, play them in random order under neutral names. Example:
  ```bash
  mkdir -p blind && cd blind
  for c in L C; do for k in fly rain dlg bass; do ln -sf "../${k}_${c}.mkv" "tmp_${k}_${c}"; done; done
  # shuffle: 10 trials per clip class, each trial plays X (random of L or C), you say which it was after hearing A (L) and B (C) first
  ```
  Keep the key in a file you do not open until the end.
- Trials: ABX, 10 per clip class. With 10 trials, 9 correct gives p of about 0.011 and 8 correct gives p of about 0.055 (one-sided binomial,
  [calc]); require 9 of 10 before you accept "I can hear it".
- If you can discriminate, then preference scoring (1-5) on: trajectory smoothness, overhead feel (do things come from above?), front image and dialogue
  anchoring, bass weight in height-heavy scenes, artefacts (zipper, pumping, distortion).
- Do not run more than 4-5 trials in a row; fatigue wipes out the effect. Rest 10 minutes between clip classes. Record the room noise floor once.

**Decision rule, set before you start.**
| Result | Action |
|---|---|
| Cannot discriminate (below 9 of 10 on two or more classes) | The panners are equivalent in your room. Stay live, decide on practicalities. Done |
| Discriminate and prefer VBAP | Stay live. Done |
| Discriminate and prefer Cavern on two or more classes | Try Cavern via the Driver target with your layout to see if it is the geometry; if it still wins, adopt H3 for chosen titles only |
| Step 1 residual is large | Investigate Omniphony live/offline difference first; results of Step 4 are not comparable until understood |

---

## 7. Unverified items (could not establish)

1. **Which one sounds better.** No independent listening test or measurement of Omniphony versus Cavern exists in what I found. All differences
   above come from source code and author docs.
2. **Your actual Omniphony layout.** `~/.config/omniphony/config.yaml` is not in the repository (your docs say "contents not yet confirmed"). I could
   not compute where VBAP puts rear or ceiling objects for your exact speaker angles. Suggest committing the layout YAML to this repo.
3. **How the object cube is anchored to a seat against the back wall.** Both renderers assume a cube with a listener at its centre; I did not
   establish how Omniphony's room ratios, rear ratio and your measured positions interact. This affects every ear-level and overhead object.
4. **Cavern render time and CPU load** for a feature film in Perfect quality. No published figure found. Time one title.
5. **Whether upstream's `CavernizeCLI` render is finished in a newer release.** In the clone it is a `NotImplementedException` TODO; the Cavernize
   installer (Windows) may differ from the repository.
6. **Cavernize subtitle handling** in the direct Matroska PCM writer.
7. **How AVRs interpret a baked 5.1.2 WAV/FLAC mask** (TopRear slots) and whether a baked file plays correctly in other players.
8. **Seek behaviour and long-run stability of `ad_orender`.** No independent reports; your own use reports no lip-sync problem only.
9. **Whether your installed versions support DTS:X** and which versions are really installed (your docs disagree: 0.3.0 versus 0.6).
10. **DD+ JOC decode accuracy** against Dolby's reference for either decoder. Only forum anecdotes ("some objects had distortion or artifacts" for
    Cavern, 2022-23; the harletty E-AC-3 notes record bugs fixed in May 2026 with the later state unknown).
11. **The exact LFE low-pass slope in Cavern** (documentation says first-order, implementation derives from a biquad).
12. **Whether Cavern ignores object size** (grep found no assignment; not a proof).
13. **Bus factor and contributor counts** (shallow clones; GitHub API blocked).
14. **Claims from author docs, not independently checked:** that VBAP out-of-hull behaviour conforms to ITU-R BS.2127; that tested DTS:X
    tracks were all fixed 7.1.4; that the harletty TrueHD decoder is accurate; that Cavern's guidelines yield "a very close or equal listening
    experience to official decoders".
15. **Operational numbers** I computed assume 48 kHz, 8 channels, 2.5 h and typical FLAC ratios; a real 2 h 40 min title differs.
16. **The Dolby patent** is cited only as a statement of a method contrasted with VBAP, not as a description of Dolby's shipping renderer.

---

## Sources

Code and docs read (local clones, all read-only):
- Omniphony: `/home/claude/mgth/omniphony` (`README.md`, `omniphony-renderer/ABI.md`, `BRIDGE_API.md`, `QUICKSTART.md`, `docs/placement.md`,
  `channel-render-modes.md`, `channel-object-contract.md`, `phantom-extraction-methods.md`, `output-correction.md`, `latency-regulation.md`,
  `volumetric-backend.md`, `from-file-evaluator-architecture.md`, `dsp-validation-report.md`, `mpv-omniphony.md`, `install/linux.md`,
  `layouts/5.1.2.yaml`; `renderer/src/spatial_vbap/vbap_native.rs`, `render_backend/size_to_spread.rs`, `crossover/bands.rs`)
- mpv-omniphony: `/home/claude/mgth/mpv-omniphony` (`README.md`, `mpv-fork.env`)
- harletty-bridge: https://github.com/harletty/harletty-bridge (clone in the session scratchpad; `README.md`, `OBJECT_SIZE_NOTES.md`,
  `EAC3_PATCH_NOTES.md`, `docs/eac3-coupling-debug.md`, `docs/dtsx-objects-campaign.md`, `docs/dtsx-lossy-carrier.md`, `docs/truehdd-fork-retirement.md`)
- Cavern: https://github.com/VoidXH/Cavern (clone `/home/claude/voidxh/Cavern`, HEAD 2026-10-23: `Cavern/Rendering/BalanceBasedRenderer.cs`,
  `DirectionalRenderer.cs`, `Listener.cs`, `Remapping/*`, `Filters/Cavernize.cs`, `CavernSamples/CavernizeCLI/Program.cs`,
  `CavernizeGUI/*`, `Reusable/Cavernize.Logic/*`, `docs/Guidelines for object-based movie audio.md`, `LICENSE.md`, `CHANGELOG.md`)
- This repository: `docs/architecture.md`, `decisions.md`, `status.md`, `technical-writeup.md`, `omniphony-debugging.md`, `runbook.md`, `measurement.md`,
  `scripts/make-bedtest.py`, `scripts/rec.sh`

Web (author claims versus user reports marked in the text):
- Doom9, "Spatial Audio Rendering for Home Cinema" (Omniphony author's announcement, 20 May - 15 Jul 2026): https://forum.doom9.org/showthread.php?s=0e7b8ae61ea579d9441a1ed5cef5a87e&p=2031329#post2031329
- Doom9, "TrueHDD: A new TrueHD decoder with Atmos support": https://forum.doom9.org/archive/index.php/t-186454.html and https://forum.doom9.org/showthread.php?p=2021628
- Doom9 Atmos-on-PC thread (Cavern 1.6-era reports, 2022 to Aug 2025): https://forum.doom9.org/showthread.php?p=1977210
- AVForums, "Atmos decoding on a PC" (Cavern described as a file converter, not a real-time decoder): https://www.avforums.com/threads/atmos-decoding-on-a-pc.2534199/latest
- Pulkki, "Virtual Sound Source Positioning Using Vector Base Amplitude Panning" (1997): https://www.audiolabs-erlangen.com/resources/aps-w23/papers/sap_Pulkki1997.pdf
- US patent 9,712,939, "Panning of audio objects to arbitrary speaker layouts" (Dolby): https://patents.justia.com/patent/9712939
- DD+ JOC description (lossy carrier, parametric object layer, bitrates): https://cinemaconfig.com/reference/dd-plus-joc
- Pages that could not be read (empty or blocked): cavern.sbence.hu Cavernize and downloads pages, quadraphonicquad.com Omniphony threads, AUR package page,
  harletty-bridge releases page.
