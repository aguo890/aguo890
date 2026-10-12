"""Section headers, contact buttons, and the animated footer."""

from __future__ import annotations

import math
from typing import Callable

from .content import CONTACTS, stack_count
from .svgdoc import Doc, FontBook, Palette, num

SECTION_W, SECTION_H = 1200, 64
BUTTON_H = 88
FOOTER_W, FOOTER_H = 1200, 110
ICONS = {
    "person": '<circle cx="44" cy="37" r="6.5"/><path d="M31 57c1.6-7.5 6.8-11 13-11s11.4 3.5 13 11"/>',
    "mail": '<rect x="29" y="33" width="30" height="22" rx="3"/><path d="M30.5 35.5 44 45.5l13.5-10"/>',
    "globe": ('<circle cx="44" cy="44" r="13"/><ellipse cx="44" cy="44" rx="5.6" ry="13"/>'
              '<path d="M31 44h26M33 37.5h22M33 50.5h22"/>'),
}


def section_builder(spec: tuple[str, str, str, str]) -> Callable[[FontBook, Palette], Doc]:
    slug, index, title, tag = spec

    def build(book: FontBook, pal: Palette) -> Doc:
        label = tag.format(n=stack_count())
        doc = Doc(book, pal, (SECTION_W, SECTION_H), (f"{index} — {title.title()}", f"Section header: {title}"))
        _section(doc, index, title, label)
        return doc

    return build


def _section(doc: Doc, index: str, title: str, tag: str) -> None:
    p = doc.pal
    y = 32
    x = 26
    doc.style("sec", ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}"
                     ".sweep{animation:sweep 5s cubic-bezier(.5,0,.5,1) infinite}")
    doc.add(f'<circle class="pulse" cx="11" cy="{y}" r="5" fill="{p.cy}"{doc.glow(3)}/>')
    for s, font, color, size, ls, gap in [(index, "m7", p.mu, 22, 0, 12), ("//", "m4", p.faint, 22, 0, 14),
                                         (title, "i6", p.tx, 24, 3, 0)]:
        doc.add(doc.text(x, y + 8.5, s, font, size, color, ls=ls))
        x += doc.tw(s, font, size, ls) + gap
    tag_w = doc.tw(tag, "m4", 16, 1.5) + 28
    line_x0, line_x1 = x + 28, SECTION_W - tag_w - 22
    _hairline_with_ticks(doc, line_x0, line_x1, y)
    doc.add(
        f'<rect x="{num(SECTION_W - tag_w - 1)}" y="{y - 14}" width="{num(tag_w)}" height="28" rx="4" '
        f'{doc.panel(1.6)}/>',
        doc.text(SECTION_W - tag_w / 2 - 1, y + 5.5, tag, "m4", 16, p.mu, "middle", 1.5),
    )


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
    doc.style("btn", ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.25}}"
                     ".nudge{animation:nudge 2.4s ease-in-out infinite}"
                     "@keyframes nudge{50%{transform:translate(3px,-3px)}}")
    delay = f' style="animation-delay:{index * 0.8:g}s"'
    doc.add(
        f'<rect x="1" y="1" width="{num(w - 2)}" height="{BUTTON_H - 2}" rx="8" {doc.panel(1.5)}/>',
        f'<rect x="20" y="20" width="48" height="48" rx="7" fill="none" {doc.hair()}/>',
        f'<g fill="none" stroke="{p.tx}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{ICONS[icon]}</g>",
        doc.text(84, 41, label, "m7", 18, p.tx, ls=2),
        doc.text(84, 66, value, "m4", 16, p.mu),
        f'<circle class="pulse" cx="{num(w - 20)}" cy="20" r="3.5" fill="{p.gn}"{doc.glow(2.5)}{delay}/>',
        f'<g class="nudge"{delay}>{doc.text(w - 22, 62, "↗", "m4", 24, p.cy, "end")}</g>',
    )


def footer(book: FontBook, pal: Palette) -> Doc:
    doc = Doc(book, pal, (FOOTER_W, FOOTER_H), ("End of line", "Animated footer with a heartbeat trace and LED."))
    p = doc.pal
    title = "END OF LINE"
    tw = doc.tw(title, "m7", 20, 6)
    cx = FOOTER_W / 2
    left_end, right_start = cx - tw / 2 - 60, cx + tw / 2 + 36
    _ecg(doc, 40, left_end, "a", 0)
    _ecg(doc, right_start, FOOTER_W - 40, "b", 1.5)
    doc.style("hb", ".hb{transform-box:fill-box;transform-origin:center;animation:hb 1.5s ease-out infinite}"
                    "@keyframes hb{0%,100%{transform:scale(1);opacity:.9}12%{transform:scale(1.5);opacity:1}"
                    "24%{transform:scale(1);opacity:.7}36%{transform:scale(1.3);opacity:1}60%{opacity:.6}}")
    doc.add(
        f'<circle class="hb" cx="{num(cx - tw / 2 - 26)}" cy="44" r="5" fill="{p.gn}"{doc.glow(3)}/>',
        doc.text(cx + 3, 51, title, "m7", 20, p.tx, "middle", 6),
        doc.text(cx, 82, "aguo890  ·  SESSION OK", "m4", 16, p.mu, "middle", 1.5),
    )
    return doc


def _ecg_points(x0: float, x1: float, y: float) -> list[tuple[float, float]]:
    beat = [(0, 0), (40, 0), (48, -5), (56, 0), (66, 0), (70, 6), (76, -26), (82, 12), (86, 0), (100, 0),
            (112, -7), (124, 0), (150, 0)]
    pts: list[tuple[float, float]] = []
    x = x0
    while x + 150 <= x1:
        pts.extend((x + dx, y + dy) for dx, dy in beat)
        x += 150
    pts.append((x1, y))
    return pts


def _ecg(doc: Doc, x0: float, x1: float, key: str, delay: float) -> None:
    p = doc.pal
    pts = _ecg_points(x0, x1, 46)
    d = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in pts)
    length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    doc.style(f"ecg{key}", (
        f".ecg{key}{{stroke-dasharray:110 {num(length + 200)};stroke-dashoffset:110;"
        f"animation:ecg{key} 3s linear {delay:g}s infinite}}"
        f"@keyframes ecg{key}{{to{{stroke-dashoffset:-{num(length)}}}}}"))
    comet = f'class="ecg{key}" d="{d}" fill="none" stroke="{p.cy}" stroke-linejoin="round" stroke-linecap="round"'
    halo = f'<path {comet} stroke-width="7" stroke-opacity=".18"/>' if p.glow else ""
    doc.add(
        f'<path d="{d}" fill="none" {doc.hair(0.9)} stroke-linejoin="round"/>',
        halo,
        f'<path {comet} stroke-width="2"/>',
    )
