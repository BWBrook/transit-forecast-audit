"""Graphical abstract for the reconstruction brief and article.

Reads the saved per-planet comparison table (Table 3) and the PIT/percentile
summary; writes SVG, PDF (rsvg-convert) and PNG to results/reconstruction_displays/.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/reconstruction_displays"
TABLE = OUT / "table3_planets.csv"
PIT = OUT / "pit_table2.json"

W, H = 1000, 612
FONT = "'Avenir Next', 'Helvetica Neue', Arial, sans-serif"
INK, INK2, MUTED, RULE = "#1f2328", "#4b535c", "#7a828b", "#d0d5da"
BLUE, VERM, BAND, TINT = "#0072B2", "#D55E00", "#eef1f4", "#e6f1f8"

X0, X1 = 70, 950
LO, HI = math.log10(0.25), math.log10(900)


def x(minutes):
    return X0 + (math.log10(minutes) - LO) / (HI - LO) * (X1 - X0)


def text(xp, yp, s, size=13, weight=400, fill=INK, anchor="start", style=""):
    return (f'<text x="{xp:.1f}" y="{yp:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{style}>{s}</text>')


def swarm(values, y0, r, gap=1.0):
    placed, out = [], []
    for v in sorted(values):
        px = x(v)
        for k in range(200):
            dy = (k + 1) // 2 * (2 * r + gap) * (1 if k % 2 else -1) * 0.5
            py = y0 + dy
            if all((px - qx) ** 2 + (py - qy) ** 2 >= (2 * r + gap) ** 2 for qx, qy in placed):
                break
        placed.append((px, py))
        out.append((px, py))
    return out


def icon(kind, cx, cy):
    s = f'stroke="{BLUE}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "clock":
        return (f'<circle cx="{cx}" cy="{cy}" r="10" {s}/>'
                f'<path d="M{cx} {cy-6} V{cy} L{cx+5} {cy+3}" {s}/>')
    if kind == "lock":
        return (f'<rect x="{cx-9}" y="{cy-2}" width="18" height="13" rx="2" {s}/>'
                f'<path d="M{cx-5} {cy-2} V{cy-7} a5 5 0 0 1 10 0 V{cy-2}" {s}/>')
    if kind == "dip":
        return f'<path d="M{cx-13} {cy-5} H{cx-6} L{cx-3} {cy+6} H{cx+3} L{cx+6} {cy-5} H{cx+13}" {s}/>'
    return (f'<circle cx="{cx}" cy="{cy}" r="10" {s}/><circle cx="{cx}" cy="{cy}" r="5" {s}/>'
            f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="{BLUE}"/>')


def main():
    rows = [r for r in csv.DictReader(open(TABLE)) if r["max_abs_error_min"]]
    worst = {r["planet"]: float(r["max_abs_error_min"]) for r in rows}
    hr = worst.pop("HR858b")
    others = list(worst.values())
    pit = json.loads(PIT.read_text())
    median = pit["abs_error_min"]["pooled"]["p50"]
    cov = pit["pit_coverage95_check"]["M0"]
    n_events, n_planets = pit["events"], pit["planets"]
    assert n_planets == len(others) + 1 == 151 and n_events == 2185
    assert max(others) < 26.4 and 355 < hr < 410

    e = []
    e.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    e.append(text(40, 46, "How well did published planet-transit predictions hold up?", 28, 600))
    e.append(text(40, 74, f"ExoClock’s November 2025 catalogue, tested against {n_events:,} transits of "
                          f"{n_planets} planets that NASA’s TESS satellite saw later", 15, 400, INK2))

    steps = [("clock", "Predictions issued", "November 2025"),
             ("lock", "Test rules locked", "before any data opened"),
             ("dip", "Transits measured", "independently, 2026"),
             ("target", "Every prediction scored", "against its stated range")]
    sx = [40 + i * 235 for i in range(4)]
    for i, (k, a, b) in enumerate(steps):
        cx, cy = sx[i] + 20, 122
        e.append(f'<circle cx="{cx}" cy="{cy}" r="19" fill="{TINT}"/>')
        e.append(icon(k, cx, cy))
        e.append(text(cx + 28, cy - 3, a, 15, 600))
        e.append(text(cx + 28, cy + 15, b, 13.5, 400, INK2))
        if i < 3:
            ax = sx[i + 1] - 8
            e.append(f'<path d="M{ax-5} {cy-5} L{ax} {cy} L{ax-5} {cy+5}" stroke="{MUTED}" '
                     f'stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

    top, base = 178, 404
    e.append(f'<line x1="40" y1="160" x2="{W-40}" y2="160" stroke="{RULE}" stroke-width="1"/>')
    e.append(f'<rect x="{x(60):.1f}" y="{base-30}" width="{x(240)-x(60):.1f}" height="30" fill="{BAND}"/>')
    e.append(text((x(60) + x(240)) / 2, base - 11, "length of a transit", 14, 400, INK2, "middle"))

    ymid = 306
    pts = swarm(others, ymid, 4.0, 0.8)
    for px, py in pts:
        e.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.0" fill="{BLUE}" stroke="#ffffff" stroke-width="1"/>')
    hx = x(hr)
    e.append(f'<circle cx="{hx:.1f}" cy="{ymid}" r="8" fill="{VERM}" stroke="#ffffff" stroke-width="2"/>')

    bl, br = x(min(others)), x(max(others))
    by = min(py for _, py in pts) - 16
    e.append(f'<path d="M{bl:.1f} {by+7} V{by} H{br:.1f} V{by+7}" stroke="{INK2}" stroke-width="1.2" fill="none"/>')
    e.append(text((bl + br) / 2, by - 28, "150 of 151 planets: every transit", 16.5, 600, INK, "middle"))
    e.append(text((bl + br) / 2, by - 10, "within 26 minutes of its prediction", 16.5, 600, INK, "middle"))

    ly = by - 28
    e.append(text(X1 + 10, ly, "1 planet missed by hours", 16.5, 600, INK, "end"))
    e.append(text(X1 + 10, ly + 18, "HR 858 b came about 6 hours early", 14, 400, INK2, "end"))
    e.append(text(X1 + 10, ly + 34, "on all 16 transits; a neighbouring", 14, 400, INK2, "end"))
    e.append(text(X1 + 10, ly + 50, "planet ran hours late", 14, 400, INK2, "end"))
    e.append(f'<path d="M{hx:.1f} {ly+60} V{ymid-12}" stroke="{INK2}" stroke-width="1.2"/>')

    e.append(f'<line x1="{X0}" y1="{base}" x2="{X1}" y2="{base}" stroke="{MUTED}" stroke-width="1"/>')
    for v, lab in [(1, "1 minute"), (10, "10 minutes"), (60, "1 hour"), (360, "6 hours")]:
        e.append(f'<line x1="{x(v):.1f}" y1="{base}" x2="{x(v):.1f}" y2="{base+6}" stroke="{MUTED}" stroke-width="1"/>')
        e.append(text(x(v), base + 22, lab, 14, 400, INK2, "middle"))
    e.append(text((X0 + X1) / 2, base + 44, "Each dot is one planet’s largest miss (logarithmic scale)", 14.5, 400, MUTED, "middle"))

    cards = [(f"≈{median:.0f} minute", "typical miss across", f"all {n_events:,} transits"),
             (f"{round(cov*100)}%, not 95%", "of each planet’s transits fell inside", "ranges labelled 95%: a little narrow"),
             ("Open table", "every planet’s predictions and misses,", "re-scorable by anyone")]
    cw, cg, cy0 = 290, 25, 488
    for i, (big, l1, l2) in enumerate(cards):
        cx = 40 + i * (cw + cg)
        e.append(f'<rect x="{cx}" y="{cy0}" width="{cw}" height="96" rx="8" fill="#f6f8fa"/>')
        e.append(f'<rect x="{cx}" y="{cy0}" width="4" height="96" rx="2" fill="{BLUE}"/>')
        e.append(text(cx + 20, cy0 + 38, big, 26, 600))
        e.append(text(cx + 20, cy0 + 64, l1, 14.5, 400, INK2))
        e.append(text(cx + 20, cy0 + 82, l2, 14.5, 400, INK2))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="{FONT}">\n<title>Graphical abstract: transit predictions agreed to minutes, '
           f'with one hours-long miss</title>\n' + "\n".join(e) + "\n</svg>\n")
    OUT.mkdir(parents=True, exist_ok=True)
    svg_p = OUT / "graphical_abstract.svg"
    svg_p.write_text(svg)
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(OUT / "graphical_abstract.pdf"), str(svg_p)], check=True)
    subprocess.run(["rsvg-convert", "-z", "2", "-o", str(OUT / "graphical_abstract.png"), str(svg_p)], check=True)
    receipt = {"inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (TABLE, PIT)},
               "planets": n_planets, "events": n_events, "hr858b_max_min": hr,
               "max_other_min": max(others), "pooled_median_min": median, "m0_coverage95_planet": cov,
               "outputs_sha256": {n: hashlib.sha256((OUT / n).read_bytes()).hexdigest()
                                  for n in ("graphical_abstract.svg",)}}
    (OUT / "graphical_abstract_receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")


if __name__ == "__main__":
    main()
