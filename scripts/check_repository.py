#!/usr/bin/env python3
"""Check internal Markdown links and required attribution using only stdlib."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")


def check_links() -> list[str]:
    errors: list[str] = []
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        text = source.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            clean = unquote(target.split("#", 1)[0].strip("<>"))
            if not clean or clean.startswith(SKIP_PREFIXES):
                continue
            destination = (source.parent / clean).resolve()
            try:
                destination.relative_to(ROOT)
            except ValueError:
                errors.append(f"{source.relative_to(ROOT)}: link escapes repository: {target}")
                continue
            if not destination.exists():
                errors.append(f"{source.relative_to(ROOT)}: missing link target: {target}")
    return errors


def check_attribution() -> list[str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required = (
        "RonitSachdev",
        "https://github.com/RonitSachdev/aws-saa-c03-guides",
        "CC BY 4.0",
    )
    return [f"README.md: missing required attribution text: {item}" for item in required if item not in readme]


def main() -> int:
    errors = check_links() + check_attribution()
    if errors:
        print("Repository checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository checks passed: internal links resolve and attribution is present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

