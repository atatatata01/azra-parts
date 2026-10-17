#!/usr/bin/env python3
"""AZRA community parts — layout check + index.json generator.

    python3 scripts/build_index.py              rebuild index.json from parts/*/*/part.json
    python3 scripts/build_index.py --check      exit 1 if index.json is stale or the layout is wrong
    python3 scripts/build_index.py --layout     layout checks only (what PR CI runs)

Layout rule: every package lives in parts/<category>/<slug>/ and holds EXACTLY part.flb,
thumb.png and part.json, where part.json's "category" and "slug" equal the folder names and its
"license" is CC0-1.0. Content validation (decode, hashes, stats, thumbnail) is azra-part-check's
job — this script never trusts part.json beyond the fields it copies into the index.

Standard library only; deterministic output (sorted, no timestamps) so index.json only changes
when the parts change.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "parts")
INDEX = os.path.join(ROOT, "index.json")
FILES = {"part.flb", "thumb.png", "part.json"}
INDEX_SCHEMA = 1
# Fields copied from part.json into the index (the app shows these without downloading the part).
INDEX_FIELDS = [
    "name", "slug", "category", "tags", "author", "license", "azra_format_version",
    "flb_sha256", "flb_bytes", "thumb_sha256", "thumb_bytes", "stats",
]
MAX_MANIFEST_BYTES = 16 * 1024


def packages():
    """Yield (category, slug, abs_dir) for every package dir, sorted."""
    if not os.path.isdir(PARTS):
        return
    for cat in sorted(os.listdir(PARTS)):
        cdir = os.path.join(PARTS, cat)
        if cat.startswith(".") or not os.path.isdir(cdir):
            continue
        for slug in sorted(os.listdir(cdir)):
            yield cat, slug, os.path.join(cdir, slug)


def check_layout():
    errors = []
    entries = []
    for name in sorted(os.listdir(PARTS)) if os.path.isdir(PARTS) else []:
        p = os.path.join(PARTS, name)
        if name != ".gitkeep" and not os.path.isdir(p):
            errors.append(f"parts/{name}: stray file (only category folders belong here)")
    for cat, slug, d in packages():
        rel = f"parts/{cat}/{slug}"
        if not os.path.isdir(d):
            errors.append(f"{rel}: stray file (only package folders belong here)")
            continue
        present = set(os.listdir(d))
        if present != FILES:
            missing = sorted(FILES - present)
            extra = sorted(present - FILES)
            errors.append(f"{rel}: must hold exactly {sorted(FILES)} (missing {missing}, extra {extra})")
            continue
        mpath = os.path.join(d, "part.json")
        if os.path.getsize(mpath) > MAX_MANIFEST_BYTES:
            errors.append(f"{rel}/part.json: larger than {MAX_MANIFEST_BYTES} bytes")
            continue
        try:
            with open(mpath, "r", encoding="utf-8") as f:
                m = json.load(f)
        except (OSError, ValueError) as e:
            errors.append(f"{rel}/part.json: unreadable ({e})")
            continue
        if not isinstance(m, dict):
            errors.append(f"{rel}/part.json: not an object")
            continue
        if m.get("category") != cat or m.get("slug") != slug:
            errors.append(f"{rel}: part.json category/slug ({m.get('category')}/{m.get('slug')}) != folder")
            continue
        if m.get("license") != "CC0-1.0":
            errors.append(f"{rel}: license must be CC0-1.0")
            continue
        e = {k: m[k] for k in INDEX_FIELDS if k in m}
        e["path"] = rel
        entries.append(e)
    return errors, entries


def render(entries):
    return json.dumps({"schema": INDEX_SCHEMA, "parts": entries}, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--write"
    errors, entries = check_layout()
    for e in errors:
        print(f"LAYOUT: {e}", file=sys.stderr)
    if errors:
        return 1
    if mode == "--layout":
        print(f"layout OK ({len(entries)} parts)")
        return 0
    text = render(entries)
    if mode == "--check":
        try:
            with open(INDEX, "r", encoding="utf-8") as f:
                current = f.read()
        except OSError:
            current = ""
        if current != text:
            print("index.json is stale: run python3 scripts/build_index.py", file=sys.stderr)
            return 1
        print(f"index.json up to date ({len(entries)} parts)")
        return 0
    if mode != "--write":
        print(__doc__, file=sys.stderr)
        return 2
    with open(INDEX, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"wrote index.json ({len(entries)} parts)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
