"""Independently verify the archived public/private OSF history and file IDs."""

import csv
import json
from pathlib import Path

from sprint1_forecast_core import ROOT, digest, write_json


def main():
    raw=ROOT/"data/raw/sprint1_osf_logs"
    receipt=json.loads((raw/"receipt.json").read_text())
    for row in receipt:
        if digest(ROOT/row["file"])!=row["sha256"]:
            raise ValueError("Changed public-source cache: "+row["file"])
    rows=[]
    for node in ("wna5e","p298n","wpjtn"):
        public=json.loads((raw/(node+"_made_public.json")).read_text())
        private=json.loads((raw/(node+"_made_private.json")).read_text())
        if public["links"].get("next") or private["links"].get("next"):
            raise ValueError("Unfinished public/private pagination")
        if len(public["data"])!=1 or private["data"]:
            raise ValueError("Public/private history requires adjudication")
        entry=public["data"][0]
        rows.append({"node":node,"public_log_id":entry["id"],
                     "public_at_utc":entry["attributes"]["date"],
                     "made_private_records":0})
    logs=json.loads((raw/"wpjtn.json").read_text())["data"]
    target="691baed85f334aadee770a79"
    added=[r for r in logs if r["attributes"]["action"]=="osf_storage_file_added"
           and target in r["attributes"].get("params",{}).get("urls",{}).get("view","")]
    if len(added)!=1:
        raise ValueError("Exact DRD forecast file add not verified")
    add=added[0]
    file_date=add["attributes"]["date"]
    public_date=next(r["public_at_utc"] for r in rows if r["node"]=="wpjtn")
    anchor=max(file_date,public_date)
    if anchor!="2025-11-18T09:43:24.090310":
        raise ValueError("Unexpected DRD availability anchor")
    source=list(csv.DictReader((ROOT/"results/pilot_v1/source_manifest.csv").open()))
    matches=[r for r in source if r["release"]=="DRD" and r["osf_name"]=="catalogue_of_ephemerides.txt"]
    if len(matches)!=1 or target not in matches[0]["osf_path"]:
        raise ValueError("Availability history does not match analysed file identity")
    write_json(ROOT/"results/sprint1/literature/osf_history_verification.json",
               {"histories":rows,"DRD_forecast_file_id":target,"DRD_file_added_log_id":add["id"],
                "DRD_file_added_utc":file_date,"DRD_verified_public_anchor_utc":anchor+"Z",
                "DRD_analysed_file_sha256":matches[0]["sha256"],"raw_receipts":receipt,
                "interpretation":"max(file add, public transition); no intervening private action in complete filtered histories",
                "strict_whole_day_start_utc":"2025-11-19T00:00:00Z","protected_data_opened":False})


if __name__=="__main__":
    main()
