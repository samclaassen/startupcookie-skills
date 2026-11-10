---
name: transparent-lower-third
description: Make on-brand animated name tags (lower thirds) for testimonial and interview videos, delivered as transparent ProRes 4444 .mov files that drop straight onto a CapCut, Premiere, Final Cut or DaVinci timeline. Pulls brand fonts and colours from the live website, renders smooth sub-pixel motion, locks geometry across a set, and verifies every file frame by frame. Use for "make a name tag for this video", "lower third", "speaker title overlay".
license: MIT
metadata:
  author: StartupCookie
  homepage: https://startupcookie.com
---

# Transparent Lower Third

> Made by [StartupCookie](https://startupcookie.com), a San Francisco marketing team for B2B startups.

Delivers a name tag that looks designed, animates smoothly, and stays identical across a series of videos except for the name and role.

## Inputs
- Name and role/title for each person. Confirm punctuation style once for the set ("Founder, Example Co" vs "Founder of Example Co").
- The brand: a website URL (preferred) or a brand guide.
- A screenshot or frame from the video (to check placement and resolution).
- The editor and the timeline frame rate (CapCut, Premiere, etc.; 24/25/30/60 fps).
- If adding to an existing set: the reference `.mov` that new tags must match.

## Step 1. Pull the brand from the live site, then check it against what renders
- Read the site's CSS for font families, weights and colour tokens (ink, surface, muted grey, border, accent).
- **Check against screenshots of the rendered pages.** Fonts declared in CSS aren't always the ones visibly used (a serif may be loaded but only used on one page). Use what the pages actually show.
- Never introduce colours that aren't on the site. Avoid AI tells: glows, glassy pills, gradients the brand doesn't use.
- Download the font files (Google Fonts or the site's own files) for the renderer.

Record the tokens in the delivery so the next tag uses the same values.

## Step 2. Confirm the spec before rendering
Default spec (proven in production at 1920×1080):
- Lower-left card, 72px from the left and bottom edges.
- 12px corner radius, hairline border, soft shadow, 4px accent bar on the left.
- Optional small uppercase label in the accent colour (a mono font works well), name in the display font (semibold), role in the body font, muted colour.
- 5 seconds total: about 0.75s entrance (slide in about 26px from the left plus fade, accent bar draws top to bottom, label, name and role rise in with a slight stagger), hold, then about 0.65s exit fade with a small drift.
- No bounces, no wipes, no glow.

Ask about: light or dark card, label or no label, resolution (if the source is 4K, render at 3840×2160), and frame rate.

## Step 3. Render
Run with Type's managed execution tool (needs Python, Pillow, numpy and ffmpeg):

```bash
python3 scripts/render_lower_third.py \
  --name "Dana Lee" --role "Founder, Example Co" --label "CUSTOMER STORY" \
  --name-font fonts/SpaceGrotesk-SemiBold.ttf --role-font fonts/Inter-Regular.ttf \
  --label-font fonts/SpaceMono-Regular.ttf \
  --ink "#0f0f0f" --surface "#fcfdfe" --muted "#525252" --border "#d9d9d9" --accent "#3d85f9" \
  --theme light --fps 30 --out out/
```

Outputs: `<name>-<fps>fps.mov` (ProRes 4444 with alpha, the deliverable), `.webm` (VP9 with alpha, fallback), `-preview.mp4` (checkerboard background, preview only), and `-still.png`. Add `--png-sequence` for a last-resort PNG frame sequence. Use `--ss 4` for quick drafts and the default `--ss 8` for final renders.

### Why it renders this way
Each of these fixed a real "it's choppy" complaint:
- **Whole-pixel motion stutters.** Motion happens in supersampled space (1/8 px steps).
- **Sub-pixel text shimmers** when sharpness changes from frame to frame. The whole tag is drawn at 8× and every frame is downsampled with the same filter, so sharpness is identical on every frame.
- **8-bit fades add rounding noise.** The fade is applied last, in floating point, and frames go to ffmpeg as 16-bit RGBA.
- **A 60fps file on a 30fps timeline drops frames unevenly.** Deliver one frame rate: the timeline's.
- **An accidental 25fps preview looks broken.** Previews use the same fps as the deliverable.

## Step 4. Lock geometry across a set
When tags must match ("they have to be the same, just a different name and role"):
- Render every tag with the same `--card-width`, set to the width the longest name needs, so all cards are identical in size.
- Same fonts, sizes, timing, fps and position for every tag in the set.
- Then verify against the reference (Step 5).

## Step 5. Verify before delivering
```bash
python3 scripts/verify_overlay.py out/dana-lee-30fps.mov
python3 scripts/verify_overlay.py out/new-30fps.mov --reference out/existing-30fps.mov
```
Check:
- ProRes 4444, `yuva444p12le`, the right fps, frame count and duration.
- The hold frame is mostly fully clear (proves the background is transparent).
- The card box is where the spec says (for example x=72 and bottom edge at 1008 on 1080p).
- The alpha curve rises and falls cleanly with no spikes.
- Against a reference: same format, and **zero** card-box mismatches across frames.
- Look at the still at 1:1 for crisp text and no clipping.

## Step 6. Deliver with import instructions
Send the `.mov` (and the WebM fallback), the preview, the tokens used, and these instructions:
- Put the `.mov` on an overlay track **above** the video clip. Blend mode Normal. No background removal or chroma key needed.
- **The `.mp4` preview has a background baked in. Never put it on the timeline.**
- The overlay's frame rate matches the timeline.
- CapCut desktop reads ProRes alpha. Some mobile editors show black instead: use the WebM, then the PNG sequence, then a green-screen render with Chroma Key as the last resort. (HEVC with alpha can only be encoded on a Mac.)
- Editors often stutter when playing ProRes in their viewer even when the file is fine. Judge smoothness from an exported test, not the viewer.

## What not to do
- Don't guess brand values or redraw the layout for each person.
- Don't send multiple frame rates "just in case".
- Don't call a tag "matched" without running the reference comparison.
- Don't add the tool's own watermark or label text.
