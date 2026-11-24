# External sidereal D1: source-backed rule audit

This is an **anonymous structural test fixture**; it deliberately contains no birth
time, birth location, identity, lived events, or personal conclusions.

## Why this path exists

The toolkit defaults to Lahiri sidereal and its own selected varga methods. The
source chart was calculated elsewhere using **True Pushya / mean nodes / Whole
Sign**. Feeding birth details through the toolkit's default astronomy would
silently change the inputs. This audit instead consumes the frozen sidereal D1
longitudes directly, using the toolkit's own `yogas.evaluate` and
`interpretation.review` implementations.

Longitudes were transcribed from displayed degrees/minutes/seconds to 0.01 arcsecond,
**not** from the full-precision external computation. Avoid boundary-sensitive
inferences and do not claim that the toolkit's derived divisional charts,
dignity/strength choices, day/night, or avasthas equal the external Canon.

## Run

```bash
python -m pip install -r requirements.txt
python -m unittest tests.test_external_sidereal_rules -v
python -m tests.external_sidereal_case_audit --output artifacts/external_sidereal_rule_audit.json
```

The dedicated GitHub Actions workflow runs both commands and uploads the full
JSON report as an artifact. It does not place private life history into the
repository. A successful GitHub Action verifies executable software behavior,
**not** empirical support for any traditional prediction.

## Interpreting the evidence

- **conditions_met:** all implemented structural predicates for a rule are true;
  it is *not* a prediction of the rule's promised real-world outcome.
- **conditions_not_met:** at least one necessary implemented predicate is false.
- **conditions_pending:** data, qualitative strength, ambiguity, or a separate
  contract is unresolved. Do not turn this into either success or failure.
- **qualification_review:** exceptions and magnitude evidence available in the
  project; their absence from the output is not proof that none exist.
- `mixed` in the example Saturn/Jupiter AD test means two recorded textual
  conditions have opposing polarity with no sourced overriding rule supplied.
  It does not mean that the world will produce both outcomes.

The test checks the repository's current `rule_coverage.json` count (170 at
creation) and fails loudly if the live catalog changes without review. It also
preserves an explicit adverse/favorable clash instead of averaging or voting.

## What is **not** established

This does not run an original astronomical birth calculation, reproduce external
D9/D10 by independent oracle, validate JHora GUI parity, authenticate source
verses, or measure predictive accuracy. This is one audited component of a
larger classical-judgment workflow; further sourced decisions are needed before
issuing final chart judgments.
