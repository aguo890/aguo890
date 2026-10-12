"""Technical stack as a layered diagram with tool chips per layer and a languages column."""

from __future__ import annotations

from .content import PYRAMID, RAILS, STACK, stack_count
from .svgdoc import Doc, FontBook, Palette, num, step_keyframes

W = 1200
TOP = 14
PYR_CX = 158
BAND_X0, BAND_X1 = 336, 958
RAIL_X = 988
CHIP_H, CHIP_GAP, ROW_GAP, CHIP_FS, CHIP_PAD = 28, 8, 8, 15, 10
HEADER_H, BAND_GAP = 30, 30
CYCLE_S = 8
TOOLS = dict(STACK)


def build(book: FontBook, pal: Palette) -> Doc:
    probe = Doc(book, pal, (W, 10), ("", ""))
    bands, height = _layout_bands(probe)
    doc = Doc(book, pal, (W, height), (
        "Technical stack",
        f"Layered stack diagram from field and electrical (L0) up to AI and agents (L6), with all "
        f"{stack_count()} stack items on their layer, plus a languages column."))
    _styles(doc)
    for band in bands:
        _draw_band(doc, band)
    _pyramid(doc, bands)
    _rail(doc, height)
    return doc


def _styles(doc: Doc) -> None:
    n = len(PYRAMID)
    css = [".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}",
           f".railflow{{stroke-dasharray:40 400;animation:railflow 6s linear infinite}}"
           f"@keyframes railflow{{to{{stroke-dashoffset:-440}}}}"]
    for k in range(n):  # k = 0 is the bottom layer
        start = k * 100 / CYCLE_S
        css.append(step_keyframes(f"lit{k}", [(0, "opacity:0"), (start, "opacity:1"),
                                              (start + 90 / CYCLE_S, "opacity:0")]))
        css.append(f".lit{k}{{opacity:0;animation:lit{k} {CYCLE_S}s linear infinite}}")
    doc.style("stack", "".join(css))


def _chip_w(doc: Doc, label: str) -> float:
    return doc.tw(label, "m4", CHIP_FS) + 2 * CHIP_PAD


def _layout_bands(doc: Doc) -> tuple[list[dict], int]:
    bands, y = [], TOP
    for code, title, areas in PYRAMID:
        chips, x, row_y = [], BAND_X0, y + HEADER_H
        for ai, area in enumerate(areas):
            items = ([("sub", f"+ {area.upper()}")] if ai else []) + [("chip", t) for t in TOOLS[area]]
            for kind, label in items:
                w = _chip_w(doc, label) if kind == "chip" else doc.tw(label, "m4", CHIP_FS) + 4
                if x + w > BAND_X1:
                    x, row_y = BAND_X0, row_y + CHIP_H + ROW_GAP
                chips.append((kind, label, x, row_y, w))
                x += w + CHIP_GAP
        bands.append({"code": code, "title": title, "y": y, "chips": chips})
        y = row_y + CHIP_H + BAND_GAP
    return bands, int(y - BAND_GAP + 16)


def _draw_band(doc: Doc, band: dict) -> None:
    p = doc.pal
    y, k = band["y"], len(PYRAMID) - 1 - [b[0] for b in PYRAMID].index(band["code"])
    title_x = BAND_X0 + 18 + doc.tw(band["code"], "m7", 16) + 10
    doc.add(
        f'<circle cx="{BAND_X0 + 5}" cy="{y + 9}" r="4" fill="{p.faint}"/>',
        f'<circle class="lit{k}" cx="{BAND_X0 + 5}" cy="{y + 9}" r="4" fill="{p.cy}"{doc.glow(3)}/>',
        doc.text(BAND_X0 + 18, y + 15, band["code"], "m7", 16, p.mu),
        doc.text(title_x, y + 15, band["title"], "m7", 16, p.tx, ls=1.5),
    )
    line_x = title_x + doc.tw(band["title"], "m7", 16, 1.5) + 16
    doc.add(f'<path d="M{num(line_x)} {y + 9}H{BAND_X1}" {doc.hair()}/>')
    for kind, label, x, cy, w in band["chips"]:
        if kind == "sub":
            doc.add(doc.text(x, cy + 19, label, "m4", CHIP_FS, p.mu))
            continue
        doc.add(
            f'<rect x="{num(x)}" y="{num(cy)}" width="{num(w)}" height="{CHIP_H}" rx="5" {doc.panel(1.5)}/>',
            doc.text(x + CHIP_PAD, cy + 19, label, "m4", CHIP_FS, p.tx),
        )


def _slab(doc: Doc, cx: float, cy: float, a: float, k: int) -> str:
    p, hw, t = doc.pal, a * 1.732, 10
    a = hw * 0.5
    top = f"M{num(cx)} {num(cy - a)}L{num(cx + hw)} {num(cy)}L{num(cx)} {num(cy + a)}L{num(cx - hw)} {num(cy)}Z"
    left = (f"M{num(cx - hw)} {num(cy)}L{num(cx)} {num(cy + a)}V{num(cy + a + t)}"
            f"L{num(cx - hw)} {num(cy + t)}Z")
    right = (f"M{num(cx)} {num(cy + a)}L{num(cx + hw)} {num(cy)}V{num(cy + t)}"
             f"L{num(cx)} {num(cy + a + t)}Z")
    op = p.panel_op
    return (
        f'<path d="{left}" fill="{p.panel}" fill-opacity="{op * 3:.3g}" {doc.hair()}/>'
        f'<path d="{right}" fill="{p.panel}" fill-opacity="{op * 1.6:.3g}" {doc.hair()}/>'
        f'<path d="{top}" fill="{p.panel}" fill-opacity="{op * 2.2:.3g}" {doc.hair(1.3)}/>'
        f'<path class="lit{k}" d="{top}" fill="{p.cy}" fill-opacity=".08" stroke="{p.cy}" stroke-width="1.5"/>'
    )


def _pyramid(doc: Doc, bands: list[dict]) -> None:
    p, n = doc.pal, len(bands)
    first, last = bands[0]["y"] + 9, bands[-1]["y"] + 9
    spacing = (last - first) / (n - 1)
    mid = (first + last) / 2
    centers = [mid + (i - (n - 1) / 2) * spacing for i in range(n)]
    sizes = [30 + i * (78 - 30) / (n - 1) for i in range(n)]
    leaders, slabs = [], []
    for i in reversed(range(n)):  # paint bottom slab first
        k = n - 1 - i
        cx, cy, a = PYR_CX, centers[i], sizes[i]
        slabs.append(_slab(doc, cx, cy, a, k))
        slabs.append(doc.text(cx, cy + 5.5, bands[i]["code"], "m7", 16, p.mu, "middle"))
        vx = cx + a * 1.732
        leaders.append(f"M{num(vx + 6)} {num(cy)}h14L{BAND_X0 - 12} {bands[i]['y'] + 9}h6")
    doc.add(f'<path d="{" ".join(leaders)}" fill="none" {doc.hair()} stroke-dasharray="3 4"/>', *slabs)
    _packet(doc, centers)


def _packet(doc: Doc, centers: list[float]) -> None:
    p = doc.pal
    top, bottom = centers[0], centers[-1]
    frames = []
    for k, cy in enumerate(reversed(centers)):
        t0 = k * 100 / CYCLE_S
        frames.append(f"{t0:.2f}%,{t0 + 40 / CYCLE_S:.2f}%{{transform:translateY({num(cy - bottom)}px)}}")
    end = (len(centers) - 1) * 100 / CYCLE_S + 40 / CYCLE_S
    doc.style("packet", (
        f".packet{{animation:packet {CYCLE_S}s cubic-bezier(.6,0,.3,1) infinite,"
        f"pfade {CYCLE_S}s linear infinite}}@keyframes packet{{{''.join(frames)}"
        f"100%{{transform:translateY({num(top - bottom)}px)}}}}"
        f"@keyframes pfade{{0%,{end:.2f}%{{opacity:1}}{end + 6:.2f}%,98%{{opacity:0}}100%{{opacity:1}}}}"))
    doc.add(
        f'<path d="M{PYR_CX} {num(bottom)}V{num(top)}" stroke="{p.cy}" stroke-opacity=".35" '
        'stroke-dasharray="2 5"/>',
        f'<circle class="packet" cx="{PYR_CX}" cy="{num(bottom)}" r="5" fill="{p.cy}"{doc.glow(4)}/>',
    )


def _rail(doc: Doc, height: int) -> None:
    p = doc.pal
    langs, spoken = TOOLS[RAILS[0]], TOOLS[RAILS[1]]
    x_line, x_chip = RAIL_X + 6, RAIL_X + 20
    top, bottom = TOP + HEADER_H, height - 16
    spoken_top = bottom - 2 * (CHIP_H + 10) - HEADER_H
    pitch = min(54.0, max(CHIP_H + 8, (spoken_top - 30 - top) / len(langs)))
    doc.add(
        doc.text(RAIL_X, TOP + 15, "LANGUAGES", "m7", 16, p.tx, ls=1.5),
        f'<path d="M{x_line} {top - 6}V{bottom - CHIP_H / 2}" {doc.hair()}/>',
        f'<path class="railflow" d="M{x_line} {top - 6}V{bottom - CHIP_H / 2}" stroke="{p.cy}" '
        'stroke-width="2"/>',
        doc.text(RAIL_X, spoken_top + 15, "SPOKEN", "m7", 16, p.tx, ls=1.5),
    )
    rows = [(t, top + i * pitch) for i, t in enumerate(langs)]
    rows += [(t, spoken_top + HEADER_H + i * (CHIP_H + 10)) for i, t in enumerate(spoken)]
    for label, y in rows:
        w = _chip_w(doc, label)
        doc.add(
            f'<path d="M{x_line} {num(y + CHIP_H / 2)}H{x_chip}" {doc.hair()}/>',
            f'<circle cx="{x_line}" cy="{num(y + CHIP_H / 2)}" r="2.5" fill="{p.mu}"/>',
            f'<rect x="{x_chip}" y="{num(y)}" width="{num(w)}" height="{CHIP_H}" rx="5" {doc.panel(1.5)}/>',
            doc.text(x_chip + CHIP_PAD, y + 19, label, "m4", CHIP_FS, p.tx),
        )
