"""Hero banner: photo, name, and role on the left; an animated one-line diagram on the right."""

from __future__ import annotations

import base64
import io
import math
import random
from functools import lru_cache
from pathlib import Path

from .svgdoc import Doc, num, step_keyframes

W, H = 1200, 440
CYCLE_S = 12
TRIP, ACK, RESTORE, CLEAR = 25, 50, 80, 94  # percent of the cycle
COL_X, COL_W = 40, 540
PANEL = (620, 28, 1176, 416)
AVATAR_SRC = Path(__file__).resolve().parents[2] / "assets" / "src" / "avatar.jpg"
AVATAR_PX, AVATAR_QUALITY = 176, 82  # about 2x the displayed size
AV_CX, AV_CY, AV_R, RING_R = COL_X + 44, 78, 44, 51
NAME_Y, ROLE_Y, TAGLINE_Y = 226, 274, 310
TREND_LABEL_Y, TREND_BOTTOM, TREND_STEP = 366, 416, 6
SX = 895  # source column x
FEEDERS = [730, 840, 950, 1060]
TRIP_FEEDER = 2  # index of FDR 3
UTIL_CY, MAIN_Y, XF_CY = 112, 144, (192, 210)
BUS_Y, BRK_Y, LOAD_Y, LABEL_Y = 246, 282, 338, 380
NAME, ROLE = "AARON GUO", "Software Automation Controls Engineer"
TAGLINE = "telemetry · operator HMIs · alarms · plant data"
CHIPS = [("cy", "SpaceXAI · full-time Oct 2026"), ("mu", "GWU CS '26"), ("gn", "Fabrik · in production")]


def build(doc: Doc) -> None:
    _styles(doc)
    _avatar(doc)
    _chips(doc, AV_CX + RING_R + 17, AV_CY)
    _identity(doc)
    _trend(doc)
    _panel(doc)


def _styles(doc: Doc) -> None:
    windows = {
        "w-norm": [(0, "opacity:1"), (TRIP, "opacity:0"), (RESTORE, "opacity:1")],
        "w-dead": [(0, "opacity:0"), (TRIP, "opacity:1"), (RESTORE, "opacity:0")],
        "w-trip": [(0, "opacity:0"), (TRIP, "opacity:1"), (ACK, "opacity:0")],
        "w-ack": [(0, "opacity:0"), (ACK, "opacity:1"), (RESTORE, "opacity:0")],
        "w-rst": [(0, "opacity:0"), (RESTORE, "opacity:1"), (CLEAR, "opacity:0")],
    }
    css = []
    for name, stops in windows.items():
        css.append(step_keyframes(name, stops))
        css.append(f".{name}{{{stops[0][1]};animation:{name} {CYCLE_S}s linear infinite}}")
    css.append(
        ".blink{animation:blink .5s steps(1) infinite}@keyframes blink{50%{opacity:.18}}"
        ".flow{stroke-dasharray:6 10;animation:flow .8s linear infinite}"
        "@keyframes flow{to{stroke-dashoffset:-16}}"
        ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.3}}"
        ".spin{transform-box:view-box;transform-origin:"
        f"{AV_CX}px {AV_CY}px;animation:spin 9s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
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


@lru_cache(maxsize=1)
def _avatar_b64() -> str:
    from PIL import Image  # only the hero needs Pillow

    with Image.open(AVATAR_SRC) as src:
        img = src.convert("RGB").resize((AVATAR_PX, AVATAR_PX), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=AVATAR_QUALITY, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _avatar(doc: Doc) -> None:
    p = doc.pal
    x, y, d = AV_CX - AV_R, AV_CY - AV_R, 2 * AV_R
    circ = 2 * math.pi * RING_R
    dash = f"{num(circ * 0.25)} {num(circ * 0.2)} {num(circ * 0.025)} {num(circ * 0.525)}"
    arc = f'cx="{AV_CX}" cy="{AV_CY}" r="{RING_R}" fill="none" stroke="{p.cy}" stroke-dasharray="{dash}"'
    halo = f'<circle {arc} stroke-width="6" stroke-opacity=".16"/>' if p.glow else ""
    dot = (AV_CX + RING_R * math.cos(math.pi / 4), AV_CY + RING_R * math.sin(math.pi / 4))
    doc.define("avclip", f'<clipPath id="avclip"><circle cx="{AV_CX}" cy="{AV_CY}" r="{AV_R}"/></clipPath>')
    doc.add(
        f'<image x="{x}" y="{y}" width="{d}" height="{d}" preserveAspectRatio="xMidYMid slice" '
        f'clip-path="url(#avclip)" href="data:image/jpeg;base64,{_avatar_b64()}"/>',
        f'<circle cx="{AV_CX}" cy="{AV_CY}" r="{AV_R}" fill="none" {doc.hair()}/>',
        f'<circle cx="{AV_CX}" cy="{AV_CY}" r="{RING_R}" fill="none" {doc.hair()}/>',
        f'<g class="spin">{halo}<circle {arc} stroke-width="2.2" stroke-linecap="round"/></g>',
        f'<circle cx="{num(dot[0])}" cy="{num(dot[1])}" r="6.5" fill="{p.gn}" stroke="{p.page}" '
        f'stroke-width="3"/>',
    )


def _chips(doc: Doc, x0: float, cy: float) -> None:
    p = doc.pal
    gap, h = 10, 30
    rows: list[list[tuple[str, str, float]]] = [[]]
    x = x0
    for color, label in CHIPS:
        w = doc.tw(label, "m4", 16) + 38
        if rows[-1] and x + w > COL_X + COL_W:
            rows.append([])
            x = x0
        rows[-1].append((color, label, w))
        x += w + gap
    top = cy - (len(rows) * h + (len(rows) - 1) * gap) / 2
    for r, row in enumerate(rows):
        x, y = x0, top + r * (h + gap)
        for color, label, w in row:
            _chip(doc, (x, y, w, h), color, label)
            x += w + gap


def _chip(doc: Doc, box: tuple[float, float, float, float], color: str, label: str) -> None:
    p = doc.pal
    x, y, w, h = box
    led = getattr(p, color)
    pulse = ' class="pulse"' if color != "mu" else ""
    glow = doc.glow(2.5) if color != "mu" else ""
    doc.add(
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{h}" rx="4" {doc.panel(1.6)}/>',
        f'<circle{pulse} cx="{num(x + 15)}" cy="{num(y + h / 2)}" r="4" fill="{led}"{glow}/>',
        doc.text(x + 28, y + 20.5, label, "m4", 16, p.tx),
    )


def _identity(doc: Doc) -> None:
    p = doc.pal
    name_size = min(96.0, COL_W / doc.tw(NAME, "id", 1, -0.01))
    role_size = min(28.0, COL_W / doc.tw(ROLE, "i6", 1))
    doc.add(doc.text(COL_X - 3, NAME_Y, NAME, "id", round(name_size, 1), p.tx, ls=-round(name_size * 0.01, 2)))
    _role_reveal(doc, role_size)
    doc.add(doc.text(COL_X, TAGLINE_Y, TAGLINE, "m4", 16, p.mu))


def _role_reveal(doc: Doc, size: float) -> None:
    p = doc.pal
    width = doc.tw(ROLE, "i6", size)
    doc.define("roleclip", f'<clipPath id="roleclip"><rect class="reveal" x="{COL_X - 2}" y="{ROLE_Y - 30}" '
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
        f'<g clip-path="url(#roleclip)">{doc.text(COL_X, ROLE_Y, ROLE, "i6", round(size, 1), p.tx)}</g>',
        f'<rect class="caret" x="{COL_X}" y="{ROLE_Y - 22}" width="3" height="28" fill="{p.cy}"{doc.glow(2.5)}/>',
    )


def _trend_values() -> list[float]:
    rnd = random.Random(7)
    dip_on, dip_off = COL_W * TRIP / 100 - 15, COL_W * RESTORE / 100 - 15
    out = []
    for i in range(0, COL_W + 1, TREND_STEP):
        v = 0.6 + 0.07 * math.sin(i / 31) + 0.05 * math.sin(i / 11 + 1.3) + rnd.uniform(-0.035, 0.035)
        dip = _smooth((i - dip_on) / 30) * (1 - _smooth((i - dip_off) / 30))
        out.append(v * (1 - 0.45 * dip))
    out[-1] = out[0]
    return out


def _smooth(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def _trend(doc: Doc) -> None:
    p = doc.pal
    vals = _trend_values()
    pts = [(COL_X + i * TREND_STEP + k * COL_W, TREND_BOTTOM - 2 - v * 40)
           for k in range(2) for i, v in enumerate(vals)]
    line = "M" + " L".join(f"{num(x)} {num(y)}" for x, y in pts)
    area = f"{line} L{num(pts[-1][0])} {TREND_BOTTOM} L{num(pts[0][0])} {TREND_BOTTOM}Z"
    x0, x1, top = COL_X, COL_X + COL_W, TREND_LABEL_Y + 6
    doc.define("trendfade", (
        f'<linearGradient id="tfg" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".18" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff"/></linearGradient>'
        f'<mask id="tmask" maskUnits="userSpaceOnUse" x="{x0}" y="{top}" width="{COL_W}" height="{TREND_BOTTOM - top}">'
        f'<rect x="{x0}" y="{top}" width="{COL_W}" height="{TREND_BOTTOM - top}" fill="url(#tfg)"/></mask>'
        f'<linearGradient id="tarea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p.cy}" '
        f'stop-opacity=".22"/><stop offset="1" stop-color="{p.cy}" stop-opacity="0"/></linearGradient>'))
    doc.add(
        doc.text(COL_X, TREND_LABEL_Y, "BUS LOAD", "m4", 16, p.mu, ls=1),
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
    _legend(doc, x1 - 20, y0 + 80)
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
        inner += doc.text(x + (12 if box else 0), top + 18.5, label, font, 16, color, ls=0.5)
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
    trunk = (f"M{SX} {UTIL_CY + 13}V{MAIN_Y} M{SX} {MAIN_Y + 22}V{XF_CY[0] - 11} "
             f"M{SX} {XF_CY[1] + 11}V{BUS_Y}")
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
    ring = f'fill="none" stroke="{p.tx}" stroke-width="1.8"'
    doc.add(
        f'<circle cx="{SX}" cy="{UTIL_CY}" r="13" {ring}/>',
        f'<path d="M{SX - 7} {UTIL_CY}c2.4-5 4.6-5 7 0s4.6 5 7 0" fill="none" stroke="{p.tx}" stroke-width="1.6"/>',
        doc.text(lx, UTIL_CY + 5, "UTILITY", "m4", 16, p.mu, "end"),
        f'<rect x="{SX - 11}" y="{MAIN_Y}" width="22" height="22" rx="2" fill="{p.mu}"/>',
        doc.text(lx, MAIN_Y + 17, "MAIN · MV SWGR", "m4", 16, p.mu, "end"),
        f'<circle cx="{SX}" cy="{XF_CY[0]}" r="11" {ring}/>',
        f'<circle cx="{SX}" cy="{XF_CY[1]}" r="11" {ring}/>',
        doc.text(lx, sum(XF_CY) / 2 + 5, "XFMR-1", "m4", 16, p.mu, "end"),
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
            doc.text(x, LABEL_Y, label, "m4", 16, p.tx, "middle"),
        )
        return
    doc.add(
        f'<g class="w-norm"><rect {brk} fill="{p.mu}"/><path d="{load}" fill="{p.mu}"/>'
        f'{doc.text(x, LABEL_Y, label, "m4", 16, p.tx, "middle")}</g>',
        f'<g class="w-dead"><path d="{load}" fill="none" stroke="{p.faint}" stroke-width="1.5"/></g>',
        f'<rect class="halo" x="{x - 15}" y="{BRK_Y - 4}" width="30" height="30" rx="4" fill="none" '
        f'stroke="{p.rd}" stroke-width="2"/>',
        f'<g class="w-trip"><g class="blink"><rect {brk} fill="{p.rd}" fill-opacity=".2" stroke="{p.rd}" '
        f'stroke-width="2.2"{doc.glow(3)}/>{doc.text(x, LABEL_Y, label, "m7", 16, p.rd, "middle")}</g>'
        f'{doc.text(x + 18, BRK_Y + 17, "TRIP", "m7", 16, p.rd)}</g>',
        f'<g class="w-ack"><rect {brk} fill="none" stroke="{p.am}" stroke-width="2.2"/>'
        f'{doc.text(x, LABEL_Y, label, "m7", 16, p.am, "middle")}'
        f'{doc.text(x + 18, BRK_Y + 17, "ACK", "m7", 16, p.am)}</g>',
    )
