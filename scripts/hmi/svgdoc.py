"""Shared SVG plumbing: palettes, measured text, and embedded subset fonts."""

from __future__ import annotations

import base64
import io
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

# key -> (file, css weight, generic fallback)
FONTS = {
    "i4": ("Inter-Regular.ttf", 400, "sans"),
    "i6": ("Inter-SemiBold.ttf", 600, "sans"),
    "id": ("InterDisplay-ExtraBold.ttf", 800, "sans"),
    "m4": ("JetBrainsMono-Regular.ttf", 400, "mono"),
    "m7": ("JetBrainsMono-Bold.ttf", 700, "mono"),
}
FALLBACKS = {
    "sans": "Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
    "mono": "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace",
}
REDUCED_MOTION_CSS = (
    "@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}"
)


@dataclass(frozen=True)
class Palette:
    name: str
    page: str
    tx: str
    mu: str
    dim: str
    faint: str
    hair: str
    hair_op: float
    panel: str
    panel_op: float
    am: str
    cy: str
    rd: str
    gn: str
    glow: bool


DARK = Palette(
    name="dark", page="#0D1117", tx="#E6EDF3", mu="#8B949E", dim="#6E7681", faint="#484F58",
    hair="#8B949E", hair_op=0.32, panel="#C9D1D9", panel_op=0.035,
    am="#FFB627", cy="#4CC9F0", rd="#F85149", gn="#3FB950", glow=True,
)
LIGHT = Palette(
    name="light", page="#FFFFFF", tx="#1F2328", mu="#59636E", dim="#818B98", faint="#AFB8C1",
    hair="#59636E", hair_op=0.28, panel="#1F2328", panel_op=0.03,
    am="#9A6700", cy="#0A7AA8", rd="#CF222E", gn="#1A7F37", glow=False,
)
PALETTES = (DARK, LIGHT)


def num(v: float) -> str:
    """Compact number formatting for coordinates."""
    r = round(v, 1)
    return str(int(r)) if r == int(r) else f"{r:g}"


class FontBook:
    """Loads source TTFs once; measures advance widths and emits WOFF2 subsets."""

    def __init__(self, fonts_dir: Path) -> None:
        self._dir = fonts_dir
        self._fonts = {k: TTFont(fonts_dir / f) for k, (f, _, _) in FONTS.items()}
        self._cmaps = {k: f.getBestCmap() for k, f in self._fonts.items()}
        self._cache: dict[tuple[str, str], str] = {}

    def has(self, key: str, ch: str) -> bool:
        return ord(ch) in self._cmaps[key]

    def width(self, key: str, s: str, size: float, ls: float = 0.0) -> float:
        font = self._fonts[key]
        hmtx, cmap = font["hmtx"], self._cmaps[key]
        units = sum(hmtx[cmap[ord(c)]][0] for c in s)
        return units * size / font["head"].unitsPerEm + ls * max(len(s) - 1, 0)

    def woff2_b64(self, key: str, chars: set[str]) -> str:
        text = "".join(sorted(chars))
        if (key, text) not in self._cache:
            self._cache[(key, text)] = self._subset(key, text)
        return self._cache[(key, text)]

    def _subset(self, key: str, text: str) -> str:
        font = TTFont(self._dir / FONTS[key][0], recalcTimestamp=False)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.hinting = False
        opts.desubroutinize = True
        sub = subset.Subsetter(opts)
        sub.populate(text=text)
        sub.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        return base64.b64encode(buf.getvalue()).decode("ascii")


class Doc:
    """One SVG document: collects body, defs, css, and the glyphs each font needs."""

    def __init__(self, book: FontBook, pal: Palette, size: tuple[int, int], label: tuple[str, str]) -> None:
        self.book, self.pal = book, pal
        self.w, self.h = size
        self.title, self.desc = label
        self.body: list[str] = []
        self.defs: dict[str, str] = {}
        self.css: dict[str, str] = {}
        self.used: dict[str, set[str]] = defaultdict(set)

    def add(self, *parts: str) -> None:
        self.body.extend(parts)

    def define(self, key: str, markup: str) -> None:
        self.defs.setdefault(key, markup)

    def style(self, key: str, css: str) -> None:
        self.css.setdefault(key, css)

    def text(self, x: float, y: float, s: str, font: str = "m4", size: float = 16,
             fill: str | None = None, anchor: str = "start", ls: float = 0, extra: str = "") -> str:
        missing = sorted({c for c in s if not self.book.has(font, c)})
        if missing:
            raise ValueError(f"font {font} lacks glyphs {missing!r} in {s!r}")
        self.used[font].update(s)
        attrs = f' text-anchor="{anchor}"' if anchor != "start" else ""
        attrs += f' letter-spacing="{num(ls)}"' if ls else ""
        return (f'<text x="{num(x)}" y="{num(y)}" class="{font}" font-size="{num(size)}" '
                f'fill="{fill or self.pal.tx}"{attrs}{extra}>{escape(s)}</text>')

    def tw(self, s: str, font: str = "m4", size: float = 16, ls: float = 0) -> float:
        return self.book.width(font, s, size, ls)

    def hair(self, op_scale: float = 1.0) -> str:
        return f'stroke="{self.pal.hair}" stroke-opacity="{self.pal.hair_op * op_scale:.3g}"'

    def panel(self, op_scale: float = 1.0) -> str:
        return f'fill="{self.pal.panel}" fill-opacity="{self.pal.panel_op * op_scale:.3g}" {self.hair()}'

    def glow(self, strength: float = 3.0) -> str:
        if not self.pal.glow:
            return ""
        fid = f"glow{num(strength).replace('.', '_')}"
        self.define(fid, (
            f'<filter id="{fid}" x="-100%" y="-100%" width="300%" height="300%">'
            f'<feGaussianBlur stdDeviation="{num(strength)}" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'))
        return f' filter="url(#{fid})"'

    def render(self) -> str:
        style = self._font_css() + "".join(self.css.values()) + REDUCED_MOTION_CSS
        defs = f"<defs>{''.join(self.defs.values())}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(self.title)}</title><desc id="d">{escape(self.desc)}</desc>'
            f"<style>{style}</style>{defs}{''.join(self.body)}</svg>\n"
        )

    def _font_css(self) -> str:
        out = []
        for key in sorted(self.used):
            _, weight, generic = FONTS[key]
            b64 = self.book.woff2_b64(key, self.used[key])
            out.append(
                f'@font-face{{font-family:"ag-{key}";font-weight:{weight};'
                f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}'
                f'.{key}{{font-family:"ag-{key}",{FALLBACKS[generic]};font-weight:{weight}}}'
            )
        return "".join(out)


def step_keyframes(name: str, stops: list[tuple[float, str]]) -> str:
    """Hard-step keyframes: each (percent, declarations) holds until the next stop."""
    frames = []
    for i, (pct, decl) in enumerate(stops):
        end = stops[i + 1][0] - 0.01 if i + 1 < len(stops) else 100
        frames.append(f"{num_pct(pct)}%,{num_pct(end)}%{{{decl}}}")
    return f"@keyframes {name}{{{''.join(frames)}}}"


def num_pct(v: float) -> str:
    return f"{round(v, 2):g}"
