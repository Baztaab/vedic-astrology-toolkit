"""Regression checks for an anonymous chart supplied as external sidereal longitudes.

No natal date, location, or identifying information is stored here.
Passing these tests checks deterministic program behavior, not predictions.
"""
import json
from pathlib import Path
import unittest

from vedic_toolkit import core, decision_rules, yogas
from tests.external_sidereal_case_audit import FIXTURE, generate


class ExternalSiderealD1Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.longitudes = cls.fixture["longitudes"]

    def test_fixture_contains_no_identifying_birth_inputs(self):
        self.assertEqual(set(self.longitudes), set(core.PLANETS) | {"Asc"})
        for forbidden in ("name", "birth", "datetime", "date", "timezone", "latitude", "longitude", "city"):
            self.assertNotIn(forbidden, self.fixture)

    def test_frozen_d1_signs_without_recomputing_ayanamsa(self):
        signs = core.division(self.longitudes, 1)
        actual = {planet: core.SIGNS[sign] for planet, sign in signs.items()}
        self.assertEqual(actual, self.fixture["expected_d1_signs"])
        self.assertEqual(core.count(signs["Asc"], signs["Jupiter"]), 3)
        self.assertEqual(core.count(signs["Saturn"], signs["Jupiter"]), 11)

    def test_whole_yoga_catalog_and_reproducibility(self):
        first = yogas.evaluate(self.longitudes)
        second = yogas.evaluate(dict(reversed(list(self.longitudes.items()))))
        expected = json.loads(
            (Path(__file__).resolve().parents[1] / "rule_coverage.json").read_text(encoding="utf-8")
        )["count"]
        self.assertEqual(first["rules_checked"], expected)
        self.assertEqual(len(first["rules"]), expected)
        self.assertEqual(first["rules"], second["rules"])

    def test_selected_yogas_report_structure_not_life_outcomes(self):
        rows = yogas.evaluate(self.longitudes)["rules"]
        by_name = {row["name"]: row for row in rows}
        for name in ("Budha-Aaditya", "Vesi", "Anaphaa"):
            with self.subTest(rule=name):
                self.assertEqual(by_name[name]["status"], "conditions_met")
        for name in ("Kemadruma", "Sakata"):
            with self.subTest(rule=name):
                self.assertEqual(by_name[name]["status"], "conditions_not_met")

    def test_opposing_dasha_conditions_are_retained(self):
        signs = core.division(self.longitudes, 1)
        lagna = signs["Asc"]
        jupiter_is_3rd = core.count(lagna, signs["Jupiter"]) == 3
        jupiter_debilitated = signs["Jupiter"] == core.DEBIL["Jupiter"]
        jupiter_11th_from_saturn = core.count(signs["Saturn"], signs["Jupiter"]) == 11
        evidence = [
            {"id": "jupiter_11th_from_saturn", "polarity": "supportive",
             "met": jupiter_11th_from_saturn, "source": "BPHS ch.57, Saturn/Jupiter AD"},
            {"id": "jupiter_3rd_and_debilitated", "polarity": "adverse",
             "met": jupiter_is_3rd and jupiter_debilitated,
             "source": "BPHS ch.57, Saturn/Jupiter AD"},
        ]
        result = decision_rules.resolve(
            evidence, topic="Saturn/Jupiter conditional textual conflict",
            window="AD only; no event forecast"
        )
        self.assertEqual(result["classification"], "mixed")
        self.assertTrue(result["needs_review"])
        self.assertIsNone(result["probability"])
        self.assertEqual(len(result["active_evidence"]), 2)

    def test_unknown_override_cannot_suppress_a_known_condition(self):
        evidence = [
            {"id": "active", "polarity": "adverse", "met": True, "source": "synthetic test"},
            {"id": "exception", "polarity": "supportive", "met": None, "source": "synthetic test"},
        ]
        result = decision_rules.resolve(
            evidence, topic="test", window="test",
            overrides=[{"by": "exception", "target": "active", "source": "synthetic test"}]
        )
        self.assertEqual([r["id"] for r in result["active_evidence"]], ["active"])
        self.assertEqual(result["pending_evidence"], ["exception"])
        self.assertTrue(result["pending_overrides"])

    def test_audit_contains_all_rules_and_review(self):
        result = generate()
        self.assertEqual(len(result["rules"]), result["rules_checked"])
        self.assertEqual(sum(result["rule_status_counts"].values()), result["rules_checked"])
        self.assertIn("qualification_review", result)
        self.assertNotIn("birth_datetime", result)


if __name__ == "__main__":
    unittest.main()
