#!/usr/bin/env python3
# build_site.py - assembles the GitHub Pages site into _site/.
#   python3 site/build_site.py
# examples.json records the real ./errorbuddy output for every example, so the
# playground works even without the WebAssembly build (ci/github-pages-wasm.yml).
import glob, json, os, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, "architecture"))
subprocess.run(["make", "-s"], cwd=ROOT, check=True)

for f in glob.glob(os.path.join(ROOT, "site", "*.html")):
    shutil.copy(f, OUT)
for f in glob.glob(os.path.join(ROOT, "architecture", "*.svg")):
    shutil.copy(f, os.path.join(OUT, "architecture"))
for f in ("ErrorBuddy_Complete.pdf", "ErrorBuddy_Complete.pptx", "ErrorBuddy_Final_Report.pdf"):
    shutil.copy(os.path.join(ROOT, f), OUT)

examples = []
for name in sorted(os.listdir(os.path.join(ROOT, "examples"))):
    if not name.endswith(".txt") or name == "empty.txt":
        continue
    path = os.path.join("examples", name)
    r = subprocess.run(["./errorbuddy", path, "--tokens"], cwd=ROOT, capture_output=True, text=True)
    examples.append({"name": name[:-4], "source": open(os.path.join(ROOT, path)).read(),
                     "output": r.stdout.replace(path, "program.txt"), "exit": r.returncode})
json.dump(examples, open(os.path.join(OUT, "examples.json"), "w"))
open(os.path.join(OUT, ".nojekyll"), "w").close()
print("wrote", OUT)
