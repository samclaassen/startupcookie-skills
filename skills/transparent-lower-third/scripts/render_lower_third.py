#!/usr/bin/env python3
"""render_lower_third.py - animated name-tag lower third with real transparency.

Outputs (in --out):
  <slug>-<fps>fps.mov          ProRes 4444 with alpha (yuva444p12le). Main deliverable.
  <slug>-<fps>fps.webm         VP9 with alpha (fallback for editors without ProRes).
  <slug>-preview.mp4           H.264 over a checkerboard. PREVIEW ONLY: never put it on a timeline.
  <slug>-still.png             Transparent PNG of the hold frame.
  <slug>-png/frame_0001.png... (only with --png-sequence) last-resort fallback.

Why it renders this way (each fixes a real choppiness bug):
  * The whole tag is drawn at --ss x resolution and every frame is downsampled
    with the same box filter, so text sharpness is identical on every frame
    (sub-pixel motion at 1x makes glyphs shimmer).
  * Motion is applied in the supersampled space (1/ss px steps), never whole pixels.
  * Opacity fades are applied LAST, in floating point, after downsampling,
    and frames are piped to ffmpeg as 16-bit RGBA, so there's no 8-bit rounding noise.
  * One frame rate per delivery: match the editor's timeline (--fps).

Usage:
  python3 render_lower_third.py --name "Dana Lee" --role "Founder, Example Co" \
      --name-font fonts/SpaceGrotesk-SemiBold.ttf --role-font fonts/Inter-Regular.ttf \
      --label "CUSTOMER STORY" --label-font fonts/SpaceMono-Regular.ttf \
      --accent "#3d85f9" --theme light --fps 30 --out out/

  Lock geometry across a set:  --card-width 489   (use the width needed by the longest name)
Requires: Python 3, Pillow, numpy, ffmpeg (with prores_ks and libvpx-vp9).
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEFAULT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease_out_cubic(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in_out_sine(t):
    t = min(max(t, 0.0), 1.0)
    return -(math.cos(math.pi * t) - 1) / 2


def font(path, size):
    f = ImageFont.truetype(path, size)
    return f


def text_layer(size, xy, text, fnt, rgb):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).text(xy, text, font=fnt, fill=rgb + (255,))
    return im


def to_premul(im):
    a = np.asarray(im, dtype=np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a


def over(dst, src, dx=0, dy=0, opacity=1.0):
    """Alpha-composite premultiplied src onto dst with an integer offset (in ss pixels)."""
    if opacity <= 0:
        return
    H, W = dst.shape[:2]
    h, w = src.shape[:2]
    x0, y0 = max(dx, 0), max(dy, 0)
    x1, y1 = min(dx + w, W), min(dy + h, H)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - dy:y1 - dy, x0 - dx:x1 - dx] * opacity
    d = dst[y0:y1, x0:x1]
    d *= (1.0 - s[..., 3:4])
    d += s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--name-font", default=DEFAULT_BOLD)
    ap.add_argument("--role-font", default=DEFAULT_FONT)
    ap.add_argument("--label-font", default=DEFAULT_FONT)
    ap.add_argument("--theme", choices=["light", "dark"], default="light")
    ap.add_argument("--ink", default="#0f0f0f")
    ap.add_argument("--surface", default="#fcfdfe")
    ap.add_argument("--muted", default="#525252")
    ap.add_argument("--border", default="#d9d9d9")
    ap.add_argument("--accent", default="#3d85f9")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--duration", type=float, default=5.0)
    ap.add_argument("--margin", type=int, default=72, help="distance from left and bottom edges (at 1080p)")
    ap.add_argument("--card-width", type=int, default=0, help="lock card width in px (0 = fit text)")
    ap.add_argument("--radius", type=int, default=12)
    ap.add_argument("--ss", type=int, default=8, help="supersampling factor (8 recommended, 4 for quick drafts)")
    ap.add_argument("--png-sequence", action="store_true")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found")

    ink, surface, muted, border, accent = map(hex_rgb, (args.ink, args.surface, args.muted, args.border, args.accent))
    if args.theme == "dark":
        ink, surface, muted, border = (245, 246, 248), (18, 18, 20), (170, 170, 176), (60, 60, 66)

    k = args.height / 1080.0  # scale all metrics with output height
    S = args.ss
    px = lambda v: int(round(v * k * S))  # 1080p px -> supersampled px

    name_f = font(args.name_font, px(40))
    role_f = font(args.role_font, px(22))
    label_f = font(args.label_font, px(13)) if args.label else None

    pad_x, pad_top, pad_bot, bar_w = px(32), px(24), px(26), px(4)
    gap_label, gap_name = px(8), px(6)

    def tsize(f, t):
        b = f.getbbox(t)
        return b[2] - b[0], b[3] - b[1], b

    lw, lh, lb = tsize(label_f, args.label) if label_f else (0, 0, (0, 0, 0, 0))
    nw, nh, nb = tsize(name_f, args.name)
    rw, rh, rb = tsize(role_f, args.role)

    content_w = max(lw, nw, rw)
    card_w = px(args.card_width) if args.card_width else content_w + 2 * pad_x + bar_w
    if card_w < content_w + 2 * pad_x + bar_w:
        print(f"warning: --card-width {args.card_width} is narrower than the text; text will be clipped",
              file=sys.stderr)
    card_h = pad_top + (lh + gap_label if label_f else 0) + nh + gap_name + rh + pad_bot

    shadow_pad = px(30)
    RW, RH = card_w + 2 * shadow_pad, card_h + 2 * shadow_pad + px(10)
    cx, cy = shadow_pad, shadow_pad  # card origin inside the region

    # --- static layers at supersampled size -----------------------------------------
    # Shadow: build at 1x and upscale (blurring at 8x is slow and looks the same).
    s1 = Image.new("L", (RW // S + 1, RH // S + 1), 0)
    ImageDraw.Draw(s1).rounded_rectangle(
        [cx // S, cy // S + int(6 * k), (cx + card_w) // S, (cy + card_h) // S + int(6 * k)],
        radius=int(args.radius * k), fill=int(255 * 0.22))
    s1 = s1.filter(ImageFilter.GaussianBlur(10 * k)).resize((RW, RH), Image.BILINEAR)
    shadow = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    shadow.putalpha(s1)

    card = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=px(args.radius),
                        fill=surface + (255,), outline=border + (255,), width=max(1, px(1)))

    bar = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    ImageDraw.Draw(bar).rectangle([cx, cy, cx + bar_w - 1, cy + card_h], fill=accent + (255,))
    # clip the bar to the card's rounded corners
    mask = Image.new("L", (RW, RH), 0)
    ImageDraw.Draw(mask).rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=px(args.radius), fill=255)
    bar.putalpha(Image.fromarray(np.minimum(np.asarray(bar.getchannel("A")), np.asarray(mask))))

    tx = cx + bar_w + pad_x
    y = cy + pad_top
    layers = []
    if label_f:
        layers.append(("label", text_layer((RW, RH), (tx - lb[0], y - lb[1]), args.label, label_f, accent), 0.20))
        y += lh + gap_label
    layers.append(("name", text_layer((RW, RH), (tx - nb[0], y - nb[1]), args.name, name_f, ink), 0.28))
    y += nh + gap_name
    layers.append(("role", text_layer((RW, RH), (tx - rb[0], y - rb[1]), args.role, role_f, muted), 0.36))

    P_shadow, P_card, P_bar = to_premul(shadow), to_premul(card), to_premul(bar)
    P_text = [(n, to_premul(im), t0) for n, im, t0 in layers]
    bar_top, bar_h = cy, card_h

    # --- timeline -------------------------------------------------------------------
    fps, T = args.fps, args.duration
    n_frames = int(round(fps * T))
    ENTER, EXIT = 0.75, 0.65
    slide = 26 * k * S
    drift = 10 * k * S
    rise = 8 * k * S

    ox = int(round(args.margin * k)) - cx // S
    oy = args.height - int(round(args.margin * k)) - (cy + card_h) // S

    os.makedirs(args.out, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", args.name.lower()).strip("-")
    tmp = tempfile.mkdtemp()
    raw_path = os.path.join(tmp, "frames.rgba64")
    rw_, rh_ = RW // S, RH // S
    still = None

    with open(raw_path, "wb") as raw:
        for i in range(n_frames):
            t = i / fps
            e_in = ease_out_cubic(t / ENTER)
            e_out = ease_in_out_sine((t - (T - EXIT)) / EXIT) if t > T - EXIT else 0.0
            dx = int(round(-slide * (1 - e_in) - drift * e_out))
            canvas = np.zeros((RH, RW, 4), np.float32)
            over(canvas, P_shadow, dx, 0)
            over(canvas, P_card, dx, 0)
            # accent bar draws top to bottom between 0.15s and 0.75s
            bp = ease_out_cubic((t - 0.15) / 0.6)
            if bp > 0:
                cut = bar_top + int(bar_h * bp)
                b = P_bar.copy()
                b[cut:] = 0
                over(canvas, b, dx, 0)
            for _, P, t0 in P_text:
                p = ease_out_cubic((t - t0) / 0.45)
                if p > 0:
                    over(canvas, P, dx, int(round(rise * (1 - p))), opacity=p)
            # downsample: identical box filter every frame (premultiplied)
            small = canvas[:rh_ * S, :rw_ * S].reshape(rh_, S, rw_, S, 4).mean(axis=(1, 3))
            # global fade LAST, in float
            fade = min(e_in * 1.0, 1.0) * (1 - e_out)
            small *= fade
            a = small[..., 3:4]
            rgb = np.where(a > 1e-6, small[..., :3] / np.maximum(a, 1e-6), 0)
            out = np.concatenate([rgb, a], axis=2)
            raw.write((np.clip(out, 0, 1) * 65535 + 0.5).astype("<u2").tobytes())
            if abs(t - T / 2) < 0.5 / fps:
                still = (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)
            if i % fps == 0:
                print(f"frame {i + 1}/{n_frames}", flush=True)

    pad = f"pad={args.width}:{args.height}:{ox}:{oy}:color=0x00000000"
    src = ["-f", "rawvideo", "-pix_fmt", "rgba64le", "-s", f"{rw_}x{rh_}", "-r", str(fps), "-i", raw_path]
    base = os.path.join(args.out, f"{slug}-{fps}fps")

    def run(cmd):
        print(" ".join(cmd))
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    run(["ffmpeg", "-y", *src, "-vf", f"{pad},format=yuva444p12le",
         "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p12le",
         "-alpha_bits", "16", "-vendor", "apl0", base + ".mov"])
    run(["ffmpeg", "-y", *src, "-vf", f"{pad},format=yuva420p",
         "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "12",
         "-row-mt", "1", "-auto-alt-ref", "0", base + ".webm"])
    # preview over a checkerboard so transparency is obvious
    run(["ffmpeg", "-y", "-f", "lavfi", "-i",
         f"color=c=0x9a9a9a:s={args.width}x{args.height}:r={fps}:d={T}",
         *src, "-filter_complex",
         f"[0]geq=lum='if(eq(mod(floor(X/40)+floor(Y/40),2),0),170,120)':cb=128:cr=128[bg];"
         f"[1]{pad},format=rgba[fg];[bg][fg]overlay=format=auto,format=yuv420p",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-frames:v", str(n_frames),
         os.path.join(args.out, f"{slug}-preview.mp4")])
    if still is not None:
        full = Image.new("RGBA", (args.width, args.height), (0, 0, 0, 0))
        full.paste(Image.fromarray(still, "RGBA"), (ox, oy))
        full.save(os.path.join(args.out, f"{slug}-still.png"))
    if args.png_sequence:
        seq = os.path.join(args.out, f"{slug}-png")
        os.makedirs(seq, exist_ok=True)
        run(["ffmpeg", "-y", *src, "-vf", pad, "-pix_fmt", "rgba", os.path.join(seq, "frame_%04d.png")])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"done: card {card_w // S}x{card_h // S}px at x={ox + cx // S}, y={oy + cy // S}; {n_frames} frames @ {fps}fps")


if __name__ == "__main__":
    main()
