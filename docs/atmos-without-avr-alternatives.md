# Atmos to loudspeakers without an AVR: is there anything besides Omniphony and Cavern?

Research date: 2026-10-25. Target rig: Kubuntu 24.04 laptop, PipeWire 1.0.5, CamillaDSP 4.1.3, USB 7.1 DAC into a Z906 plus two ceiling heights (5.1.2), see [architecture.md](architecture.md) and [technical-writeup.md](technical-writeup.md).

Evidence labels used throughout: **[V]** verified by me by reading the primary source (repo files cloned on 2026-10-25, or the web page named); **[C]** a claim by the vendor, author or a forum poster that I could not independently confirm; **[I]** my inference.

## 1. Verdict (short)

1. For the real use case (MKV TrueHD Atmos or DD+ JOC files, decoded and rendered live to analog speakers from a PC, with picture in sync), **I found no third path.** Omniphony with harletty-bridge is the only live, object-aware, open, cross-platform route. Cavern/Cavernize is the only other object-aware route I can confirm, and it is a file renderer (Cavern's own README says TrueHD Atmos is "in Cavernize only, with Truehdd").
2. **Windows adds nothing.** Dolby Access "Atmos for Home Theater" is an HDMI-bitstream feature that only shows up when the sink reports Atmos. Microsoft's own spatial sound page does not mention analog or USB endpoints at all. Omniphony itself already runs on Windows (ASIO or WASAPI), so a Windows machine would only be a different host for the same engine.
3. **There is one commercial, official path that does exactly what is asked, on macOS:** Dolby Reference Player (about $400 per one 2022-era write-up, price not re-verified) rendering TrueHD or .ec3 files to a multichannel aggregate device, up to 9.1.6. A user with an Okto dac8pro and a 5.1.2 layout reports it works. It is an audio file QC player with no picture, so it is a **reference to listen against, not a replacement for the film path**.
4. Everything else is either (a) a decoder with no renderer, (b) a renderer with no Atmos decoder, or (c) hardware that decodes Atmos but costs far more than the problem is worth. The useful new facts are that the ecosystem around the current stack is moving fast (truehdd 0.6.2 in Sept 2026, harletty split into Dolby/DTS/IAMF plugins, Omniphony at 0.7.0), and **this rig is on mpv-omniphony 0.4.2 while 0.7.0 is current**.
5. DTS:X: nothing beyond harletty. It decodes DTS:X as a **fixed 7.1.4 (twelve labelled channels), not as objects**; I found no other open DTS:X decoder.

## 2. Per-path evidence

Status key: **works today** / **partially** / **not feasible** / **unverified**.

### 2.1 Windows and Dolby's own PC stack

| Path | Status | Evidence | Notes |
|---|---|---|---|
| Dolby Access "Dolby Atmos for Home Theater" to a USB DAC with analog speakers | **not feasible** | Microsoft moderator answers: the option "only appears when Windows detects a compatible HDMI audio device that supports Dolby Atmos"; optical/S-PDIF will not show it; the PC passes a bitstream and the soundbar or AVR decodes and does speaker layout. [V] (learn.microsoft.com answers 12807694 and 5909641, community answers, not Microsoft documentation) | The rendering is done by the downstream device, which is exactly what is being avoided. |
| Windows spatial sound API (`ISpatialAudioClient`) | **not feasible for this goal** | Microsoft's page lists the output formats as Dolby Atmos for Home Theater (7.1.4 bed, 20 dynamic objects on Windows), DTS:X for Home Theater (8.1.4.4 bed, 32 objects), headphone formats, and built-in-speaker formats; it "does not address analog or USB multichannel endpoints". [V] (learn.microsoft.com Windows/win32/coreaudio/spatial-sound, ar-sa mirror) | `ISpatialAudioClient` is an app-to-renderer API. It lets an app send objects to whatever spatial renderer the user selected; it is not a decoder, and I found no mechanism for a third party to supply a speaker renderer for a USB DAC. [I] |
| CRU EDID trick (8-channel LPCM) | **partially** (7.1 LPCM only) | Poster added 8-channel LPCM to the EDID and got real 7.1 LPCM; Windows caps layouts at 7.1; "does not create a native Atmos endpoint". [V] (answers 5909641) | Irrelevant unless something upstream decodes Atmos. |
| Dolby Atmos Renderer (the 2023 merged Production plus Mastering Suite) | **partially / unverified for playback** | $299 new, $50 upgrade, from Avid Store, March 2023. Mac (Apple silicon native) and Windows; on Windows it "must run on a separate computer from the DAW". [V] (soundonsound.com, production-expert.com) Dolby's guide lists Core Audio (Mac), a Send/Return driver (Mac) and ASIO (Windows, Mastering Suite only); monitoring up to 22 speaker channels; it covers playing a master or media file in section 14 but the excerpt I got was cut off. [V] | Built to monitor mixes from a DAW and create masters. I could not confirm that it opens TrueHD/MLP (the guide mentions "MLP Lossless" only in the trademark list) or plays a bitstream as a consumer player. Also not confirmed which monitor layouts (5.1.2?) exist. Treat as a content-creation tool. |
| Dolby Atmos Music Panner / Production Suite as a "player-side live renderer" | **not feasible as a player** | The Music Panner is a DAW plug-in feeding the Renderer (same sources). [V] | No evidence it is intended or usable as a consumer playback chain. |
| Dolby Reference Player (DRP) | **works today (macOS), partially elsewhere** | Dolby: "stand-alone, file-based application for playback and QC" of Dolby Digital, DD+, TrueHD, AC-4 and Atmos, and it "renders Dolby Atmos to a specified speaker configuration". [V] (professional.dolby.com DRP page; OS list and price not stated there). A write-up: costs $400, outputs up to 9.1.6, plays .mlp and .ec3, uses a macOS aggregate device "Atmos Out", per-channel assignment in Window > speaker configuration. [C] (immersiveaudioalbum.com/?p=18267, date not stated). A forum poster plays TrueHD files in DRP into an Okto dac8pro for a 5.1.2 layout. [C] (avnirvana.com thread 10312). Audiophilestyle: DRP "is a file player with no input routing". [C] | Needs bare .mlp/.ec3 extracted from MKV, no video sync. Windows build, current price and home-use licence terms: **unverified** (Dolby's store pages were access-restricted to me). |
| Dolby "Atmos Connect" | **unverified (probably means FlexConnect)** | I found no product named "Atmos Connect". I found Dolby Atmos **FlexConnect**, a TV-driven wireless speaker feature on 2025 LG and TCL TVs. [C] (search-result titles and press-release URLs only; I did not read the pages) | TV feature, not PC. Not relevant to this rig. |
| Windows 11 2025-2026 spatial audio changes | **unverified** | Searches returned only how-to pages. I found no news of a custom-speaker Atmos renderer for USB DACs. | Absence of evidence, not proof. |

### 2.2 Open-source decoders and renderers

| Path | Status | Evidence | Notes |
|---|---|---|---|
| **truehdd** (Rainbaby) | **works today (decoder only)** | README: CLI for decoding TrueHD; "Experimental ... not intended for production environments or consumer playback"; v0.6.2 released 2026-09-15, repo last commit 2026-10-23. [V] (cloned github.com/truehdd/truehdd). Doom9: outputs `.atmos` (DAMF header), `.atmos.metadata` (YAML object positions) and a 16-channel 24-bit 48 kHz CAF; "rendering is out of scope"; no TrueHD spec existed, author read FFmpeg `mlpdec.c` and reverse-engineered; the object metadata format is shared with E-AC-3 JOC. [V] (forum.doom9.org t-186454). | Decoder with no renderer and no live mode. The reason Cavern and harletty exist. Caveats posted: bed is often only the LFE; no DRC; channel order differs from DRP; one user reported >8 channels failing (unresolved). [C] |
| **harletty** CLI and **harletty-bridge** | **works today** | Fork of truehdd, "85% byte-identical to upstream"; adds E-AC-3 JOC, DTS/DTS:X and Auro-3D, IAMF input; writes DAMF or CAF/WAV; Apache-2.0. Bridge ships `dolby`, `dts`, `iamf` plugins for Omniphony. [V] (cloned harletty/harletty-bridge, last commit 2026-10-21) | This is the Omniphony path, not an alternative. But its CLI **is** the only thing I found that turns TrueHD, DD+ JOC, DTS:X and IAMF into Atmos master files on disk. |
| **FFmpeg** TrueHD object extraction | **not feasible today** | A patch "avcodec/mlpdec: Add decoding of object audio data" (Massimo Eynard, 2025-03-22) adds an off-by-default `extract_objects` option that outputs raw object feeds as "unspecified order" channels, no side data; a reviewer (James Almer) noted a 7.1.4 layout guess for 12 channels. The pages show no merge or final decision. [V] (ffmpeg.org pipermail 341429, 341555) | Even if merged it gives PCM object tracks without the position metadata, so it cannot render. I did not find a fork that exposes the OAMD metadata through FFmpeg. [I] |
| **Cavern / Cavernize** (VoidXH) | **works today (offline), partially live** | README: TrueHD Atmos "in Cavernize only, with Truehdd"; DD+ JOC; ADM BWF; DAMF; renders to any layout, QuickEQ exports CamillaDSP filters. [V] (cloned VoidXH/Cavern, last commit 2026-10-23). DAMF reader and writer classes exist in `Cavern.Format`. [V] AVForums 2025: TrueHD support landed Aug 2025, real-time version "in development". [C] | Already known to you. A useful second opinion because it is an independent renderer. |
| **libspatialaudio 0.4.0** | **partially (renderer, no Atmos decoder)** | Released 2025-12-21; ObjectPanner (VBAP) and a Renderer with spread, divergence, zone exclusion; HOA to 3rd order; binaural and loudspeaker outputs; IAMF compatibility stated; Dolby Atmos only "potentially". [V] (jbkempf.com/blog/2025/libspatialaudio-0.4) | Needs someone to feed it objects. Used by VLC. Whether VLC 4 uses it for Atmos: **unverified** (no evidence found). |
| **IAMF / Eclipsa Audio** | **partially (open renderer exists, no Atmos bridge found)** | AOMedia published Open Audio Renderer v1.0.0, dated 2026-05-27 (spec), announced 2026-07-30: loudspeaker and binaural renderers for channel, scene and object IAMF content; it does not mention ADM or Atmos. [V] (aomedia.org/specifications/oar/1.0.0, audioxpress). IAMF supports layouts such as 5.1.2 and 7.1.4. [V] (opensource.googleblog.com, DAW plugin post) Google's DAW plug-in is Pro Tools on macOS only at launch. [V] Harletty ships an IAMF decode plugin and Omniphony has IAMF-in-Matroska plans (the plan says "nothing ... has been listened to on speakers"). [V] (Omniphony docs/iamf-matroska-plan.md) | I found **no tool that converts Atmos to IAMF** other than possible work inside the harletty/Omniphony ecosystem (a "harlettizer" encoder is referenced in an internal plan; not verified as shipped). IAMF is mostly a way to author new content, not to play your existing Atmos library. |
| **EBU ADM Renderer (EAR) / EAR Production Suite** | **partially (offline), not as a player** | `ear-render` renders BW64/ADM files to BS.2051 layouts including 0+5+0, 2+5+0, 4+5+0 and 4+7+0; v2.1.0 dated 2022-01-26; BSD-3-Clause-Clear; page describes file-based rendering. [V] (pypi.org/project/ear). EAR Production Suite is DAW (VST) tooling from BBC R&D/IRT; Linux support and real-time not stated. [V] | Needs an ADM file. Atmos to ADM requires the Dolby Renderer or a DAMF-to-ADM converter. I did not verify whether Cavern writes ADM. The 2+5+0 layout is the closest EAR has to 5.1.2, but EAR's handling of Dolby-style Atmos ADM content is untested by me. [I] |
| **SPARTA / SAF (McCormack), IEM suite, Ambisonic decoders** | **not feasible for Atmos** | SPARTA/SAF are VST and C libraries for spatial rendering; I found nothing that decodes Atmos into them. [I] (search results only; I did not read SAF docs) | Could host a custom VBAP renderer but add nothing Omniphony lacks. |
| **Steam Audio / game-engine spatializers** | **not feasible** | No Atmos stream decoder. [I] | |
| **SoundScape Renderer, JACK-based DBAP/VBAP tools** | **unverified** | Appeared in search results only. | Same limitation: renderer without decoder. |
| **libmpegh / MPEG-H players** | **not feasible** | MPEG-H is a different codec; it cannot decode Dolby streams. [I] | |

### 2.3 Players and ecosystems

| Path | Status | Evidence | Notes |
|---|---|---|---|
| Kodi (Linux, Windows, CoreELEC, Zidoo-style boxes) | **not feasible (passthrough only)** | Kodi's audio guide discusses HDMI passthrough to an AVR that decodes; on Windows WASAPI is needed for TrueHD/DTS-HD passthrough; it does not mention Atmos rendering. [V] (kodi.wiki Audio_Configuration_Guide) A poster on Linux: bitstreaming TrueHD Atmos works and "Linux doesn't decode Atmos or DTS:X itself, so the receiver has to handle it". [C] (lemmy.4d2.org post 3731649) | Kodi without passthrough falls back to core or a 7.1 PCM downmix, which discards objects. [I] |
| Plex and Jellyfin | **not feasible** | A Jellyfin poster: Atmos TrueHD is transcoded to "EAC3 7.1 from Plex or AAC in the case of Jellyfin", Atmos not preserved. [C] (forum.jellyfin.org tid=3368) | They only help if a downstream device decodes DD+ JOC. |
| Apple TV 4K | **not feasible for PCM objects** | Plex forum: Apple TV does not do HDMI passthrough of TrueHD in third-party apps and outputs "LPCM from a decoded Dolby core audio input, other metadata dropped". [C] (forums.plex.tv t/decoding-with-apple-tv/888895) | I did not verify what Apple TV sends for streamed DD+ JOC Atmos in 2026. Unverified. |
| macOS native Atmos | **partially** | Audiophilestyle thread: current macOS decodes DD+ Atmos at system level; users report 7.1.4 to a Merging device via aggregate devices for Music and TV apps; "no renderer on either platform decodes streaming Atmos ... to PCM for a USB DAC" and the thread is undated (~2018 article). [C] (audiophilestyle.com topic 65488 page 4) | Note a Mac does not read your MKV TrueHD files in these apps. Useful only for Apple Music Atmos and purchased titles. Unverified for 5.1.2 USB. |
| Nvidia Shield, Fire Stick, Fire Cube | **not feasible** | These pass Atmos bitstream over HDMI. [I] | The PC cannot get streaming Atmos from them without an HDMI capture path that is both HDCP-blocked and PCM-only. [I] |
| HDMI audio extractors | **not feasible** | KanexPro HAECOAX3 ($125.95 new) passes Atmos through on HDMI; its optical output carries LPCM 2/5.1 and DD/DTS only; analog is stereo. [V] (avlgear.com) | Extractors do not decode Atmos. They only split. |

### 2.4 Linux plumbing (Wine, VMs, bitstream)

| Path | Status | Evidence |
|---|---|---|
| Dolby Access under Wine or Proton | **not feasible / unverified** | No evidence found of it running. Even where it runs on Windows it needs an HDMI sink reporting Atmos (see 2.1). [I] |
| Windows VM with GPU or USB passthrough | **not feasible for new capability** | Same Windows limitation. [I] |
| PipeWire MAT/TrueHD passthrough to HDMI | **unverified** | Forum claims (partly AI-labelled) that Linux bitstreaming works. [C] I did not test PipeWire 1.0.5 itself. A cheap extractor then has nothing to decode with (see above). |

### 2.5 Hardware that decodes Atmos to analog (comparison only)

| Unit | Status | Price found | Notes |
|---|---|---|---|
| Denon AVR-X1800H | **not suitable** | Rs 75,000 (sale price, list Rs 105,900) at avstore.in [V] | An AVR. The listing shows speaker terminals, two sub pre-outs and a stereo pre-out, not 5.1.2 line-level pre-outs, so it cannot feed the Z906 analog inputs without reworking. [V/I] |
| Marantz AV7706 pre-pro | works today | EUR 2,535.61 (hifihut.com, "with lead time"); 11.2-channel RCA and XLR pre-outs, Dolby Atmos [V]. Dubai used listings appeared but I did not read prices. | The cheapest current "real processor" I could verify. India price: **not found**. |
| Monolith HTP-1 | works today | $3,429.37 used, sold out (tmraudio.com) [V] | Not a good value signal. New price not re-verified. |
| miniDSP Flex HTx | **not feasible** | $949; "does not support bitstream (e.g. Dolby/DTS) decoding", LPCM only [V] (minidsp.com) | No Atmos decode. Useful only as a PCM-input DSP. |
| Trinnov Altitude 16/32, StormAudio | works today | AVForums: Altitude 32 uses an i5-12400, units cost "over £10k"; PCs "under £1k" can do similar work [C] (avforums.com thread 2534199) | Out of scope on cost. |

## 3. Comparison with the current stack

| Criterion | Omniphony + harletty (current) | Dolby Reference Player (macOS) | Cavern/Cavernize | Hardware pre-pro |
|---|---|---|---|---|
| Atmos objects to speakers live | yes | yes (file only) | offline (realtime not shipped per sources) | yes |
| Picture in sync | yes (mpv) | no | no (offline file) | yes, via HDMI source |
| Fidelity vs Dolby | **unmeasured against Dolby**; VBAP vs Dolby's renderer will differ [I] | **reference** | different renderer [V] | reference-grade |
| Cost | free (GPL, Apache plugins) | about $400 plus a Mac [C] | free | EUR 2.5k+ [V] |
| Maintenance risk | one maintainer ("nights-and-weekends project, not a product") [V]; frequent ABI breaks (README compatibility table) [V] | Dolby commercial product, restricted store [C] | single author, long-lived [V] | low |
| Fit for 5.1.2, USB DAC, CamillaDSP, PipeWire | already running | aggregate-device on macOS, not Linux | files only | needs analog multichannel input on Z906 side |

## 4. Recommendation (ranked, for this rig)

1. **Stay on Omniphony and bring it current.** The repo README says the combined line is at v0.7.0 and the player at `mpv-v0.7.0`, ABI 0.12, with harletty split into three plugins (bridge_api 0.6.x). Your docs list mpv-omniphony 0.4.2, liborender ABI 0.6, and a bridge with no version number. Per the harletty README, an old host refuses the new plugins, and a new host reads a combined old bridge for "one release". Test the upgrade in a separate prefix so the working install is untouched.
2. **Keep Cavern/Cavernize as an independent offline cross-check**, because it is the only other object-aware renderer that is verified. Render the same scene both ways and compare level and position at the seat with your existing measurement loop.
3. **If you want ground truth for fidelity, borrow or buy a Mac and Dolby Reference Player for A/B only.** Unverified: price, licence for home use, whether a Windows build exists. I would not buy it until a free trial is confirmed; the DRP page says a free trial exists. [V]
4. **Do not buy a hardware processor** to solve this. The cheapest verified current unit is about EUR 2.5k, and it cannot sit in front of the Z906 without level matching to its analog inputs.
5. **Treat IAMF, EAR, libspatialaudio and SAF as future renderer options, not decoders.** Re-check if harletty or another project adds an Atmos-to-IAMF or Atmos-to-ADM path.

### What I would test first

1. Upgrade in a scratch directory: mpv-omniphony 0.7.0 plus a harletty-bridge release that says "requires Omniphony bridge_api 0.6". Replay one TrueHD Atmos clip and one DD+ JOC clip. Record at the seat. Compare to the current 0.4.2 render with your chirp and band-energy checks.
2. Run the harletty/truehdd CLI on the same clip to DAMF, then open the DAMF with Cavern and render 5.1.2. Compare object positions of one moving sound (helicopter-type scene) between the two renderers.
3. DTS:X: play one DTS-HD MA with DTS:X sample through `harletty_dts_bridge` and listen to whether the heights are only a fixed 7.1.4 fold, as the bridge docs say.

## 5. DTS:X, briefly

| Path | Status | Evidence |
|---|---|---|
| Windows DTS:X for Home Theater | **not feasible** (HDMI) | Microsoft lists DTS:X for Home Theater as an HDMI home-theater format with an 8.1.4.4 bed and 32 objects. [V] |
| harletty DTS plugin in Omniphony | **partially** | Decodes DTS, DTS-HD, DTS:X and Auro-3D. The first attempt faked objects and was **rolled back**; the current result is "twelve labeled fixed channels" (reconstructed 7.1.4), with a re-landing step still listed as "Phase 5". [V] (Omniphony docs/channel-object-contract.md; harletty-bridge docs/dtsx-objects-campaign.md) |
| Cavern | **not feasible** | Cavern's supported-codec list does not include DTS:X. [V] |
| FFmpeg | **unverified** | I did not check whether it exposes DTS:X extensions. [I] it drops them. |

## 6. Unverified items and gaps

- Dolby Reference Player: supported OSes, current price, home-use licence, whether the MKV can be fed directly (Dolby store pages were blocked from my session).
- Whether the Dolby Atmos Renderer plays TrueHD or .atmos masters standalone to a 5.1.2 monitor layout, and whether Windows has a standalone mode.
- Any Windows 11 25H2/26H1 change that opens spatial formats to USB endpoints.
- "Dolby Atmos Connect": no match found; only FlexConnect seen in titles.
- Apple TV 4K behaviour for streamed Atmos in 2026.
- PipeWire 1.0.5 TrueHD/MAT passthrough, tested.
- Atmos-to-IAMF converters (harlettizer status) and whether Cavern can write ADM.
- Used pre-pro prices in India (Marantz, Denon, Monolith, Trinnov): not found.
- Whether Omniphony 0.7.0 improves fidelity or latency on your rig: no listening data.
- A listening comparison of Omniphony VBAP against Dolby's renderer: no one has published one that I found; this is the main unknown about fidelity.

## 7. Sources

Local clones read on 2026-10-25 (shallow, anonymous):
- https://github.com/truehdd/truehdd (README, CHANGELOG: 0.6.2 on 2026-09-15)
- https://github.com/mgth/Omniphony (README, docs/multi-bridge.md, docs/channel-object-contract.md, docs/iamf-matroska-plan.md, docs/mpv-omniphony.md)
- https://github.com/harletty/harletty-bridge (README, docs/harletty-cli.md, docs/dtsx-objects-campaign.md)
- https://github.com/VoidXH/Cavern (README, CHANGELOG, Cavern.Format source tree)

Web:
- https://forum.doom9.org/archive/index.php/t-186454.html (truehdd announcement and caveats)
- https://ffmpeg.org/pipermail/ffmpeg-devel/2025-March/341429.html and https://ffmpeg.org/pipermail/ffmpeg-devel/2025-March/341555.html (mlpdec object patch and review)
- https://learn.microsoft.com/en-us/answers/a/12807694 and https://learn.microsoft.com/en-in/answers/questions/5909641/why-does-not-appear-the-dolby-atmos-for-home-theat (Windows Atmos for Home Theater conditions)
- https://learn.microsoft.com/ar-sa/Windows/win32/coreaudio/spatial-sound (Windows spatial sound formats and limits)
- https://professional.dolby.com/product/media-processing-and-delivery/drp---dolby-reference-player (Dolby Reference Player)
- https://immersiveaudioalbum.com/?p=18267 (DRP macOS multichannel setup, $400 claim)
- https://www.avnirvana.com/threads/atmos-setup-issues.10312/ (DRP into Okto dac8pro, 5.1.2)
- https://professional.dolby.com/siteassets/content-creation/dolby-atmos/dolby_atmos_renderer_guide.pdf (Renderer drivers)
- https://professional.dolby.com/product/dolby-atmos-content-creation/dolby-atmos-renderer/ (Renderer overview)
- https://www.soundonsound.com/news/dolby-atmos-renderer-application-released and https://www.production-expert.com/production-expert-1/new-dolby-atmos-renderer-application-announced ($299 / $50 upgrade, Windows separate computer)
- https://audiophilestyle.com/forums/topic/65488-article-how-to-decode-and-play-dolby-truehd-atmos-on-windows-and-macos/page/4/ (macOS and Windows, undated)
- https://techenclave.com/t/getting-dolby-atmos-out-of-pc/258255 (2022-2023 discussion: no analog route)
- https://www.avforums.com/threads/atmos-decoding-on-a-pc.2534199/latest (Cavern TrueHD timeline, Trinnov)
- https://jbkempf.com/blog/2025/libspatialaudio-0.4 (libspatialaudio 0.4.0)
- https://aomedia.org/specifications/oar/1.0.0/ and https://audioxpress.com/news/alliance-for-open-media-publishes-open-audio-renderer-oar-v1-advancing-open-spatial-audio (OAR v1)
- https://opensource.googleblog.com/2025/06/introducing-open-source-daw-plugin-for-eclipsa-audio.html (Eclipsa DAW plugin)
- https://pypi.org/project/ear/ and https://tech.ebu.ch/publications/software/ear-production-suite (EAR)
- https://kodi.wiki/view/Audio_Configuration_Guide (Kodi passthrough)
- https://forum.jellyfin.org/showthread.php?tid=3368 (Jellyfin transcode)
- https://forums.plex.tv/t/decoding-with-apple-tv/888895 (Apple TV LPCM)
- https://lemmy.4d2.org/post/3731649 (Linux bitstream claims)
- https://avlgear.com/collections/signal-processors/products/kanexpro-haecoax3-18gbps-4k-hdmi-audio-extractor-with-dolby-atmos (extractor, $125.95)
- https://www.minidsp.com/products/ht-series/flex-htx (no Dolby/DTS decode, $949)
- https://hifihut.com/products/marantz-av7706-11-2-channel-av-processor-pre-amplifier (EUR 2,535.61)
- https://tmraudio.com/components/home-theater/monoprice-monolith-htp-1-16-channel-home-theater-processor-htp1-remote ($3,429.37 used, sold out)
- https://avstore.in/products/denon-avr-x1800h (Rs 75,000)
- https://www.lg.com/us/press-release/lg-enables-dolby-atmos-flexconnect-on-select-2025-lg-oled-tvs-through-software-update (FlexConnect, titles only; not read in full)
