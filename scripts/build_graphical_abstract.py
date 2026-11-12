"""Graphical abstract for the reconstruction brief and article.

Reads the saved per-planet comparison table (Table 3) and the PIT/percentile
summary; writes SVG, PDF (rsvg-convert) and PNG to results/reconstruction_displays/.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/reconstruction_displays"
TABLE = OUT / "table3_planets.csv"
PIT = OUT / "pit_table2.json"
CLAIMS = ROOT / "coordination/claims.md"

W, H = 1000, 632
FONT = "'Avenir Next', 'Helvetica Neue', Arial, sans-serif"
INK, INK2, MUTED, RULE = "#1f2328", "#4b535c", "#7a828b", "#d0d5da"
BLUE, VERM, TINT = "#0072B2", "#D55E00", "#e6f1f8"

X0, X1 = 70, 950
LO, HI = math.log10(0.25), math.log10(900)


def x(minutes):
    return X0 + (math.log10(minutes) - LO) / (HI - LO) * (X1 - X0)


def text(xp, yp, s, size=16, weight=400, fill=INK, anchor="start", style=""):
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
    all_rows = list(csv.DictReader(open(TABLE)))
    rows = [r for r in all_rows if int(r["n_accepted"]) > 0]
    worst = {r["planet"]: float(r["max_abs_error_min"]) for r in rows}
    hr = worst.pop("HR858b")
    hr_events = int(next(r for r in rows if r["planet"] == "HR858b")["n_accepted"])
    others = list(worst.values())
    pit = json.loads(PIT.read_text())
    median = pit["abs_error_min"]["pooled"]["p50"]
    cov = pit["pit_coverage95_check"]["M0"]
    n_events, n_planets = pit["events"], pit["planets"]
    claims = CLAIMS.read_text().splitlines()
    c021 = next(s for s in claims if s.startswith("| C021 |"))
    c043 = next(s for s in claims if s.startswith("| C043 |"))
    c048 = next(s for s in claims if s.startswith("| C048 |"))
    c050 = next(s for s in claims if s.startswith("| C050 |"))
    c063 = next(s for s in claims if s.startswith("| C063 |"))
    accepted, intended = (int(s.replace(",", "")) for s in
                          re.search(r"([\d,]+) of ([\d,]+) manifest events", c043).groups())
    core_planets = int(re.search(r"supports (\d+) core", c021).group(1))
    near, total, bound = re.search(r"so (\d+)/(\d+) planets .*? within ([\d.]+) min", c063).groups()
    near, total, bound = int(near), int(total), float(bound)
    claimed_median = float(re.search(r"median absolute error ([\d.]+) min", c063).group(1))
    claimed_cov = float(re.search(r"coverage ([\d.]+)/", c063).group(1))
    assert n_planets == len(others) + 1 == total
    assert n_events == sum(int(r["n_accepted"]) for r in all_rows) == accepted
    assert len(all_rows) == core_planets
    assert sum(int(r["n_intended"]) for r in all_rows) == intended
    assert sum(v <= bound for v in [*others, hr]) == near == len(others)
    assert round(median, 4) == claimed_median and round(cov, 5) == claimed_cov
    assert "inconclusive by the pre-registered rule" in c043 and 355 < hr < 410
    assert f"{hr_events} accepted held-out transits" in c048 and "before the DRD prediction" in c048
    neighbour_min = float(re.search(r"c \+([\d.]+) to \+", c050).group(1))
    assert neighbour_min > 60 and "Published-reference PDCSAP offsets" in c050

    e = []
    e.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    e.append(text(40, 46, "How well did published planet-transit predictions hold up?", 28, 600))
    e.append(text(40, 74, f"ExoClock’s November 2025 forecasts: {n_events:,} accepted TESS timings "
                          f"from {n_planets} planets", 16, 400, INK2))

    steps = [("clock", "Predictions issued", "November 2025"),
             ("lock", "Main test locked", "before data access"),
             ("dip", "Timings measured", "after lock, own code"),
             ("target", "Accepted times scored", "range width + misses")]
    sx = [40 + i * 235 for i in range(4)]
    for i, (k, a, b) in enumerate(steps):
        cx, cy = sx[i] + 20, 122
        e.append(f'<circle cx="{cx}" cy="{cy}" r="19" fill="{TINT}"/>')
        e.append(icon(k, cx, cy))
        e.append(text(cx + 28, cy - 3, a, 16, 600))
        e.append(text(cx + 28, cy + 17, b, 16, 400, INK2))
        if i < 3:
            ax = sx[i + 1] - 8
            e.append(f'<path d="M{ax-5} {cy-5} L{ax} {cy} L{ax-5} {cy+5}" stroke="{MUTED}" '
                     f'stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

    base = 418
    e.append(f'<line x1="40" y1="160" x2="{W-40}" y2="160" stroke="{RULE}" stroke-width="1"/>')

    ymid = 306
    pts = swarm(others, ymid, 4.0, 0.8)
    for px, py in pts:
        e.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.0" fill="{BLUE}" stroke="#ffffff" stroke-width="1"/>')
    hx = x(hr)
    e.append(f'<circle cx="{hx:.1f}" cy="{ymid}" r="8" fill="{VERM}" stroke="#ffffff" stroke-width="2"/>')

    bl, br = x(min(others)), x(max(others))
    by = min(py for _, py in pts) - 16
    e.append(f'<path d="M{bl:.1f} {by+7} V{by} H{br:.1f} V{by+7}" stroke="{INK2}" stroke-width="1.2" fill="none"/>')
    e.append(text((bl + br) / 2, by - 28, f"{near} of {total} planets", 17, 600, INK, "middle"))
    e.append(text((bl + br) / 2, by - 8, f"all accepted timings within {bound:g} minutes", 17, 600, INK, "middle"))

    ly = by - 28
    e.append(text(X1 + 10, ly, "1 planet missed by hours", 17, 600, INK, "end"))
    e.append(text(X1 + 10, ly + 20, "HR 858 b: about 6 hours early", 16, 400, INK2, "end"))
    e.append(text(X1 + 10, ly + 39, f"on all {hr_events} accepted timings", 16, 400, INK2, "end"))
    e.append(text(X1 + 10, ly + 58, "Neighbour was hours late", 16, 400, INK2, "end"))
    e.append(text(X1 + 10, ly + 77, "on a separate published timetable", 16, 400, INK2, "end"))
    e.append(f'<path d="M{hx:.1f} {ly+87} V{ymid-12}" stroke="{INK2}" stroke-width="1.2"/>')
    e.append(text((X0 + X1) / 2, base - 15,
                  f"Accepted: {n_events:,} of {intended:,} predicted transits; {n_planets} of {core_planets} planets",
                  16, 400, INK2, "middle"))

    e.append(f'<line x1="{X0}" y1="{base}" x2="{X1}" y2="{base}" stroke="{MUTED}" stroke-width="1"/>')
    for v, lab in [(1, "1 minute"), (10, "10 minutes"), (60, "1 hour"), (360, "6 hours")]:
        e.append(f'<line x1="{x(v):.1f}" y1="{base}" x2="{x(v):.1f}" y2="{base+6}" stroke="{MUTED}" stroke-width="1"/>')
        e.append(text(x(v), base + 22, lab, 16, 400, INK2, "middle"))
    e.append(text((X0 + X1) / 2, base + 44, "Each dot: one planet’s largest accepted miss (logarithmic scale)", 16, 400, INK2, "middle"))

    cards = [(f"≈{median:.0f} minute", "typical miss across", f"{n_events:,} accepted timings"),
             (f"{round(cov*100)}%, not 95%", "inside 95% timing ranges,", "averaged over planets"),
             ("Open table", "predictions + accepted timings", "to test better forecasts")]
    cw, cg, cy0 = 290, 25, 488
    for i, (big, l1, l2) in enumerate(cards):
        cx = 40 + i * (cw + cg)
        e.append(f'<rect x="{cx}" y="{cy0}" width="{cw}" height="96" rx="8" fill="#f6f8fa"/>')
        e.append(f'<rect x="{cx}" y="{cy0}" width="4" height="96" rx="2" fill="{BLUE}"/>')
        e.append(text(cx + 20, cy0 + 38, big, 26, 600))
        e.append(text(cx + 20, cy0 + 64, l1, 16, 400, INK2))
        e.append(text(cx + 20, cy0 + 84, l2, 16, 400, INK2))
    e.append(text(W / 2, 615,
                  "Ranges include timing uncertainty. Widening’s score benefit: inconclusive.",
                  16, 400, INK2, "middle"))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="{FONT}">\n<title>Graphical abstract: transit predictions agreed to minutes, '
           f'with one hours-long miss</title>\n' + "\n".join(e) + "\n</svg>\n")
    OUT.mkdir(parents=True, exist_ok=True)
    svg_p = OUT / "graphical_abstract.svg"
    svg_p.write_text(svg)
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(OUT / "graphical_abstract.pdf"), str(svg_p)], check=True)
    subprocess.run(["rsvg-convert", "-z", "2", "-o", str(OUT / "graphical_abstract.png"), str(svg_p)], check=True)
    receipt = {"inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (TABLE, PIT, CLAIMS)},
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "planets": n_planets, "events": n_events, "hr858b_max_min": hr,
               "max_other_min": max(others), "pooled_median_min": median, "m0_coverage95_planet": cov,
               "intended_planets": core_planets, "intended_events": intended,
               "ledger_checks": {"claims": ["C021", "C043", "C048", "C050", "C063"], "pass": True,
                                 "bound_min": bound, "planets_within_bound": near},
               "minimum_font_svg_units": 16, "minimum_font_pt_at_170mm": 16 * (170 / 25.4 * 72) / W,
               "outputs_sha256": {n: hashlib.sha256((OUT / n).read_bytes()).hexdigest()
                                  for n in ("graphical_abstract.svg", "graphical_abstract.pdf", "graphical_abstract.png")}}
    (OUT / "graphical_abstract_receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")


if __name__ == "__main__":
    main()
