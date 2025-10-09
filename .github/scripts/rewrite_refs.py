#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewrite relative references in HTML/CSS/JS/SourceMap files inside a built directory.

- Reads a mapping file (original_rel -> hashed_rel), both paths relative to the site root (i.e., the dist/ root), without leading "/".
- For each target file in dist/: replace href/src/url(...) that point to original assets with correct relative path to the hashed asset.
- Handles:
  * relative paths (e.g., "../style.css", "style.css")
  * absolute-root paths (e.g., "/assets/app.js")
  * bare basenames when globally unique (e.g., "style.css" appears only once in mapping)
- Skips external/data URLs.

Usage:
    python rewrite_refs.py --dist dist --mapping dist/.fingerprint_map.txt
"""

import argparse
import os
import pathlib
import re
import sys
from typing import Optional

ATTR_RE = re.compile(
    r'(?P<prefix>\b(?:href|src)\s*=\s*["\'])(?P<url>[^"\'#?\s>]+)(?P<suffix>[^"\']*["\'])',
    re.IGNORECASE,
)
URL_FUNC_RE = re.compile(
    r'(?P<prefix>\burl\(\s*["\']?)(?P<url>[^"\')#?\s]+)(?P<suffix>[^"\')]*["\']?\s*\))',
    re.IGNORECASE,
)

TEXT_EXTS = (".html", ".css", ".js", ".map")


def load_mapping(mapping_file: pathlib.Path):
    mapping = {}
    basename_count = {}
    with mapping_file.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                original, hashed = line.split(" ", 1)
            except ValueError:
                continue
            mapping[original] = hashed
            bn = os.path.basename(original)
            basename_count[bn] = basename_count.get(bn, 0) + 1
    return mapping, basename_count


def norm_from_view(dist_root: pathlib.Path, file_dir: pathlib.Path, url: str) -> Optional[str]:
    """
    Normalize a URL referenced from file_dir to path relative to dist_root (no leading '/').
    Returns None if the URL is external, data:, or cannot be resolved within dist_root.
    """
    if url.startswith(("http://", "https://", "data:")):
        return None
    if url.startswith("/"):
        rel_to_root = url[1:]
    else:
        abs_target = (file_dir / url).resolve()
        try:
            rel_to_root = str(abs_target.relative_to(dist_root))
        except ValueError:
            return None
    return os.path.normpath(rel_to_root)


def rel_from_view(dist_root: pathlib.Path, file_dir: pathlib.Path, rel_to_root: str) -> str:
    target_path = (dist_root / rel_to_root).resolve()
    return os.path.relpath(target_path, file_dir)


def rewrite_text(dist_root: pathlib.Path, mapping: dict, basename_count: dict, p: pathlib.Path, text: str) -> str:
    file_dir = p.parent

    def _do_sub(m: re.Match) -> str:
        url = m.group("url")
        norm = norm_from_view(dist_root, file_dir, url)
        replacement = None

        if norm and norm in mapping:
            replacement = rel_from_view(dist_root, file_dir, mapping[norm])
        else:
            # basename-only & globally unique
            bn = os.path.basename(url)
            if "/" not in url and basename_count.get(bn) == 1:
                original = next(k for k in mapping.keys() if os.path.basename(k) == bn)
                replacement = rel_from_view(dist_root, file_dir, mapping[original])

        if replacement:
            return f"{m.group('prefix')}{replacement}{m.group('suffix')}"
        return m.group(0)

    text2 = ATTR_RE.sub(_do_sub, text)
    text2 = URL_FUNC_RE.sub(_do_sub, text2)
    return text2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", required=True, help="Path to built dir (e.g., dist)")
    ap.add_argument("--mapping", required=True, help="Path to mapping file inside dist")
    args = ap.parse_args()

    dist_root = pathlib.Path(args.dist).resolve()
    mapping_file = pathlib.Path(args.mapping).resolve()

    if not dist_root.exists():
        print(f"[rewrite_refs] dist not found: {dist_root}", file=sys.stderr)
        sys.exit(1)
    if not mapping_file.exists():
        print(f"[rewrite_refs] mapping file not found: {mapping_file}", file=sys.stderr)
        sys.exit(1)

    mapping, basename_count = load_mapping(mapping_file)

    targets = []
    for ext in TEXT_EXTS:
        targets += list(dist_root.rglob(f"*{ext}"))

    changed = 0
    for p in targets:
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[rewrite_refs] skip unreadable {p}: {e}", file=sys.stderr)
            continue
        new = rewrite_text(dist_root, mapping, basename_count, p, t)
        if new != t:
            p.write_text(new, encoding="utf-8")
            changed += 1

    print(f"[rewrite_refs] processed={len(targets)} changed={changed}")


if __name__ == "__main__":
    main()
