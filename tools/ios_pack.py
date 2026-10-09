#!/usr/bin/env python3
"""Copy the game into the iOS shell's www folder and zip the whole Xcode project as RollModel-iOS.zip (run from the repo root)."""
import os, shutil, zipfile, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
www = os.path.join(root, 'ios', 'RollModel', 'RollModel', 'www')
if os.path.isdir(www): shutil.rmtree(www)
shutil.copytree(os.path.join(root, 'game'), www)
out = os.path.join(root, 'RollModel-iOS.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    base = os.path.join(root, 'ios')
    for d, _, files in os.walk(base):
        for f in files:
            p = os.path.join(d, f); z.write(p, os.path.relpath(p, root))
print(out, os.path.getsize(out) // 1024, 'KB')
