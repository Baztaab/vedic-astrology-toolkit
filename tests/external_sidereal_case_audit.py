"""Reproducible, anonymous, external-sidereal D1 yoga inventory.

This is NOT a birth-chart computation, empirical validation, or event forecast.
It consumes already-computed longitudes so the toolkit's default Lahiri setting
does not silently replace an independent True Pushya calculation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from vedic_toolkit import core, interpretation, yogas

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "external_sidereal_case_d1.json"
CATALOG = Path(__file__).resolve().parents[1] / "rule_coverage.json"


def json_safe(value):
    if isinstance(value, Fraction):
        return float(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        return sorted(json_safe(item) for item in value)
    return value


def generate():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    longitudes = fixture["longitudes"]
    if set(longitudes) != set(core.PLANETS) | {"Asc"}:
        raise ValueError("The input must contain exactly nine grahas and the ascendant.")
    signs = core.division(longitudes, 1)
    actual_signs = {name: core.SIGNS[index] for name, index in signs.items()}
    if actual_signs != fixture["expected_d1_signs"]:
        raise ValueError("External sidereal D1 signs do not match the frozen fixture.")

    catalog = yogas.evaluate(longitudes, varga=1)
    review = interpretation.review(longitudes, catalog)
    expected_count = json.loads(CATALOG.read_text(encoding="utf-8"))["count"]
    if len(catalog["rules"]) != expected_count:
        raise ValueError("Yoga inventory coverage changed; review this result before release.")

    statuses = Counter(rule["status"] for rule in catalog["rules"])
    payload = {
        "schema": "external_sidereal_yoga_audit_v1",
        "fixture": FIXTURE.name,
        "input_sha256": hashlib.sha256(
            json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "input_provenance": fixture["provenance"],
        "d1_signs": actual_signs,
        "rules_checked": len(catalog["rules"]),
        "rule_status_counts": dict(sorted(statuses.items())),
        "rules": catalog["rules"],
        "qualification_review": review,
        "disclaimers": [
            "Rules represent traditional structural conditions, not verified future events.",
            "Missing strength, speed, day/night, and special-point inputs remain unqualified.",
            "Tool-specific divisional formulas and their derived qualifiers are not certified equal to the external chart's divisional canon.",
            "No birth date, birthplace, identity, or lived-life outcomes are included.",
            "Conflicting or pending classical rules are not silently converted into favorable or adverse final judgments.",
        ],
    }
    return json_safe(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = generate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "report": str(args.output),
        "rules_checked": report["rules_checked"],
        "rule_status_counts": report["rule_status_counts"],
        "qualification_status": report["qualification_review"].get("status", "reviewed"),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
