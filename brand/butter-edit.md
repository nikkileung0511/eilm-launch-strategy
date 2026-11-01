# The Butter Edit — house editing style for @heyitsbutterr

Status: **approved v1** (2026-11-01). Visual version: `brand/butter-edit.html`.
Source: three reference reels, measured frame by frame (see `references/README.md`).
Canvas for every number below: 1080 × 1920, 9:16.

## Colour

| Token | Hex | Use |
|---|---|---|
| Butter | `#F2C94C` | Signature. Venue names, reaction pops, title-card cursor bar, end stamp |
| Plum | `#6B3A63` | Item title card box |
| Blush | `#E8669F` | The ★ only |
| Cream | `#FFF4D2` | Dish labels, location tag, title-card text |
| Espresso | `#2B1E18` | Outlines, stamp ink |

Captions and asides are pure white. Grade footage warm and true to the room; don't push saturation.

## Type

Three faces only:
- **Klasyczny (Instagram "Classic")** for every spoken caption and aside. Always.
- **Instrument Serif** for opener titles, item title cards and the location tag.
- **Hanken Grotesk** for dish labels, reaction pops and the stamp's place line.

Klasyczny is not available as a font file. When captions are burned in, use the stand-in
**Inter Tight SemiBold**, tracking −3%, white, 4px black outline (no soft shadow).
On request, also export a caption-free version so captions can be added in Instagram with the real Klasyczny.

### Text styles

| Style | Spec | Position & timing |
|---|---|---|
| Spoken captions | Klasyczny (Inter Tight SemiBold 46px, lh 1.12, −3%), white, 4px black outline | Centred, top of block at y 1270. One spoken phrase per caption, max 2 lines × 30 chars, lowercase as spoken, ≥ 0.6s on screen |
| Asides | Klasyczny (Inter Tight SemiBold 34px), white, thin black outline, lowercase, in (brackets) | Top third, y ≈ 400; two may sit side by side; 4-frame fade |
| Opener title | Kicker: Instrument Serif caps 58px, +4% tracking, cream, ★ in blush. Venue: Instrument Serif Italic 140px, butter, soft glow. Sub-line: Hanken Grotesk Medium 34px, cream 80% | Frame 1 to first cut; 6-frame fade in |
| Item title card | Instrument Serif 64px, cream, hero word italic; plum box, 4px radius, butter cursor bar at left | Types on at 2 frames/char, holds ≥ 1.2s, left third over that item's close-up |
| Dish label | Hanken Grotesk Medium 34px, cream, left-aligned at x 96, one idea per line, max 4 lines | Appears on the cut, no animation |
| Location tag | Instrument Serif Italic 34px, cream 80%, "Venue, Suburb" | Centred at y 1540, on for the whole reel, every reel |
| Reaction pop | Hanken Grotesk ExtraBold 64px caps, butter, 3px espresso stroke, −4° | Beside the face; 120% → 100% in 5 frames, hold 1s; max one per 10s |
| Butter Stamp (end card) | Full-frame butter; five butter pats (filled espresso or outlined) = rating; handle in Instrument Serif Italic 76px; place in Hanken Grotesk SemiBold 32px caps | Last 1.0s, hard cut in, soft "tap" sound |

Spellcheck every venue, suburb and dish name. Deliberate misspellings in reaction pops are fine; accidental ones are not.

### Safe zones
Keep text out of: top 0–250px; bottom 380px; right 160px from y 770 down.

## Cuts & pacing

- Hook: first cut before 2.0s. Frame one is food or a bite, never an empty room or black screen.
- B-roll shots: 1.0–2.5s. Cut on the action (bite, pull-apart, sauce drag, knife).
- Talking shots: up to 8s, with a hard punch-in to 112% at each new sentence (reset every 3–4s).
- Length: 35–50s for a single spot; up to 70s for a multi-item taste test.
- Straight cuts only. No whips, glitches or 3D transitions.
- End on the verdict line or the shopfront sign, then the Butter Stamp.

## Motion (only these five)

1. Punch-in: hard cut 100% → 112% on an emphasis word or new sentence.
2. Slow push: static plate shots drift 100% → 105% over the shot, ease in-out.
3. Speed ramp: 100% → 50% → 100% for cheese pulls, sauce drags, pours (needs 60fps footage).
4. Collage pop: three past photos land 4 frames apart, scale 92% → 100%, ±4° tilt, hold 1.5s ("if you don't know me yet" intros).
5. Type-on: item title cards only, 2 frames/char.

## Music & sound

- Music-led (dining diaries, no voiceover): upbeat track, cuts snapped to detected beats, dish labels instead of captions.
- Voice-led (bite reviews, taste tests): voice is the track; any music bed ~20 dB under the voice.
- The crunch: music drops out, bite sound +3–4 dB, caption `< volume up >`.
- Master: −14 LUFS integrated, −1 dBTP.
- Cleanup: light noise reduction on café voiceovers, high-pass at 80 Hz, no heavy compression.
- The trending track is chosen in the Instagram app at posting; edit to a placeholder at the tempo given.

## Formats

**Dining Diary** (music-led, 30–40s, shots ~1.4s): 0–1.5s room + opener title → one dish per 1–2s with dish labels and slow pushes → action shots → staff, room, shopfront sign → Stamp.

**Bite Review** (voice-led, 40–50s, shots ~1.8s): 0–1s bite + `< volume up >` → context line with title over the hold-up → talking with punch-ins, one reaction pop, asides → B-roll of it being made → verdict line → Stamp.

**Taste Test** (voice-led, 50–70s, shots ~2.3s): "if you don't know me yet" + collage pop → table spread → per item: title card → close-up → bite → verdict → ranking → Stamp.

## Export

- 1080 × 1920, 30fps (60fps footage only for slow motion)
- H.264 High, CRF 18, yuv420p, `+faststart`
- AAC 48 kHz stereo, 256 kbps, −14 LUFS / −1 dBTP
- Also deliver: cover frame (PNG) and captions (SRT)
- File name: `YYYY-MM-DD_venue-suburb_format.mp4`
