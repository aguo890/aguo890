#!/usr/bin/env python3
"""Generate the profile README's SVG assets (dark + light variants) and its stack table.

Usage:
    python3 scripts/build_assets.py --fonts-dir DIR

DIR must contain the OFL-licensed source fonts:
    Inter-Regular.ttf, Inter-SemiBold.ttf, InterDisplay-ExtraBold.ttf
        (Inter 4.1, https://github.com/rsms/inter/releases, extras/ttf/)
    JetBrainsMono-Regular.ttf, JetBrainsMono-Bold.ttf
        (JetBrains Mono 2.304, https://github.com/JetBrains/JetBrainsMono/releases, fonts/ttf/)

The hero photo comes from assets/src/avatar.jpg (downscaled and re-encoded as JPEG at build time).

Requires: fonttools, brotli, Pillow. Each SVG embeds WOFF2 subsets of only the glyphs it uses.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Callable  # noqa: E402

from hmi import cards, chrome, hero, stack  # noqa: E402
from hmi.content import CARDS, CONTACTS, SECTIONS, stack_markdown  # noqa: E402
from hmi.svgdoc import PALETTES, Doc, FontBook, Palette  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
TABLE_START, TABLE_END = "<!-- stack-table:start -->", "<!-- stack-table:end -->"

Builder = Callable[[FontBook, Palette], Doc]


def jobs() -> list[tuple[str, Builder]]:
    out: list[tuple[str, Builder]] = [("hero", hero_doc), ("stack", stack.build)]
    out += [(f"sections/{s[0]}", chrome.section_builder(s)) for s in SECTIONS]
    out += [(f"cards/{c.slug}", cards.card_builder(c)) for c in CARDS]
    out += [(f"contact/{c[0]}", chrome.contact_builder(c)) for c in CONTACTS]
    return out


def hero_doc(book: FontBook, pal: Palette) -> Doc:
    doc = Doc(book, pal, (hero.W, hero.H), (
        "Aaron Guo — Software Automation Controls Engineer",
        "Photo of Aaron Guo with his name, role, and status chips, next to an animated one-line electrical "
        "diagram where feeder 3 trips, is acknowledged, and is restored."))
    hero.build(doc)
    return doc


def write_assets(book: FontBook, only: str | None) -> None:
    for name, builder in jobs():
        if only and only not in name:
            continue
        for pal in PALETTES:
            path = ASSETS / f"{name}-{pal.name}.svg"
            path.parent.mkdir(parents=True, exist_ok=True)
            svg = builder(book, pal).render()
            path.write_text(svg, encoding="utf-8")
            print(f"{path.relative_to(ROOT)}  {len(svg.encode()) / 1024:.1f} KB")


def update_readme_table() -> None:
    if not README.exists():
        return
    text = README.read_text(encoding="utf-8")
    if TABLE_START not in text or TABLE_END not in text:
        return
    head, rest = text.split(TABLE_START, 1)
    _, tail = rest.split(TABLE_END, 1)
    README.write_text(f"{head}{TABLE_START}\n\n{stack_markdown()}\n\n{TABLE_END}{tail}", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fonts-dir", type=Path, required=True)
    parser.add_argument("--only", help="build only assets whose path contains this text")
    args = parser.parse_args()
    write_assets(FontBook(args.fonts_dir), args.only)
    if not args.only:
        update_readme_table()


if __name__ == "__main__":
    main()
