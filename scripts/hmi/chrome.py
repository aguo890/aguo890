"""Section headers and contact buttons."""

from __future__ import annotations

import math
from typing import Callable

from .content import CONTACTS
from .svgdoc import Doc, FontBook, Palette, num

SECTION_W, SECTION_H = 1200, 64
BUTTON_H = 88
ICONS = {
    "person": '<circle cx="44" cy="37" r="6.5"/><path d="M31 57c1.6-7.5 6.8-11 13-11s11.4 3.5 13 11"/>',
    "mail": '<rect x="29" y="33" width="30" height="22" rx="3"/><path d="M30.5 35.5 44 45.5l13.5-10"/>',
    "globe": ('<circle cx="44" cy="44" r="13"/><ellipse cx="44" cy="44" rx="5.6" ry="13"/>'
              '<path d="M31 44h26M33 37.5h22M33 50.5h22"/>'),
}


def section_builder(spec: tuple[str, str]) -> Callable[[FontBook, Palette], Doc]:
    _, title = spec

    def build(book: FontBook, pal: Palette) -> Doc:
        doc = Doc(book, pal, (SECTION_W, SECTION_H), (title.capitalize(), f"Section header: {title.capitalize()}"))
        _section(doc, title)
        return doc

    return build


def _section(doc: Doc, title: str) -> None:
    y = 32
    doc.style("sec", ".sweep{animation:sweep 5s cubic-bezier(.5,0,.5,1) infinite}")
    doc.add(doc.text(0, y + 8.5, title, "i6", 24, doc.pal.tx, ls=3))
    _hairline_with_ticks(doc, doc.tw(title, "i6", 24, 3) + 28, SECTION_W - 1, y)


def _hairline_with_ticks(doc: Doc, x0: float, x1: float, y: float) -> None:
    p = doc.pal
    ticks = " ".join(f"M{num(x)} {y - 4}v8" for x in _frange(x0, x1, 48))
    span = x1 - x0
    doc.define("sweepg", (
        f'<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p.cy}" '
        f'stop-opacity="0"/><stop offset=".85" stop-color="{p.cy}"/><stop offset="1" stop-color="{p.cy}" '
        f'stop-opacity="0"/></linearGradient>'
        f'<clipPath id="lineclip"><rect x="{num(x0)}" y="{y - 6}" width="{num(span)}" height="12"/></clipPath>'))
    doc.style("sweepk", f"@keyframes sweep{{from{{transform:translateX(0)}}to{{transform:translateX({num(span + 140)}px)}}}}")
    doc.add(
        f'<path d="M{num(x0)} {y}H{num(x1)}" {doc.hair()}/>',
        f'<path d="{ticks}" {doc.hair(0.8)}/>',
        f'<g clip-path="url(#lineclip)"><rect class="sweep" x="{num(x0 - 140)}" y="{y - 1.5}" width="140" '
        f'height="3" rx="1.5" fill="url(#sweepg)"/></g>',
    )


def _frange(a: float, b: float, step: float) -> list[float]:
    n = int((b - a) // step)
    return [a + i * step for i in range(1, n + 1) if a + i * step < b - 8]


def button_width(book: FontBook) -> float:
    widest = max(max(book.width("m4", v, 16), book.width("m7", label, 18, 2)) for _, label, v, _ in CONTACTS)
    return math.ceil(84 + widest + 56)


def contact_builder(spec: tuple[str, str, str, str]) -> Callable[[FontBook, Palette], Doc]:
    slug, label, value, icon = spec
    index = [c[0] for c in CONTACTS].index(slug)

    def build(book: FontBook, pal: Palette) -> Doc:
        w = button_width(book)
        doc = Doc(book, pal, (w, BUTTON_H), (f"{label.title()}: {value}", f"Contact button for {label.title()}"))
        _button(doc, w, (label, value, icon), index)
        return doc

    return build


def _button(doc: Doc, w: float, spec: tuple[str, str, str], index: int) -> None:
    label, value, icon = spec
    p = doc.pal
    doc.style("btn", ".nudge{animation:nudge 2.4s ease-in-out infinite}"
                     "@keyframes nudge{50%{transform:translate(3px,-3px)}}")
    delay = f' style="animation-delay:{index * 0.8:g}s"'
    doc.add(
        f'<rect x="1" y="1" width="{num(w - 2)}" height="{BUTTON_H - 2}" rx="8" {doc.panel(1.5)}/>',
        f'<rect x="20" y="20" width="48" height="48" rx="7" fill="none" {doc.hair()}/>',
        f'<g fill="none" stroke="{p.tx}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{ICONS[icon]}</g>",
        doc.text(84, 41, label, "m7", 18, p.tx, ls=2),
        doc.text(84, 66, value, "m4", 16, p.mu),
        f'<g class="nudge"{delay}>{doc.text(w - 22, 62, "↗", "m4", 24, p.cy, "end")}</g>',
    )
