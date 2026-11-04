"""Check D028/D029 calendar boundaries using official schedule metadata only.

Downloads two fixed schedule URLs only when --acquire is supplied. Never
requests target-level products, photometry, transit measurements or images.
"""

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/tess_schedule"
SOURCES = {
    "heasarc_sectors_2026-11-05.html": "https://heasarc.gsfc.nasa.gov/docs/tess/sector.html",
    "orbit_times_2026-11-05.csv": "https://archive.stsci.edu/missions/tess/doc/tess_drn/tess_orbit_times_by_sector.csv",
}


class TableRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            if self.row is None:
                self.row = []
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag in ("tr", "table") and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def source_rows(text):
    parser = TableRows()
    parser.feed(text)
    result = []
    for row in parser.rows:
        if not row or not re.fullmatch(r"s\d+", row[0]):
            continue
        sector = int(row[0][1:])
        if sector < 97 or sector > 110:
            continue
        start, end = [datetime.strptime(row[i], "%Y %b %d").date().isoformat() for i in (4, 5)]
        result.append({"sector": sector, "start_calendar_day": start, "end_calendar_day": end,
                       "pointing_ra_dec": row[2], "pointing_roll": row[3],
                       "source_comment": row[7] if len(row) > 7 else ""})
    if {r["sector"] for r in result} != set(range(97, 111)):
        raise ValueError("Incomplete source schedule extraction for sectors 97–110")
    return sorted(result, key=lambda r: (r["sector"], r["start_calendar_day"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire", action="store_true")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    receipt = []
    for name, url in SOURCES.items():
        path = RAW / name
        meta = RAW / (name + ".receipt.json")
        if not path.exists() and args.acquire:
            data = urlopen(url, timeout=30).read()
            path.write_bytes(data)
            path.chmod(0o444)
            meta.write_text(json.dumps({"url": url, "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "metadata_only": True}, indent=2) + "\n")
        source = json.loads(meta.read_text())
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != source["sha256"] or source["url"] != url:
            raise ValueError("Schedule provenance mismatch")
        receipt.append({"path": str(path.relative_to(ROOT)), **source})
    rows = source_rows((RAW / "heasarc_sectors_2026-11-05.html").read_text())
    for row in rows:
        lo, hi = row["start_calendar_day"], row["end_calendar_day"]
        row["sealed_calendar_overlap"] = hi >= "2025-11-19"
        row["strict_A_calendar_class"] = ("wholly_before_conservative_issue_boundary" if hi < "2026-02-12" else
            "wholly_after_conservative_issue_boundary" if lo > "2026-02-12" else "straddles_conservative_issue_boundary")
        row["schedule_status_on_2026_11_05"] = "ended" if hi < "2026-11-05" else "future" if lo > "2026-11-05" else "in_progress"
        row["precision"] = "calendar dates only; not target exposure windows"
    orbit_text = (RAW / "orbit_times_2026-11-05.csv").read_text().splitlines()
    orbit = list(csv.DictReader(line for line in orbit_text if not line.startswith("#")))
    old_jd = 2461082.5
    old_date = datetime.fromtimestamp((old_jd - 2440587.5)*86400, tz=timezone.utc).isoformat()
    corrected = datetime(2026, 2, 12, tzinfo=timezone.utc).timestamp()/86400 + 2440587.5
    out = ROOT / "results/pilot_v1/tranche2_review"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "schedule_calendar_review.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {"metadata_only": True, "light_curves_opened": 0,
        "command": "python scripts/review_tranche2_schedule.py --acquire",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": receipt, "orbit_csv_max_sector": max(int(r["Sector"]) for r in orbit),
        "orbit_csv_status": "Stale: ends at sector 42; cannot resolve sealed-era exact orbit windows",
        "old_strict_A_constant_jd": old_jd, "old_constant_actual_UTC": old_date,
        "intended_day_after_publication_UTC": "2026-02-12T00:00:00+00:00",
        "corrected_UTC_JD": corrected,
        "findings": ["S98 spans Nov 9 to Jan 5, not a 27.4-day window",
            "S99 has a documented Jan 15-22 interruption; special sector 1751 is outside the standard-sector inventory",
            "S100 straddles the conservative issue boundary; event eligibility cannot be assigned from sector label alone",
            "S110 is in progress on Nov 5; full-sector future predictions are not already observed transits",
            "Calendar schedule does not prove target cadence availability, usable data or transit detection",
            "No BJD_TDB forecast values were subtracted from UTC/date-only schedule values in this audit"],
        "counts_recomputed": False}
    (out / "schedule_review.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k != "sources"}, indent=2))


if __name__ == "__main__":
    main()
