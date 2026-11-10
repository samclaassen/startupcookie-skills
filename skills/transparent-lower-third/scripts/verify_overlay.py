#!/usr/bin/env python3
"""verify_overlay.py - QA a transparent overlay video, optionally against a reference.

Usage:
  python3 verify_overlay.py new.mov [--reference old.mov]

Checks:
  * codec/profile/pix_fmt/fps/frame count/duration (ffprobe)
  * alpha is real: share of fully clear pixels on the hold frame, partial alpha on fade frames
  * per-frame opaque bounding box (card geometry) and peak alpha curve
  * smoothness: frame-to-frame change in mean alpha should rise and fall cleanly,
    with no spikes (a spike = a visible stutter)
  * with --reference: same codec/fps/frames, same card box on every frame,
    max difference in the alpha curve
Requires ffmpeg/ffprobe and numpy.
"""
import argparse
import json
import subprocess
import sys

import numpy as np


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                          "-show_entries", "stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,nb_read_frames:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    s["duration"] = float(j["format"]["duration"])
    return s


def alpha_frames(path, w, h):
    cmd = (["ffmpeg", "-v", "error"] + (["-c:v", "libvpx-vp9"] if path.endswith(".webm") else []) +
           ["-i", path, "-vf", "alphaextract", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)


def stats(path):
    p = probe(path)
    w, h = p["width"], p["height"]
    A = alpha_frames(path, w, h)
    mean = A.reshape(len(A), -1).mean(axis=1)
    boxes = []
    for f in A:
        ys, xs = np.where(f >= 250)
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None)
    return p, A, mean, boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--reference")
    args = ap.parse_args()

    p, A, mean, boxes = stats(args.file)
    hold = A[len(A) // 2]
    clear = (hold == 0).mean() * 100
    print(f"codec={p['codec_name']} profile={p.get('profile')} pix_fmt={p['pix_fmt']} "
          f"{p['width']}x{p['height']} fps={p['r_frame_rate']} frames={p['nb_read_frames']} dur={p['duration']:.3f}s")
    print(f"hold frame: {clear:.1f}% fully clear pixels (transparency OK)" if clear > 50
          else f"hold frame: only {clear:.1f}% clear - is the background baked in?")
    partial = [i for i, f in enumerate(A) if ((f > 0) & (f < 250)).mean() > 0.01]
    print(f"frames with partial alpha (fades): {len(partial)}")
    hb = boxes[len(A) // 2]
    if hb:
        print(f"card box on hold frame: x {hb[0]}-{hb[2]}, y {hb[1]}-{hb[3]} ({hb[2]-hb[0]+1}x{hb[3]-hb[1]+1})")
    d = np.abs(np.diff(mean))
    med = np.median(d[d > 0]) if (d > 0).any() else 0
    spikes = [i + 1 for i in range(1, len(d) - 1) if d[i] > 0.05 and d[i] > 2.5 * max(d[i - 1], d[i + 1], 1e-6)]
    print("alpha delta curve: " + " ".join(f"{x:.2f}" for x in d if x > 0.005))
    print("smoothness: OK (no isolated spikes)" if not spikes else f"smoothness: spikes at frames {spikes}")

    if args.reference:
        rp, RA, rmean, rboxes = stats(args.reference)
        same = all(p[k] == rp[k] for k in ("codec_name", "pix_fmt", "r_frame_rate", "nb_read_frames", "width", "height"))
        print(f"\nvs reference: format {'identical' if same else 'DIFFERENT'}")
        n = min(len(boxes), len(rboxes))
        mism = [i for i in range(n) if boxes[i] != rboxes[i]]
        print(f"card box mismatches: {len(mism)} of {n} frames" + (f" (first: {mism[:5]})" if mism else ""))
        print(f"max alpha-curve difference: {np.abs(mean[:n] - rmean[:n]).max():.3f}")


if __name__ == "__main__":
    main()
