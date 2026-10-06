#!/usr/bin/env python3
"""Read a feature matrix CSV and print an honest parity score.

Standard library only. Python 3.9 or newer.

Usage:
    python3 parity.py clone/features.csv

Input CSV columns: feature,area,priority,original,clone,notes
  priority: must, should or could
  original: yes, partial or no (no means the original does not have it, so the row is excluded)
  clone:    yes, partial, no, skip or n/a

Scoring:
  must = 3 points, should = 2, could = 1.
  yes earns full points, partial earns half, no earns none.
  skip and n/a rows are left out of the score and reported separately.
  Rows the original does not have are left out too.
  Parity = points earned / points available, as a percentage, rounded down.

The last line is the parity line. Copy it verbatim into clone/receipts.md.
"""
import argparse
import csv
import math
import sys

WEIGHTS = {"must": 3, "should": 2, "could": 1}
EARNED = {"yes": 1.0, "partial": 0.5, "no": 0.0}
EXCLUDED_CLONE = {"skip", "n/a", "na"}
REQUIRED_COLUMNS = ["feature", "area", "priority", "original", "clone"]


def _norm(value):
    return (value or "").strip().lower()


def read_matrix(path):
    with open(path, "r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("CSV is missing columns: {}".format(", ".join(missing)))
        return [{key: (value or "") for key, value in row.items() if key} for row in reader]


def score(rows):
    """Return a dict with the score and the lists the skill prints. Pure, no printing."""
    warnings = []
    scored = []
    skipped = []
    not_applicable = []
    original_lacks = []
    for index, row in enumerate(rows, start=2):  # line 1 is the header
        feature = row.get("feature", "").strip() or "(unnamed row {})".format(index)
        priority = _norm(row.get("priority"))
        original = _norm(row.get("original"))
        clone = _norm(row.get("clone"))
        if priority not in WEIGHTS:
            warnings.append("line {}: priority {!r} is not must, should or could. Counted as could.".format(index, row.get("priority")))
            priority = "could"
        if original == "no":
            original_lacks.append(feature)
            continue
        if clone in EXCLUDED_CLONE:
            (skipped if clone == "skip" else not_applicable).append((feature, row.get("notes", "").strip()))
            continue
        if clone not in EARNED:
            warnings.append("line {}: clone {!r} is not yes, partial, no, skip or n/a. Counted as no.".format(index, row.get("clone")))
            clone = "no"
        scored.append({"feature": feature, "area": row.get("area", "").strip() or "(no area)", "priority": priority, "clone": clone, "weight": WEIGHTS[priority]})

    available = sum(item["weight"] for item in scored)
    earned = sum(item["weight"] * EARNED[item["clone"]] for item in scored)
    percent = int(math.floor(earned / available * 100)) if available else 0

    by_priority = {}
    for name in WEIGHTS:
        items = [item for item in scored if item["priority"] == name]
        by_priority[name] = {"done": sum(1 for item in items if item["clone"] == "yes"), "partial": sum(1 for item in items if item["clone"] == "partial"), "total": len(items)}

    areas = {}
    for item in scored:
        bucket = areas.setdefault(item["area"], {"area": item["area"], "available": 0, "earned": 0.0, "missing": 0})
        bucket["available"] += item["weight"]
        bucket["earned"] += item["weight"] * EARNED[item["clone"]]
        if item["clone"] != "yes":
            bucket["missing"] += 1
    area_scores = []
    for bucket in areas.values():
        pct = int(math.floor(bucket["earned"] / bucket["available"] * 100)) if bucket["available"] else 0
        area_scores.append({"area": bucket["area"], "percent": pct, "missing": bucket["missing"]})
    area_scores.sort(key=lambda item: (item["percent"], -item["missing"], item["area"]))

    order = {"must": 0, "should": 1, "could": 2}
    missing = [item for item in scored if item["clone"] != "yes"]
    missing.sort(key=lambda item: order[item["priority"]])  # stable, so CSV order survives inside a priority

    shippable = by_priority["must"]["total"] > 0 and by_priority["must"]["done"] == by_priority["must"]["total"]
    if by_priority["must"]["total"] == 0:
        warnings.append("no must rows found. Mark at least one feature must before trusting this score.")

    return {
        "percent": percent,
        "earned": earned,
        "available": available,
        "by_priority": by_priority,
        "areas": area_scores,
        "missing": missing,
        "skipped": skipped,
        "not_applicable": not_applicable,
        "original_lacks": original_lacks,
        "shippable": shippable,
        "warnings": warnings,
    }


def parity_line(result):
    bp = result["by_priority"]
    verdict = "shippable slice" if result["shippable"] else "not shippable yet"
    return "PARITY {}% | must {}/{} | should {}/{} | could {}/{} | skipped {} | n/a {} | {}".format(
        result["percent"],
        bp["must"]["done"], bp["must"]["total"],
        bp["should"]["done"], bp["should"]["total"],
        bp["could"]["done"], bp["could"]["total"],
        len(result["skipped"]), len(result["not_applicable"]), verdict,
    )


def render(result):
    lines = []
    for warning in result["warnings"]:
        lines.append("warning: " + warning)
    if result["warnings"]:
        lines.append("")
    bp = result["by_priority"]
    lines.append("Parity: {}% ({:g} of {:g} points)".format(result["percent"], result["earned"], result["available"]))
    lines.append("Must-haves done: {} of {}{}".format(bp["must"]["done"], bp["must"]["total"], " ({} partial)".format(bp["must"]["partial"]) if bp["must"]["partial"] else ""))
    lines.append("Should-haves done: {} of {}".format(bp["should"]["done"], bp["should"]["total"]))
    lines.append("Could-haves done: {} of {}".format(bp["could"]["done"], bp["could"]["total"]))
    lines.append("Excluded: {} skipped, {} n/a, {} the original does not have".format(len(result["skipped"]), len(result["not_applicable"]), len(result["original_lacks"])))
    if result["skipped"]:
        lines.append("")
        lines.append("Skipped (cannot be rebuilt, with reason):")
        for feature, note in result["skipped"]:
            lines.append("- {}{}".format(feature, ": " + note if note else ""))
    if result["not_applicable"]:
        lines.append("")
        lines.append("Not applicable (browser or OS provides it):")
        for feature, note in result["not_applicable"]:
            lines.append("- {}{}".format(feature, ": " + note if note else ""))
    if result["areas"]:
        lines.append("")
        lines.append("Weakest areas:")
        for item in result["areas"][:3]:
            lines.append("- {} at {}% ({} feature{} not done)".format(item["area"], item["percent"], item["missing"], "" if item["missing"] == 1 else "s"))
    if result["missing"]:
        lines.append("")
        lines.append("Missing, in build order:")
        for item in result["missing"]:
            state = "partial" if item["clone"] == "partial" else "missing"
            lines.append("- [{}] {} ({}, {})".format(item["priority"], item["feature"], item["area"], state))
    lines.append("")
    if not result["shippable"]:
        lines.append("Not shippable yet: a must-have is missing or partial.")
    else:
        lines.append("Every must-have is done. The slice is shippable to you; a person still checks it before anyone else sees it.")
    lines.append(parity_line(result))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("csv_path", help="feature matrix CSV")
    args = parser.parse_args(argv)
    try:
        rows = read_matrix(args.csv_path)
    except (OSError, ValueError) as err:
        print(str(err), file=sys.stderr)
        return 1
    print(render(score(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
