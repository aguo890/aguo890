"""Hero banner: operator identity on the left, an animated one-line HMI on the right."""

from __future__ import annotations

import math
import random

from .svgdoc import Doc, num, step_keyframes

W, H = 1200, 440
CYCLE_S = 12
TRIP, ACK, RESTORE, CLEAR = 25, 50, 80, 94  # percent of the cycle
COL_X, COL_W = 40, 540
PANEL = (620, 60, 1176, 420)
SX = 895  # source column x
FEEDERS = [730, 840, 950, 1060]
TRIP_FEEDER = 2  # index of FDR 3
BUS_Y, BRK_Y, LOAD_Y = 268, 300, 352
TREND_TOP, TREND_BOTTOM = 392, 420
NAME, ROLE = "AARON GUO", "Software Automation Controls Engineer"
TAGLINE = "telemetry · operator HMIs · alarms · plant data"
CHIPS = [("cy", "SpaceXAI · full-time Oct 2026"), ("mu", "GWU CS '26"), ("gn", "Fabrik · in production")]


def build(doc: Doc) -> None:
    _styles(doc)
    _top_bar(doc)
    _identity(doc)
    _trend(doc)
    _panel(doc)


def _styles(doc: Doc) -> None:
    windows = {
        "w-ok": [(0, "opacity:1"), (TRIP, "opacity:0"), (CLEAR, "opacity:1")],
        "w-norm": [(0, "opacity:1"), (TRIP, "opacity:0"), (RESTORE, "opacity:1")],
        "w-dead": [(0, "opacity:0"), (TRIP, "opacity:1"), (RESTORE, "opacity:0")],
        "w-trip": [(0, "opacity:0"), (TRIP, "opacity:1"), (ACK, "opacity:0")],
        "w-ack": [(0, "opacity:0"), (ACK, "opacity:1"), (RESTORE, "opacity:0")],
        "w-rst": [(0, "opacity:0"), (RESTORE, "opacity:1"), (CLEAR, "opacity:0")],
    }
    css = []
    for name, stops in windows.items():
        base = stops[0][1]
        css.append(step_keyframes(name, stops))
        css.append(f".{name}{{{base};animation:{name} {CYCLE_S}s linear infinite}}")
    css.append(
        ".blink{animation:blink .5s steps(1) infinite}@keyframes blink{50%{opacity:.18}}"
        ".flow{stroke-dasharray:6 10;animation:flow .8s linear infinite}"
        "@keyframes flow{to{stroke-dashoffset:-16}}"
        ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}"
        ".halo{opacity:0;transform-box:fill-box;transform-origin:center;"
        f"animation:halo {CYCLE_S}s ease-out infinite}}"
        f"@keyframes halo{{0%,{TRIP - 0.01}%{{opacity:0;transform:scale(.6)}}"
        f"{TRIP}%{{opacity:.9;transform:scale(.6)}}{TRIP + 9}%,100%{{opacity:0;transform:scale(2.8)}}}}"
        ".scan{animation:scan 7s linear infinite}"
        f"@keyframes scan{{to{{transform:translateY({PANEL[3] - PANEL[1] + 60}px)}}}}"
        f".trend{{animation:trend {CYCLE_S}s linear infinite}}"
        f"@keyframes trend{{to{{transform:translateX(-{COL_W}px)}}}}"
    )
    doc.style("hero", "".join(css))


def _top_bar(doc: Doc) -> None:
    p = doc.pal
    left = COL_X - 12
    doc.add(
        f'<rect x="{left}" y="18" width="11" height="11" transform="rotate(45 {left + 5.5} 23.5)" '
        f'fill="none" stroke="{p.cy}" stroke-width="1.6"/>',
        doc.text(left + 22, 29, "AG-HMI", "m7", 16, p.tx, ls=2),
        doc.text(left + 22 + doc.tw("AG-HMI", "m7", 16, 2) + 16, 29, "/  OPERATOR PROFILE", "m4", 16, p.mu, ls=1),
    )
    right = PANEL[2]
    online_w = doc.tw("ONLINE", "m7", 16, 1.5)
    led_x = right - online_w - 14
    sys_x = led_x - 12
    doc.add(
        doc.text(right, 29, "ONLINE", "m7", 16, p.tx, "end", 1.5),
        f'<circle class="pulse" cx="{num(led_x)}" cy="23.5" r="4.5" fill="{p.gn}"{doc.glow(3)}/>',
        doc.text(sys_x, 29, "SYS", "m4", 16, p.mu, "end", 1.5),
    )
    _alarm_counter(doc, sys_x - doc.tw("SYS", "m4", 16, 1.5) - 22)
    doc.add(_fade_line(doc, "topline", 0, W, 46))


def _alarm_counter(doc: Doc, right: float) -> None:
    p = doc.pal
    w = doc.tw("ALM 0", "m7", 16, 1) + 22
    x = right - w
    box = f'<rect x="{num(x)}" y="11" width="{num(w)}" height="25" rx="3" '
    mid = x + w / 2
    doc.add(
        f'<g class="w-ok">{box}fill="none" {doc.hair()}/>'
        f'{doc.text(mid, 29, "ALM 0", "m7", 16, p.mu, "middle", 1)}</g>',
        f'<g class="w-trip"><g class="blink">{box}fill="{p.rd}" fill-opacity=".16" stroke="{p.rd}"/>'
        f'{doc.text(mid, 29, "ALM 1", "m7", 16, p.rd, "middle", 1)}</g></g>',
        f'<g class="w-ack">{box}fill="{p.am}" fill-opacity=".12" stroke="{p.am}"/>'
        f'{doc.text(mid, 29, "ALM 1", "m7", 16, p.am, "middle", 1)}</g>',
        f'<g class="w-rst">{box}fill="none" {doc.hair()}/>'
        f'{doc.text(mid, 29, "ALM 0", "m7", 16, p.mu, "middle", 1)}</g>',
    )


def _fade_line(doc: Doc, gid: str, x0: float, x1: float, y: float) -> str:
    p = doc.pal
    doc.define(gid, (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">'
        f'<stop offset="0" stop-color="{p.hair}" stop-opacity="0"/>'
        f'<stop offset=".08" stop-color="{p.hair}" stop-opacity="{p.hair_op}"/>'
        f'<stop offset=".92" stop-color="{p.hair}" stop-opacity="{p.hair_op}"/>'
        f'<stop offset="1" stop-color="{p.hair}" stop-opacity="0"/></linearGradient>'))
    return f'<path d="M{num(x0)} {num(y)}H{num(x1)}" stroke="url(#{gid})" stroke-width="1"/>'


def _identity(doc: Doc) -> None:
    p = doc.pal
    name_size = min(96.0, COL_W / doc.tw(NAME, "id", 1, -0.01))
    role_size = min(28.0, COL_W / doc.tw(ROLE, "i6", 1))
    doc.add(
        f'<rect x="{COL_X}" y="76" width="3" height="16" fill="{p.am}"/>',
        doc.text(COL_X + 12, 90, "OPERATOR  ·  CONTROLS + SOFTWARE", "m4", 16, p.mu, ls=2),
        doc.text(COL_X - 3, 172, NAME, "id", round(name_size, 1), p.tx, ls=-round(name_size * 0.01, 2)),
    )
    _role_reveal(doc, role_size)
    doc.add(doc.text(COL_X, 252, TAGLINE, "m4", 16, p.mu))
    _chips(doc, 274)


def _role_reveal(doc: Doc, size: float) -> None:
    p = doc.pal
    width = doc.tw(ROLE, "i6", size)
    doc.define("roleclip", f'<clipPath id="roleclip"><rect class="reveal" x="{COL_X - 2}" y="190" '
                           f'width="{num(width + 8)}" height="40"/></clipPath>')
    doc.style("reveal", (
        ".reveal{transform-box:fill-box;transform-origin:0 0;"
        "animation:reveal 1.6s cubic-bezier(.6,0,.2,1) .3s both}"
        "@keyframes reveal{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        f".caret{{transform:translateX({num(width + 6)}px);"
        "animation:caret 1.6s cubic-bezier(.6,0,.2,1) .3s both,cblink 1.1s steps(1) 2s infinite}"
        f"@keyframes caret{{from{{transform:translateX(0)}}to{{transform:translateX({num(width + 6)}px)}}}}"
        "@keyframes cblink{50%{opacity:0}}"))
    doc.add(
        f'<g clip-path="url(#roleclip)">{doc.text(COL_X, 220, ROLE, "i6", round(size, 1), p.tx)}</g>',
        f'<rect class="caret" x="{COL_X}" y="198" width="3" height="28" fill="{p.cy}"{doc.glow(2.5)}/>',
    )


def _chips(doc: Doc, top: float) -> None:
    p = doc.pal
    x, y, gap, h = COL_X, top, 10, 30
    for color, label in CHIPS:
        w = doc.tw(label, "m4", 16) + 38
        if x + w > COL_X + COL_W:
            x, y = COL_X, y + h + gap
        led = getattr(p, color)
        pulse = ' class="pulse"' if color != "mu" else ""
        glow = doc.glow(2.5) if color != "mu" else ""
        doc.add(
            f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{h}" rx="4" {doc.panel(1.6)}/>',
            f'<circle{pulse} cx="{num(x + 15)}" cy="{num(y + h / 2)}" r="4" fill="{led}"{glow}/>',
            doc.text(x + 28, y + 20.5, label, "m4", 16, p.tx),
        )
        x += w + gap


def _trend_values() -> list[float]:
    rnd = random.Random(7)
    out = []
    for i in range(0, COL_W + 1, 6):
        v = 0.6 + 0.07 * math.sin(i / 31) + 0.05 * math.sin(i / 11 + 1.3) + rnd.uniform(-0.035, 0.035)
        dip = _smooth((i - 120) / 30) * (1 - _smooth((i - 420) / 30))
        out.append(v * (1 - 0.45 * dip))
    out[-1] = out[0]
    return out


def _smooth(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def _trend(doc: Doc) -> None:
    p = doc.pal
    vals = _trend_values()
    pts = [(COL_X + i * 6 + k * COL_W, TREND_BOTTOM - 2 - v * 40) for k in range(2) for i, v in enumerate(vals)]
    line = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in pts)
    area = f"{line} L{num(pts[-1][0])} {TREND_BOTTOM} L{num(pts[0][0])} {TREND_BOTTOM}Z"
    x0, x1 = COL_X, COL_X + COL_W
    doc.define("trendfade", (
        f'<linearGradient id="tfg" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".18" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff"/></linearGradient>'
        f'<mask id="tmask" maskUnits="userSpaceOnUse" x="{x0}" y="{TREND_TOP - 20}" width="{COL_W}" height="60">'
        f'<rect x="{x0}" y="{TREND_TOP - 20}" width="{COL_W}" height="60" fill="url(#tfg)"/></mask>'
        f'<linearGradient id="tarea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p.cy}" '
        f'stop-opacity=".22"/><stop offset="1" stop-color="{p.cy}" stop-opacity="0"/></linearGradient>'))
    doc.add(
        doc.text(COL_X, 378, "TREND  ·  BUS LOAD", "m4", 16, p.mu, ls=1),
        f'<circle class="pulse" cx="{num(x1 - doc.tw("LIVE", "m4", 16, 1) - 12)}" cy="372.5" r="3.5" '
        f'fill="{p.cy}"{doc.glow(2.5)}/>',
        doc.text(x1, 378, "LIVE", "m4", 16, p.mu, "end", 1),
        f'<path d="M{x0} {TREND_BOTTOM}H{x1}" {doc.hair()}/>',
        f'<g mask="url(#tmask)"><g class="trend"><path d="{area}" fill="url(#tarea)"/>'
        f'<path d="{line}" fill="none" stroke="{p.cy}" stroke-width="1.8" stroke-linejoin="round"/></g></g>',
    )


def _panel(doc: Doc) -> None:
    x0, y0, x1, y1 = PANEL
    p = doc.pal
    w, h = x1 - x0, y1 - y0
    doc.define("grid", (
        f'<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse" x="{x0}" y="{y0}">'
        f'<circle cx="10" cy="10" r=".9" fill="{p.mu}" fill-opacity=".28"/></pattern>'
        f'<clipPath id="pclip"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4"/></clipPath>'
        f'<linearGradient id="scang" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p.cy}" '
        f'stop-opacity="0"/><stop offset=".9" stop-color="{p.cy}" stop-opacity="{".05" if p.glow else ".03"}"/>'
        f'<stop offset="1" stop-color="{p.cy}" stop-opacity="0"/></linearGradient>'))
    doc.add(
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" {doc.panel()}/>',
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" fill="url(#grid)"/>',
        f'<g clip-path="url(#pclip)"><rect class="scan" x="{x0}" y="{y0 - 60}" width="{w}" height="60" '
        f'fill="url(#scang)"/></g>',
        _corner_brackets(doc, x0, y0, x1, y1),
        f'<g class="w-trip"><g class="blink"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" '
        f'fill="{p.rd}" fill-opacity=".035" stroke="{p.rd}" stroke-opacity=".7" stroke-width="1.5"/></g></g>',
        doc.text(x0 + 20, y0 + 30, "ONE-LINE  ·  LV DISTRIBUTION", "m4", 16, p.mu, ls=1),
        f'<path d="M{x0 + 16} {y0 + 46}H{x1 - 16}" {doc.hair()}/>',
    )
    _alarm_banner(doc, x1 - 18, y0 + 11)
    _legend(doc, x1 - 20, y0 + 76)
    _one_line(doc)


def _corner_brackets(doc: Doc, x0: float, y0: float, x1: float, y1: float) -> str:
    s, c = 14, doc.pal.mu
    paths = (f"M{x0} {y0 + s}V{y0}H{x0 + s} M{x1 - s} {y0}H{x1}V{y0 + s} "
             f"M{x1} {y1 - s}V{y1}H{x1 - s} M{x0 + s} {y1}H{x0}V{y1 - s}")
    return f'<path d="{paths}" fill="none" stroke="{c}" stroke-width="1.6" stroke-opacity=".8"/>'


def _alarm_banner(doc: Doc, right: float, top: float) -> None:
    p = doc.pal
    h = 26
    states = [
        ("w-ok", "●  NO ACTIVE ALARMS", "m4", p.mu, None),
        ("w-trip", "▲  FDR 3 TRIP", "m7", p.rd, p.rd),
        ("w-ack", "■  FDR 3 TRIP · ACK", "m7", p.am, p.am),
        ("w-rst", "✓  FDR 3 RESTORED", "m4", p.gn, None),
    ]
    for cls, label, font, color, box in states:
        tw = doc.tw(label, font, 16, 0.5)
        x = right - tw - (24 if box else 0)
        inner = ""
        if box:
            inner = (f'<rect x="{num(x)}" y="{top}" width="{num(tw + 24)}" height="{h}" rx="3" fill="{box}" '
                     f'fill-opacity=".14" stroke="{box}"/>')
        tx = x + (12 if box else 0)
        inner += doc.text(tx, top + 18.5, label, font, 16, color, ls=0.5)
        wrapped = f'<g class="blink">{inner}</g>' if cls == "w-trip" else inner
        doc.add(f'<g class="{cls}">{wrapped}</g>')


def _legend(doc: Doc, right: float, top: float) -> None:
    p = doc.pal
    rows = [("ENERGIZED", p.cy, True), ("DE-ENERGIZED", p.faint, False)]
    for i, (label, color, dashed) in enumerate(rows):
        y = top + i * 24
        tx = right - doc.tw(label, "m4", 16)
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        doc.add(
            f'<path d="M{num(tx - 40)} {num(y - 5)}h28" stroke="{color}" stroke-width="2"{dash}/>',
            doc.text(right, y, label, "m4", 16, p.mu, "end"),
        )


def _one_line(doc: Doc) -> None:
    p = doc.pal
    cond = f'stroke="{p.dim}" stroke-width="2" fill="none"'
    trunk = f"M{SX} 153V170 M{SX} 192V206 M{SX} 246V{BUS_Y}"
    feeders_up = " ".join(f"M{x} {BUS_Y}V{BRK_Y}" for x in FEEDERS)
    feeders_dn = [f"M{x} {BRK_Y + 22}V{LOAD_Y}" for x in FEEDERS]
    doc.add(
        f'<path d="{trunk} {feeders_up} {" ".join(feeders_dn)}" {cond}/>',
        f'<path d="M{FEEDERS[0] - 40} {BUS_Y}H{FEEDERS[-1] + 40}" stroke="{p.tx}" stroke-opacity=".75" '
        'stroke-width="4" stroke-linecap="round"/>',
        doc.text(FEEDERS[0] - 40, BUS_Y - 12, "LV BUS", "m4", 16, p.mu),
    )
    live_dn = " ".join(d for i, d in enumerate(feeders_dn) if i != TRIP_FEEDER)
    bus = f"M{SX} {BUS_Y}H{FEEDERS[0] - 40} M{SX} {BUS_Y}H{FEEDERS[-1] + 40}"
    _flow(doc, f"{trunk} {bus} {feeders_up} {live_dn}", "")
    _flow(doc, feeders_dn[TRIP_FEEDER], "w-norm")
    _source_column(doc)
    for i, x in enumerate(FEEDERS):
        _feeder(doc, i, x)


def _flow(doc: Doc, d: str, cls: str) -> None:
    p = doc.pal
    under = (f'<path d="{d}" stroke="{p.cy}" stroke-opacity=".16" stroke-width="7" fill="none" '
             'stroke-linecap="round"/>') if p.glow else ""
    flow = f'<path class="flow" d="{d}" stroke="{p.cy}" stroke-width="2.2" fill="none"/>'
    doc.add(f'<g class="{cls}">{under}{flow}</g>' if cls else under + flow)


def _source_column(doc: Doc) -> None:
    p = doc.pal
    lx = SX - 26
    doc.add(
        f'<circle cx="{SX}" cy="140" r="13" fill="none" stroke="{p.tx}" stroke-width="1.8"/>',
        f'<path d="M{SX - 7} 140c2.4-5 4.6-5 7 0s4.6 5 7 0" fill="none" stroke="{p.tx}" stroke-width="1.6"/>',
        doc.text(lx, 145, "UTILITY", "m4", 16, p.mu, "end"),
        f'<rect x="{SX - 11}" y="170" width="22" height="22" rx="2" fill="{p.mu}"/>',
        doc.text(lx, 187, "MAIN · MV SWGR", "m4", 16, p.mu, "end"),
        f'<circle cx="{SX}" cy="217" r="11" fill="none" stroke="{p.tx}" stroke-width="1.8"/>',
        f'<circle cx="{SX}" cy="235" r="11" fill="none" stroke="{p.tx}" stroke-width="1.8"/>',
        doc.text(lx, 231, "XFMR-1", "m4", 16, p.mu, "end"),
    )


def _feeder(doc: Doc, i: int, x: float) -> None:
    p = doc.pal
    label = f"FDR {i + 1}"
    brk = f'x="{x - 11}" y="{BRK_Y}" width="22" height="22" rx="2"'
    load = f"M{x - 8} {LOAD_Y}H{x + 8}L{x} {LOAD_Y + 14}Z"
    if i != TRIP_FEEDER:
        doc.add(
            f'<rect {brk} fill="{p.mu}"/>',
            f'<path d="{load}" fill="{p.mu}"/>',
            doc.text(x, 392, label, "m4", 16, p.tx, "middle"),
        )
        return
    doc.add(
        f'<g class="w-norm"><rect {brk} fill="{p.mu}"/><path d="{load}" fill="{p.mu}"/>'
        f'{doc.text(x, 392, label, "m4", 16, p.tx, "middle")}</g>',
        f'<g class="w-dead"><path d="{load}" fill="none" stroke="{p.faint}" stroke-width="1.5"/></g>',
        f'<rect class="halo" x="{x - 15}" y="{BRK_Y - 4}" width="30" height="30" rx="4" fill="none" '
        f'stroke="{p.rd}" stroke-width="2"/>',
        f'<g class="w-trip"><g class="blink"><rect {brk} fill="{p.rd}" fill-opacity=".2" stroke="{p.rd}" '
        f'stroke-width="2.2"{doc.glow(3)}/>{doc.text(x, 392, label, "m7", 16, p.rd, "middle")}</g>'
        f'{doc.text(x + 18, BRK_Y + 17, "TRIP", "m7", 16, p.rd)}</g>',
        f'<g class="w-ack"><rect {brk} fill="none" stroke="{p.am}" stroke-width="2.2"/>'
        f'{doc.text(x, 392, label, "m7", 16, p.am, "middle")}'
        f'{doc.text(x + 18, BRK_Y + 17, "ACK", "m7", 16, p.am)}</g>',
    )
