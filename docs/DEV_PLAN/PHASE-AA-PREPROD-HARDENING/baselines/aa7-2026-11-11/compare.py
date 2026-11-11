#!/usr/bin/env python3
"""AA7 before/after comparison (committed after the cold review, F7, so the numbers can be reproduced).
Usage: compare.py <baseline-dir>   (needs Pillow; reads before/ and after/)"""
import glob, json, os, sys
from PIL import Image, ImageChops
d = sys.argv[1]
a, b = (json.load(open(f"{d}/{k}/snapshot.json")) for k in ("before", "after"))
print("docs heading ids identical:", a["docs"] == b["docs"], f"({sum(len(v) for v in a['docs'].values())} ids)")
for path in a["text"]:
    same = a["text"][path] == b["text"].get(path)
    print(f"text {'identical' if same else 'DIFFERS'}: {path} ({len(a['text'][path])} chars, header + main)")
for before in sorted(glob.glob(f"{d}/before/*.png")):
    name = os.path.basename(before); x = Image.open(before).convert("RGB"); y = Image.open(f"{d}/after/{name}").convert("RGB")
    if x.size != y.size: print(f"{name}: size differs {x.size} vs {y.size}"); continue
    diff = ImageChops.difference(x, y).convert("L").point(lambda v: 255 if v > 0 else 0)
    n = diff.histogram()[255]
    print(f"{name:18} {n / (x.size[0] * x.size[1]) * 100:6.2f}% pixels differ, box {diff.getbbox()}")
