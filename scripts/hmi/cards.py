"""Project faceplate cards: shared frame plus one animated mini-visual per project."""

from __future__ import annotations

import random
from typing import Callable

from .content import Card
from .svgdoc import Doc, FontBook, Palette, num, step_keyframes

CW, CH = 600, 340
PAD = 24
VX, VY, VW, VH = PAD, 164, CW - 2 * PAD, 124
LED_BY_KIND = {"internal": "mu", "private": "gn", "public": "cy"}
FOOTER_NOTE = {"plant-data-reliability": "6 tools · one summer"}
BASE_CSS = (
    ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}"
    ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:.2}}"
    ".flow{stroke-dasharray:5 7;animation:flow .9s linear infinite}@keyframes flow{to{stroke-dashoffset:-12}}"
)


def card_builder(card: Card, index: int) -> Callable[[FontBook, Palette], Doc]:
    def build(book: FontBook, pal: Palette) -> Doc:
        doc = Doc(book, pal, (CW, CH), (card.title, card.alt))
        doc.style("base", BASE_CSS)
        _frame(doc, card, index)
        VISUALS[card.slug](doc)
        return doc

    return build


def _frame(doc: Doc, card: Card, index: int) -> None:
    p = doc.pal
    led = getattr(p, LED_BY_KIND[card.kind])
    pulse = ' class="pulse"' if card.kind != "internal" else ""
    doc.add(
        f'<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="6" {doc.panel(1.2)}/>',
        _brackets(doc),
        f'<circle{pulse} cx="{PAD + 6}" cy="31" r="5" fill="{led}"{doc.glow(3) if pulse else ""}/>',
        doc.text(PAD + 20, 37, f"P-{index + 1:02d}", "m7", 16, p.mu, ls=1),
    )
    tag_w = doc.tw(card.tag, "m4", 16, 0.5) + 24
    doc.add(
        f'<rect x="{num(CW - PAD - tag_w)}" y="17" width="{num(tag_w)}" height="27" rx="4" {doc.panel(2)}/>',
        doc.text(CW - PAD - tag_w / 2, 36, card.tag, "m4", 16, p.mu, "middle", 0.5),
        doc.text(PAD, 92, card.title, "i6", 30, p.tx, ls=-0.3),
    )
    for i, line in enumerate(_wrap(doc, card.blurb, "i4", 18, VW)):
        doc.add(doc.text(PAD, 123 + i * 23, line, "i4", 18, p.mu))
    _footer(doc, card)


def _brackets(doc: Doc) -> str:
    s, x0, y0, x1, y1 = 12, 1, 1, CW - 1, CH - 1
    d = (f"M{x0} {y0 + s}V{y0}H{x0 + s} M{x1 - s} {y0}H{x1}V{y0 + s} "
         f"M{x1} {y1 - s}V{y1}H{x1 - s} M{x0 + s} {y1}H{x0}V{y1 - s}")
    return f'<path d="{d}" fill="none" stroke="{doc.pal.mu}" stroke-width="1.6" stroke-opacity=".7"/>'


def _wrap(doc: Doc, text: str, font: str, size: float, width: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and doc.tw(trial, font, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    if len(lines) > 2:
        raise ValueError(f"blurb wraps to {len(lines)} lines: {text!r}")
    return lines


def _footer(doc: Doc, card: Card) -> None:
    p = doc.pal
    y = CH - 40
    note = "↗ view repo" if card.repo else FOOTER_NOTE.get(card.slug, "")
    note_font = "m7" if card.repo else "m4"
    note_w = doc.tw(note, note_font, 16) if note else 0
    stack = " · ".join(card.stack)
    size = 16.0
    while doc.tw(stack, "m4", size) + note_w + 24 > VW:
        size -= 0.5
    doc.add(
        f'<path d="M{PAD} {y}H{CW - PAD}" {doc.hair()}/>',
        doc.text(PAD, y + 25, stack, "m4", size, p.mu),
    )
    if note:
        doc.add(doc.text(CW - PAD, y + 25, note, note_font, 16, p.cy if card.repo else p.mu, "end"))


# ---------------------------------------------------------------- visuals


def _relay(doc: Doc) -> None:
    p = doc.pal
    cols, rows, pitch, x0, y0 = 24, 6, 15, VX + 8, VY + 12
    rnd = random.Random(3)
    drift = {(rnd.randrange(cols), rnd.randrange(rows)) for _ in range(6)}
    sweep_s = 3.6
    doc.style("relay", (
        ".drift{opacity:0;animation:drift 7s linear infinite}"
        "@keyframes drift{0%,64%{opacity:0}66%,74%{opacity:1}76%,79%{opacity:.15}81%,92%{opacity:1}94%,100%{opacity:0}}"
        f".ping{{opacity:0;animation:ping {sweep_s}s linear infinite}}"
        "@keyframes ping{0%{opacity:.85}14%,100%{opacity:0}}"
        f".sweepbar{{animation:sweepbar {sweep_s}s linear infinite}}"
        f"@keyframes sweepbar{{from{{transform:translateX(0)}}to{{transform:translateX({cols * pitch}px)}}}}"))
    leds, pings, drifts = [], [], []
    for c in range(cols):
        col = []
        for r in range(rows):
            cx, cy = x0 + c * pitch, y0 + r * pitch
            leds.append(f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{p.faint}"/>')
            col.append(f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="{p.cy}"/>')
            if (c, r) in drift:
                delay = -rnd.uniform(0, 7)
                drifts.append(f'<circle class="drift" cx="{cx}" cy="{cy}" r="3.8" fill="{p.am}" '
                              f'style="animation-delay:{delay:.2f}s"{doc.glow(2.5)}/>')
        pings.append(f'<g class="ping" style="animation-delay:{c * sweep_s / cols:.3f}s">{"".join(col)}</g>')
    doc.add(
        f'<rect class="sweepbar" x="{x0 - 7}" y="{y0 - 8}" width="14" height="{(rows - 1) * pitch + 16}" rx="7" '
        f'fill="{p.cy}" fill-opacity=".1" stroke="{p.cy}" stroke-opacity=".35"/>',
        "".join(leds), "".join(pings), "".join(drifts),
    )
    _legend(doc, VX + 2, VY + 116, [("IN SPEC", p.faint), ("POLLED", p.cy), ("DRIFT", p.am)])
    _relay_readout(doc)


def _legend(doc: Doc, x: float, y: float, items: list[tuple[str, str]]) -> None:
    for label, color in items:
        doc.add(f'<circle cx="{num(x + 4)}" cy="{num(y - 5)}" r="4" fill="{color}"/>',
                doc.text(x + 14, y, label, "m4", 15, doc.pal.mu))
        x += doc.tw(label, "m4", 15) + 34


def _relay_readout(doc: Doc) -> None:
    p = doc.pal
    x = 410
    lock = (f'<g fill="none" stroke="{p.tx}" stroke-width="1.6"><rect x="{x}" y="{VY + 37}" width="13" height="10" '
            f'rx="2"/><path d="M{x + 3} {VY + 37}v-3.5a3.5 3.5 0 0 1 7 0V{VY + 37}"/></g>')
    doc.add(
        f'<path d="M392 {VY + 4}V{VY + VH - 4}" {doc.hair()}/>',
        doc.text(x, VY + 22, "MODE", "m4", 15, p.mu, ls=1),
        lock,
        doc.text(x + 22, VY + 47, "READ-ONLY", "m7", 16, p.tx, ls=0.5),
        doc.text(x, VY + 82, "WRITES", "m4", 15, p.mu, ls=1),
        doc.text(x, VY + 107, "HUMAN-GATED", "m7", 16, p.am, ls=0.5),
    )


AGENT_NODES = ["AGENT", "MCP", "SANDBOX GW", "VISUAL CHECK", "HUMAN PROMOTE", "PROD"]
AGENT_GRID = [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (0, 1)]
AGENT_STEP_S, AGENT_DWELL_S = 1.5, 0.85


def _agent_loop(doc: Doc) -> None:
    p = doc.pal
    nw, nh = 152, 32
    xs = [VX + nw / 2, VX + VW / 2, VX + VW - nw / 2]
    ys = [VY + 26, VY + 98]
    centers = [(xs[c], ys[r]) for c, r in AGENT_GRID]
    doc.add(
        f'<rect x="{num(xs[0])}" y="{ys[0]}" width="{num(xs[2] - xs[0])}" height="{ys[1] - ys[0]}" rx="22" '
        f'fill="none" {doc.hair()} stroke-dasharray="4 5"/>',
        _chevrons(doc, xs, ys),
    )
    _agent_token(doc, centers, nw, nh)
    cycle = AGENT_STEP_S * len(AGENT_NODES)
    accents = {4: p.am, 5: p.gn}
    for i, (label, (cx, cy)) in enumerate(zip(AGENT_NODES, centers)):
        box = f'x="{num(cx - nw / 2)}" y="{num(cy - nh / 2)}" width="{nw}" height="{nh}" rx="5"'
        start = i * AGENT_STEP_S / cycle * 100
        end = start + (AGENT_DWELL_S + 0.15) / cycle * 100
        doc.style(f"n{i}", step_keyframes(f"n{i}", [(0, "opacity:0"), (start, "opacity:1"), (end, "opacity:0")])
                  + f".n{i}{{opacity:0;animation:n{i} {cycle:g}s linear infinite}}")
        color = accents.get(i, p.cy)
        doc.add(
            f'<rect {box} {doc.panel(4)}/>',
            f'<rect class="n{i}" {box} fill="{color}" fill-opacity=".14" stroke="{color}" stroke-width="1.6"/>',
            doc.text(cx, cy + 5.5, label, "m4", 15, p.tx, "middle"),
        )


def _chevrons(doc: Doc, xs: list[float], ys: list[float]) -> str:
    mx1, mx2 = (xs[0] + xs[1]) / 2, (xs[1] + xs[2]) / 2
    my = (ys[0] + ys[1]) / 2
    right = [(mx1, ys[0]), (mx2, ys[0])]
    left = [(mx1, ys[1]), (mx2, ys[1])]
    d = [f"M{num(x - 3)} {num(y - 5)}l6 5-6 5" for x, y in right]
    d += [f"M{num(x + 3)} {num(y - 5)}l-6 5 6 5" for x, y in left]
    d += [f"M{num(xs[2] - 5)} {num(my - 3)}l5 6 5-6", f"M{num(xs[0] - 5)} {num(my + 3)}l5-6 5 6"]
    return f'<path d="{" ".join(d)}" fill="none" stroke="{doc.pal.mu}" stroke-width="1.6"/>'


def _edge(a: tuple[float, float], b: tuple[float, float], nw: float, nh: float) -> tuple[float, float]:
    """Point on node a's border facing node b."""
    if a[1] == b[1]:
        return (a[0] + (nw / 2 if b[0] > a[0] else -nw / 2), a[1])
    return (a[0], a[1] + (nh / 2 if b[1] > a[1] else -nh / 2))


def _agent_token(doc: Doc, centers: list[tuple[float, float]], nw: float, nh: float) -> None:
    n = len(centers)
    cycle = AGENT_STEP_S * n
    x0, y0 = centers[0]
    frames = []
    for i in range(n):
        a, b = centers[i], centers[(i + 1) % n]
        s, e = _edge(a, b, nw, nh), _edge(b, a, nw, nh)
        t_move = (i * AGENT_STEP_S + AGENT_DWELL_S) / cycle * 100
        t_end = (i + 1) * AGENT_STEP_S / cycle * 100
        tr = lambda pt: f"transform:translate({num(pt[0] - x0)}px,{num(pt[1] - y0)}px)"  # noqa: E731
        frames += [f"{i * AGENT_STEP_S / cycle * 100:.2f}%{{{tr(s)};opacity:0}}",
                   f"{t_move:.2f}%{{{tr(s)};opacity:1}}",
                   f"{t_end - 0.4:.2f}%{{{tr(e)};opacity:1}}",
                   f"{t_end - 0.01:.2f}%{{{tr(e)};opacity:0}}"]
    doc.style("token", f".token{{opacity:0;animation:token {cycle:g}s ease-in-out infinite}}"
                       f"@keyframes token{{{''.join(frames)}}}")
    doc.add(f'<circle class="token" cx="{num(x0)}" cy="{num(y0)}" r="5" fill="{doc.pal.cy}"{doc.glow(3)}/>')


def _spc(doc: Doc) -> None:
    p = doc.pal
    px0, px1 = VX + 48, VX + VW - 14
    ucl, cl, lcl = VY + 16, VY + 62, VY + 108
    sigma = (lcl - cl) / 3
    rnd = random.Random(11)
    n, ooc = 20, 13
    zs = [max(-2.6, min(2.6, rnd.gauss(0, 0.9))) for _ in range(n)]
    zs[ooc] = 3.7
    pts = [(px0 + 10 + i * (px1 - px0 - 20) / (n - 1), cl - z * sigma) for i, z in enumerate(zs)]
    span = px1 - px0
    reveal_pct = 62.5
    ooc_pct = (pts[ooc][0] - px0) / span * reveal_pct
    doc.define("spcclip", f'<clipPath id="spcclip"><rect class="spcrev" x="{px0}" y="{VY - 6}" '
                          f'width="{span}" height="{VH + 8}"/></clipPath>')
    doc.style("spc", (
        ".spcrev{transform-box:fill-box;transform-origin:0 0;animation:spcrev 8s linear infinite}"
        f"@keyframes spcrev{{0%{{transform:scaleX(0)}}{reveal_pct}%,100%{{transform:scaleX(1)}}}}"
        ".spccur{opacity:0;animation:spccur 8s linear infinite}"
        f"@keyframes spccur{{0%{{opacity:1;transform:translateX(0)}}{reveal_pct}%{{opacity:1;"
        f"transform:translateX({span}px)}}{reveal_pct + 3}%,100%{{opacity:0;transform:translateX({span}px)}}}}"
        + step_keyframes("oocw", [(0, "opacity:0"), (ooc_pct, "opacity:1")])
        + ".oocw{opacity:1;animation:oocw 8s linear infinite}"))
    limits = f'stroke="{p.mu}" stroke-width="1.3" stroke-dasharray="6 5"'
    doc.add(
        f'<path d="M{px0} {ucl}H{px1} M{px0} {lcl}H{px1}" {limits}/>',
        f'<path d="M{px0} {cl}H{px1}" stroke="{p.mu}" stroke-opacity=".7" stroke-width="1.2"/>',
        doc.text(VX, ucl + 5, "UCL", "m4", 15, p.mu), doc.text(VX, cl + 5, "CL", "m4", 15, p.mu),
        doc.text(VX, lcl + 5, "LCL", "m4", 15, p.mu),
        doc.text(px1, ucl - 7, "+3σ", "m4", 15, p.faint, "end"),
        doc.text(px1, lcl + 18, "−3σ", "m4", 15, p.faint, "end"),
    )
    line = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in pts)
    dots = "".join(f'<circle cx="{num(x)}" cy="{num(y)}" r="3" fill="{p.tx}"/>'
                   for i, (x, y) in enumerate(pts) if i != ooc)
    ox, oy = pts[ooc]
    doc.add(
        f'<g clip-path="url(#spcclip)"><path d="{line}" fill="none" stroke="{p.tx}" stroke-opacity=".55" '
        f'stroke-width="1.5" stroke-linejoin="round"/>{dots}'
        f'<circle cx="{num(ox)}" cy="{num(oy)}" r="4.5" fill="{p.rd}"/></g>',
        f'<g class="oocw"><circle class="blink" cx="{num(ox)}" cy="{num(oy)}" r="10" fill="none" stroke="{p.rd}" '
        f'stroke-width="1.8"{doc.glow(2.5)}/>{doc.text(ox + 16, oy + 5, "OOC", "m7", 15, p.rd)}</g>',
        f'<path class="spccur" d="M{px0} {VY - 2}V{VY + VH - 2}" stroke="{p.cy}" stroke-width="1.5" '
        'stroke-opacity=".8"/>',
    )


def _fabrik(doc: Doc) -> None:
    p = doc.pal
    base, max_h, bw, pitch = VY + VH - 2, 90, 22, 33
    target_h = 68
    heights = [0.8, 0.84, 0.88, 0.82, 0.9, 0.6, 0.86, 0.92, 0.87, 0.84]
    doc.style("fab", (
        ".bar{transform-box:fill-box;transform-origin:50% 100%;animation:grow 8s cubic-bezier(.3,0,.2,1) "
        "infinite backwards}@keyframes grow{0%{transform:scaleY(.04)}10%,90%{transform:scaleY(1)}"
        "100%{transform:scaleY(.04)}}"))
    bars = []
    for i, f in enumerate(heights):
        h = f * max_h
        color = p.am if h < target_h else p.mu
        op = "1" if h < target_h else ".55"
        bars.append(f'<rect class="bar" x="{VX + 8 + i * pitch}" y="{num(base - h)}" width="{bw}" height="{num(h)}" '
                    f'rx="2" fill="{color}" fill-opacity="{op}" style="animation-delay:{i * 0.12:.2f}s"/>')
    tx1 = VX + 8 + len(heights) * pitch - 6
    doc.add(
        doc.text(VX, VY + 12, "HOURLY OUTPUT vs TARGET", "m4", 15, p.mu, ls=0.5),
        "".join(bars),
        f'<path d="M{VX} {base}H{tx1}" {doc.hair()}/>',
        f'<path d="M{VX} {base - target_h}H{tx1}" stroke="{p.tx}" stroke-width="1.4" stroke-dasharray="7 5"/>',
    )
    _andon(doc, tx1 + 22)


def _andon(doc: Doc, x0: float) -> None:
    p = doc.pal
    w = VX + VW - x0
    doc.add(
        f'<rect x="{num(x0)}" y="{VY + 2}" width="{num(w)}" height="{VH - 4}" rx="6" {doc.panel(2.5)}/>',
        doc.text(x0 + 16, VY + 26, "ANDON · TV", "m4", 15, p.mu, ls=0.5),
        f'<rect class="pulse" x="{num(x0 + 16)}" y="{VY + 38}" width="5" height="30" rx="2" fill="{p.gn}"'
        f'{doc.glow(3)}/>',
        doc.text(x0 + 30, VY + 65, "RUN", "m7", 32, p.gn, ls=2),
        doc.text(x0 + 16, VY + 92, "100 pages", "m4", 15, p.tx),
        doc.text(x0 + 16, VY + 112, "5,300+ tests", "m4", 15, p.tx),
    )


def _job_pipeline(doc: Doc) -> None:
    p = doc.pal
    cols = [VX, VX + 196, VX + 404]
    for x, label in zip(cols, ["01 SCRAPE", "02 RANK", "03 PDF"]):
        doc.add(doc.text(x, VY + 12, label, "m7", 15, p.mu, ls=1))
    srcs = ["Greenhouse", "Lever", "Ashby"]
    sw = 138
    rank_x, rank_w = cols[1], 170
    rank_mid = VY + 70
    links = []
    for i, s in enumerate(srcs):
        y = VY + 26 + i * 32
        doc.add(f'<rect x="{VX}" y="{y}" width="{sw}" height="26" rx="4" {doc.panel(2.5)}/>',
                doc.text(VX + 12, y + 18, s, "m4", 15, p.tx))
        links.append(f"M{VX + sw} {y + 13}C{VX + sw + 30} {y + 13} {rank_x - 30} {rank_mid} {rank_x - 6} {rank_mid}")
    links.append(f"M{rank_x + rank_w + 8} {rank_mid}H{cols[2] - 6}")
    doc.add(f'<path class="flow" d="{" ".join(links)}" fill="none" stroke="{p.cy}" stroke-opacity=".7" '
            'stroke-width="1.4"/>')
    _rank_bars(doc, rank_x, rank_w)
    _pdf_doc(doc, cols[2])


def _rank_bars(doc: Doc, x: float, w: float) -> None:
    p = doc.pal
    doc.style("rank", (
        ".rbar{transform-box:fill-box;transform-origin:0 50%;animation:rbar 6s cubic-bezier(.3,0,.2,1) infinite "
        "backwards}@keyframes rbar{0%{transform:scaleX(.05)}14%,88%{transform:scaleX(1)}100%{transform:scaleX(.05)}}"))
    for i, f in enumerate([0.94, 0.76, 0.6, 0.42]):
        y = VY + 32 + i * 20
        color, op = (p.cy, "1") if i == 0 else (p.mu, ".6")
        doc.add(
            f'<rect x="{num(x)}" y="{y}" width="{num(w)}" height="12" rx="3" fill="{p.faint}" fill-opacity=".35"/>',
            f'<rect class="rbar" x="{num(x)}" y="{y}" width="{num(w * f)}" height="12" rx="3" fill="{color}" '
            f'fill-opacity="{op}" style="animation-delay:{0.3 + i * 0.15:.2f}s"/>',
        )
    doc.add(doc.text(x, VY + 118, "scored + sorted", "m4", 15, p.mu))


def _pdf_doc(doc: Doc, x: float) -> None:
    p = doc.pal
    y, w, h, fold = VY + 26, 62, 84, 14
    page = f"M{x} {y}H{x + w - fold}L{x + w} {y + fold}V{y + h}H{x}Z"
    doc.style("pdf", (
        ".pline{transform-box:fill-box;transform-origin:0 50%;animation:pline 6s steps(12) infinite backwards}"
        "@keyframes pline{0%{transform:scaleX(0)}20%,90%{transform:scaleX(1)}100%{transform:scaleX(0)}}"))
    lines = "".join(
        f'<rect class="pline" x="{x + 10}" y="{y + 22 + i * 11}" width="{num((w - 20) * f)}" height="4" rx="2" '
        f'fill="{p.cy if i == 0 else p.mu}" style="animation-delay:{1.2 + i * 0.25:.2f}s"/>'
        for i, f in enumerate([0.9, 1, 0.7, 0.95, 0.6]))
    doc.add(
        f'<path d="{page}" {doc.panel(3)} stroke-linejoin="round"/>',
        f'<path d="M{x + w - fold} {y}V{y + fold}H{x + w}" fill="none" {doc.hair()}/>',
        lines,
        doc.text(x + w + 14, y + 26, "tailored", "m4", 15, p.mu),
        doc.text(x + w + 14, y + 50, "RÉSUMÉ", "m7", 16, p.tx, ls=1),
        doc.text(x + w + 14, y + 74, "LaTeX→PDF", "m4", 15, p.mu),
    )


def _linesight(doc: Doc) -> None:
    p = doc.pal
    gx, gy, cw, ch, cols, rows = VX, VY + 10, 38, 21, 5, 5
    rnd = random.Random(5)
    messy = {(1, 2), (3, 4), (4, 1)}
    cells = []
    for r in range(rows):
        for c in range(cols):
            x, y = gx + c * cw, gy + r * ch
            fill = f'fill="{p.panel}" fill-opacity="{p.panel_op * (5 if r == 0 else 1.5):.3g}"'
            cells.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" {fill} {doc.hair()}/>')
            if r:
                color = p.am if (r, c) in messy else p.mu
                bw = rnd.randint(10, cw - 12)
                cells.append(f'<rect x="{x + 6}" y="{y + 8}" width="{bw}" height="5" rx="2" fill="{color}" '
                             f'fill-opacity="{1 if (r, c) in messy else 0.6}"/>')
    doc.style("ls", (
        f".scanrow{{animation:scanrow 5s steps(1) infinite}}@keyframes scanrow{{"
        + "".join(f"{i * 25}%{{transform:translateY({i * ch}px)}}" for i in range(4)) + "}"))
    doc.add(
        "".join(cells),
        f'<rect class="scanrow" x="{gx}" y="{gy + ch}" width="{cols * cw}" height="{ch}" fill="{p.cy}" '
        f'fill-opacity=".12" stroke="{p.cy}" stroke-width="1.4"/>',
    )
    ax0, ax1, ay = gx + cols * cw + 14, gx + cols * cw + 112, VY + 66
    doc.add(
        doc.text((ax0 + ax1) / 2, ay - 12, "LLM ETL", "m7", 15, p.cy, "middle", 0.5),
        f'<path class="flow" d="M{ax0} {ay}H{ax1 - 8}" stroke="{p.cy}" stroke-width="2"/>',
        f'<path d="M{ax1 - 10} {ay - 6}l8 6-8 6" fill="none" stroke="{p.cy}" stroke-width="2"/>',
        doc.text((ax0 + ax1) / 2, ay + 26, "semantic", "m4", 15, p.mu, "middle"),
    )
    _flying_cells(doc, (gx + 3 * cw, gy + 2 * ch), (ax1 + 40, VY + 70))
    _mini_dashboard(doc, ax1 + 14)


def _flying_cells(doc: Doc, start: tuple[float, float], end: tuple[float, float]) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    doc.style("fly", (
        ".fly{opacity:0;transform-box:fill-box;transform-origin:center;animation:fly 5s cubic-bezier(.5,0,.3,1) infinite}"
        f"@keyframes fly{{0%{{opacity:0;transform:translate(0,0)}}8%{{opacity:.9}}"
        f"30%{{opacity:.9;transform:translate({num(dx)}px,{num(dy)}px) scale(.6)}}"
        f"36%,100%{{opacity:0;transform:translate({num(dx)}px,{num(dy)}px) scale(.6)}}}}"))
    doc.add("".join(
        f'<rect class="fly" x="{num(start[0])}" y="{num(start[1] + i * 9)}" width="16" height="7" rx="2" '
        f'fill="{doc.pal.cy}" style="animation-delay:{i * 1.25:.2f}s"/>' for i in range(4)))


def _mini_dashboard(doc: Doc, x0: float) -> None:
    p = doc.pal
    w = VX + VW - x0
    base = VY + VH - 14
    doc.add(
        f'<rect x="{num(x0)}" y="{VY + 2}" width="{num(w)}" height="{VH - 4}" rx="6" {doc.panel(2.5)}/>',
        doc.text(x0 + 14, VY + 24, "DASHBOARD", "m4", 15, p.mu, ls=0.5),
    )
    doc.style("dash", (
        ".dbar{transform-box:fill-box;transform-origin:50% 100%;animation:dbar 5s cubic-bezier(.3,0,.2,1) infinite "
        "backwards}@keyframes dbar{0%{transform:scaleY(.05)}16%,90%{transform:scaleY(1)}100%{transform:scaleY(.05)}}"
        ".dline{stroke-dasharray:260;animation:dline 5s ease-out infinite}"
        "@keyframes dline{0%{stroke-dashoffset:260}40%,90%{stroke-dashoffset:0}100%{stroke-dashoffset:260}}"))
    heights = [34, 48, 40, 60, 54, 70]
    pitch = (w - 28) / len(heights)
    bars, pts = [], []
    for i, h in enumerate(heights):
        bx = x0 + 14 + i * pitch
        bars.append(f'<rect class="dbar" x="{num(bx)}" y="{base - h}" width="{num(pitch - 10)}" height="{h}" rx="2" '
                    f'fill="{p.mu}" fill-opacity=".5" style="animation-delay:{i * 0.12:.2f}s"/>')
        pts.append((bx + (pitch - 10) / 2, base - h - 10))
    line = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in pts)
    doc.add("".join(bars), f'<path class="dline" d="{line}" fill="none" stroke="{p.cy}" stroke-width="2" '
                           'stroke-linejoin="round"/>')


LOKUM_STEPS = ["PARSE QUESTION", "RETRIEVE SOURCES", "REASON IN STEPS", "ANSWER + CITE"]


def _lokum(doc: Doc) -> None:
    p = doc.pal
    cycle, step = 8, 1.5
    pitch, y0 = 29, VY + 20
    docs_x = VX + 384
    for i, label in enumerate(LOKUM_STEPS):
        y = y0 + i * pitch
        start = (0.3 + i * step) / cycle * 100
        doc.style(f"st{i}", step_keyframes(f"st{i}", [(0, "opacity:.3"), (start, "opacity:1"), (92, "opacity:.3")])
                  + f".st{i}{{animation:st{i} {cycle}s linear infinite}}"
                  + step_keyframes(f"cur{i}", [(0, "opacity:0"), (start, "opacity:1"), (start + step / cycle * 100,
                                                                                            "opacity:0")])
                  + f".cur{i}{{opacity:0;animation:cur{i} {cycle}s linear infinite}}")
        check = f"M{VX + 4} {y - 5}l3.5 3.5 6.5-7"
        chips = _cite_chips(doc, VX + 40 + doc.tw(label, "m4", 16) + 12, y) if i in (1, 3) else ""
        doc.add(
            f'<g class="st{i}"><circle cx="{VX + 8}" cy="{y - 5}" r="8" fill="none" stroke="{p.mu}" stroke-width="1.4"/>'
            f'<path d="{check}" fill="none" stroke="{p.tx}" stroke-width="1.8" stroke-linecap="round"/>'
            f'{doc.text(VX + 28, y, label, "m4", 16, p.tx)}{chips}</g>',
            f'<circle class="cur{i}" cx="{VX + 8}" cy="{y - 5}" r="8" fill="{p.cy}" fill-opacity=".2" stroke="{p.cy}" '
            f'stroke-width="1.8"{doc.glow(2.5)}/>',
        )
    _source_docs(doc, docs_x)


def _cite_chips(doc: Doc, x: float, y: float) -> str:
    p = doc.pal
    out = []
    for n in ("1", "2"):
        out.append(f'<rect x="{num(x)}" y="{y - 16}" width="30" height="21" rx="4" fill="{p.cy}" fill-opacity=".12" '
                   f'stroke="{p.cy}" stroke-opacity=".7"/>' + doc.text(x + 15, y, f"[{n}]", "m4", 14, p.cy, "middle"))
        x += 36
    return "".join(out)


def _source_docs(doc: Doc, x: float) -> None:
    p = doc.pal
    w = VX + VW - x
    doc.style("cite", ".hl{animation:hl 8s linear infinite}@keyframes hl{0%,22%{opacity:.25}26%,92%{opacity:1}"
                      "96%,100%{opacity:.25}}")
    for i in range(2):
        y = VY + 6 + i * 60
        lines = "".join(f'<rect x="{num(x + 48)}" y="{y + 12 + k * 11}" width="{num((w - 62) * f)}" height="4" '
                        f'rx="2" fill="{p.mu}" fill-opacity=".55"/>' for k, f in enumerate([1, 0.8, 0.9]))
        doc.add(
            f'<rect x="{num(x)}" y="{y}" width="{num(w)}" height="52" rx="5" {doc.panel(2.5)}/>',
            doc.text(x + 12, y + 31, f"[{i + 1}]", "m7", 15, p.cy),
            lines,
            f'<rect class="hl" x="{num(x + 46)}" y="{y + 20}" width="{num((w - 58) * 0.8)}" height="8" rx="2" '
            f'fill="{p.cy}" fill-opacity=".25" stroke="{p.cy}" stroke-opacity=".6"/>',
        )


def _seat_map(doc: Doc) -> None:
    p = doc.pal
    rnd = random.Random(21)
    cols, rows, pitch_x, pitch_y = 10, 3, 52, 27
    x0, y0 = VX + 14, VY + 42
    doc.add(
        f'<rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="6" fill="none" {doc.hair()} stroke-dasharray="5 5"/>',
        f'<rect x="{VX + VW / 2 - 56}" y="{VY + 8}" width="112" height="22" rx="4" {doc.panel(3)}/>',
        doc.text(VX + VW / 2, VY + 24, "PROCTOR", "m4", 15, p.mu, "middle", 1),
        doc.text(VX + VW - 12, VY + 24, "1,000+ students", "m4", 15, p.mu, "end"),
    )
    _legend(doc, VX + 12, VY + 24, [("LIVE", p.cy), ("IDLE", p.faint), ("FLAG", p.am)])
    doc.style("seat", ".live{animation:live 3s ease-in-out infinite}@keyframes live{50%{opacity:.4}}")
    flagged = (6, 1)
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * pitch_x, y0 + r * pitch_y
            doc.add(f'<rect x="{x}" y="{y}" width="38" height="19" rx="3" fill="none" {doc.hair(1.2)}/>')
            dot = (x + 28, y + 9.5)
            if (c, r) == flagged:
                doc.add(f'<circle class="blink" cx="{dot[0]}" cy="{dot[1]}" r="4.2" fill="{p.am}"{doc.glow(3)}/>')
            elif rnd.random() < 0.8:
                doc.add(f'<circle class="live" cx="{dot[0]}" cy="{dot[1]}" r="3.8" fill="{p.cy}" '
                        f'style="animation-delay:{-rnd.uniform(0, 3):.2f}s"/>')
            else:
                doc.add(f'<circle cx="{dot[0]}" cy="{dot[1]}" r="3.8" fill="{p.faint}"/>')


VISUALS: dict[str, Callable[[Doc], None]] = {
    "relay-fleet-telemetry": _relay,
    "ai-agent-hmi-workflow": _agent_loop,
    "plant-data-reliability": _spc,
    "fabrik": _fabrik,
    "job-automation-suite": _job_pipeline,
    "linesight": _linesight,
    "lokumai": _lokum,
    "academic-test-facility": _seat_map,
}
