"""Fidelity re-verification for the smy5 lean-head patch (model_performance-smy5).

Two mechanical passes over stock-vs-lean for the two always-on context files:

1. backticked-token pass -- every command/path/identifier/pointer in stock must
   still appear in lean.
2. sentence-coverage pass -- every stock sentence must have >=60% of its content
   words present somewhere in lean. This is the pass that caught the real
   weakening zc6t's token-only checker reported as clean.

Run from the repo root:

    python3 docs/lanes/smy5-patch-wayfinder/fidelity_check.py [BASE_REF]

BASE_REF defaults to the pre-patch base branch. With no argument the script
tries origin/main, then main, then origin/HEAD, and uses the first that
resolves -- so it works both in a full clone and in the `--single-branch`
clone a reviewer gets from `gh pr checkout`, where `origin/main` does NOT
exist as a remote-tracking ref even after `git fetch origin main`.

If no base ref resolves it FAILS LOUD with the exact fetch command to run,
rather than dying in a subprocess traceback.

Expected output: MISSING IN LEAN: NONE, and 0 uncovered sentences, both files.
Exit 0 on clean, 1 on any missing token or uncovered sentence.
"""

import pathlib
import re
import subprocess
import sys

PATHS = ["context/wayfinder-voice.md", "context/propose-and-ack.md"]


def _resolves(ref):
    return subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                          capture_output=True, text=True).returncode == 0


def resolve_base(argv):
    candidates = [argv[1]] if len(argv) > 1 else ["origin/main", "main", "origin/HEAD"]
    for ref in candidates:
        if _resolves(ref):
            return ref
    sys.exit(
        "FATAL: no base ref resolved (tried: %s).\n"
        "This is normal in a --single-branch clone. Fetch the base branch first:\n"
        "    git fetch origin main:refs/remotes/origin/main\n"
        "then re-run, or pass an explicit ref:\n"
        "    python3 %s <BASE_REF>" % (", ".join(candidates), argv[0])
    )


BASE = resolve_base(sys.argv)


def stock(path):
    r = subprocess.run(["git", "show", f"{BASE}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: {path} does not exist at base ref {BASE!r}.\n{r.stderr.strip()}")
    return r.stdout


TOKEN_RE = re.compile(r'`([^`]+)`')
# sentence-level split
def sentences(t):
    t = re.sub(r'\s+',' ',t)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if s.strip()]

STOP = set("""a an the and or of to in on for is are be by it its this that with as at
from not no do does don't you your we our they their if then than so but into
per via any all each""".split())

def content_words(s):
    return {w for w in re.findall(r"[a-z][a-z0-9_\-']+", s.lower()) if w not in STOP and len(w)>2}

exit_code = 0
print(f"base ref: {BASE}")
for path in PATHS:
    s = stock(path)
    lean = pathlib.Path(path).read_text()
    print("="*70)
    print(f"{path}: stock_chars={len(s)}  lean_chars={len(lean)}  delta={len(lean)-len(s)}")
    # 1. backticked tokens (commands, paths, identifiers, pointers)
    st = TOKEN_RE.findall(s)
    lt = set(TOKEN_RE.findall(lean))
    miss_tok = [t for t in dict.fromkeys(st) if t not in lt]
    print(f"  backticked tokens in stock: {len(set(st))}  MISSING IN LEAN: {miss_tok if miss_tok else 'NONE'}")
    # 2. sentence-level coverage: every stock sentence's content words must be >=60% covered somewhere in lean
    lw = content_words(lean)
    weak=[]
    for sent in sentences(s):
        cw = content_words(sent)
        if not cw:
            continue
        cov = len(cw & lw)/len(cw)
        if cov < 0.6:
            weak.append((round(cov,2), sent[:160], sorted(cw-lw)))
    print(f"  stock sentences with <60% content-word coverage in lean: {len(weak)}")
    for c,sent,missing in weak:
        print(f"    cov={c}  {sent}")
        print(f"      unmatched words: {missing}")
    if miss_tok or weak:
        exit_code = 1

sys.exit(exit_code)
