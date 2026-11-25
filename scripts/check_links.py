# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Check every relative link in the tracked Markdown files (M6, master prompt 11.6).

For each Markdown file tracked by git (``git ls-files '*.md'``), every inline
link or image ``[text](target)`` and every reference definition ``[id]: target``
whose target is not an external URL (``http:``, ``https:``, ``mailto:``, ``doi:``)
must resolve:

- a path resolves relative to the file's folder to an existing file or folder;
- an anchor (``#section`` alone or ``file.md#section``) must match a heading of
  the target Markdown file, slugged as GitHub does (lower case, punctuation
  removed except ``-`` and ``_``, spaces to ``-``), or an explicit ``{#id}``.

Fenced code blocks and inline code spans are ignored. The output lists every
broken link with file and line, then ``LINK-CHECK PASS`` or ``LINK-CHECK FAIL``.
Exit status 0 on pass, 1 on failure.

Usage: ``.venv/bin/python scripts/check_links.py``
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ("http://", "https://", "mailto:", "doi:", "ftp://")
INLINE = re.compile(r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFDEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
EXPLICIT_ID = re.compile(r"\{#([A-Za-z0-9_\-:.]+)[^}]*\}\s*$")


def tracked_markdown(root: Path = ROOT) -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=root, check=True, capture_output=True, text=True).stdout
    return [root / line for line in out.splitlines() if line and "node_modules/" not in line]


def _strip_code(lines: list[str]) -> list[str]:
    """Blank fenced code blocks and inline code spans, keeping line numbers."""
    clean, fence = [], None
    for line in lines:
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            clean.append("")
            continue
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            clean.append("")
            continue
        if line.startswith("    ") and not stripped.startswith(("-", "*", "+")) and not re.match(r"\d+[.)]", stripped):
            clean.append("")  # indented code block line
            continue
        clean.append(re.sub(r"`+[^`]*`+", "", line))
    return clean


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_~]|\[|\]|\([^)]*\)", lambda m: "" if m.group(0)[0] != "(" else m.group(0), text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    found: set[str] = set()
    seen: dict[str, int] = {}
    for line in _strip_code(md.read_text(encoding="utf-8").splitlines()):
        m = HEADING.match(line)
        if not m:
            continue
        title = m.group(2)
        explicit = EXPLICIT_ID.search(title)
        if explicit:
            found.add(explicit.group(1))
            title = title[: explicit.start()].strip()
        base = slug(title)
        n = seen.get(base, 0)
        found.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    return found


def links(md: Path) -> list[tuple[int, str]]:
    out = []
    for i, line in enumerate(_strip_code(md.read_text(encoding="utf-8").splitlines()), start=1):
        for m in INLINE.finditer(line):
            out.append((i, m.group(1)))
        m = REFDEF.match(line)
        if m:
            out.append((i, m.group(1)))
    return out


def check(root: Path = ROOT) -> tuple[int, list[str]]:
    """Return (number of relative links checked, list of problems)."""
    problems: list[str] = []
    checked = 0
    cache: dict[Path, set[str]] = {}
    for md in tracked_markdown(root):
        for line, target in links(md):
            if target.startswith(EXTERNAL):
                continue
            checked += 1
            path_part, _, anchor = target.partition("#")
            dest = md if not path_part else (md.parent / unquote(path_part)).resolve()
            rel = md.relative_to(root)
            if not dest.exists():
                problems.append(f"{rel}:{line}: missing target {target}")
                continue
            if anchor and dest.suffix == ".md":
                if dest not in cache:
                    cache[dest] = anchors(dest)
                if unquote(anchor).lower() not in cache[dest]:
                    problems.append(f"{rel}:{line}: missing anchor #{anchor} in {dest.relative_to(root)}")
    return checked, problems


def main() -> int:
    files = tracked_markdown()
    checked, problems = check()
    for p in problems:
        print(p)
    print(f"{len(files)} Markdown files, {checked} relative links checked, {len(problems)} broken")
    print("LINK-CHECK PASS" if not problems else "LINK-CHECK FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
