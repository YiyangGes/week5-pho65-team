# Known-Answer Test — Seeded Failure (Steps 4-6)

> **Instructions:** 1. Fill "Prediction" before you ever run the co-pilot (Step 4). 2. Fill "Observed (before fix)" from your first real run. 3. Diagnose the type (data / logic / interface) with your reasoning — do not just guess and check. 4. Apply the smallest correction, then fill "Observed (after fix)." 5. This table is your verification evidence. "It ran with no errors" is not acceptable on its own.

> **Note:** the "e.g." examples below use a fictional Tuesday-lunch scenario that does not match your actual seed file, on purpose — copying these values instead of your own real output will not pass grading, and will not match what your team actually observes.

## Capacity Prediction (made BEFORE first run)

| Field | Your answer |
|------------------------------------|------------------------------------|
| Predicted over-capacity day/slot | Saturday, February 14, 2026, 18:00–20:00 |
| Predicted booking count in that slot | 3 bookings (R016–R018), exceeding the limit of 2 |

The prediction was first stated in chat before execution and transcribed into the workbook after the initial run.

## Full Known-Answer Table

| Stage | Regular-status result | Follow-up queue result | Capacity result |
|------------------|------------------|------------------|------------------|
| **Observed (before fix)** | Mai was the only regular. Anh appeared under two phones, with 2 and 1 eligible visits; neither qualified. | Empty queue and no drafts, shown in the supplied `/crm` screenshot and initial CLI output. | February 14, 18:00–20:00: 3 bookings, OVER CAPACITY. Alternative: 14:00–16:00, 1 booking. |
| **Diagnosis** | Data issue: R013/R015 use `555-203-0003`; R014 uses `555-203-0009`. Exact-phone grouping correctly kept them separate. | Combined opted-in visits span January 5–15, within 14 days; the latest visit is 31 days before February 15. The split keys prevent qualification. | Correct result; no capacity logic change needed. |
| **Fix applied** | User approved changing only R014's phone from `555-203-0009` to `555-203-0003`. No automatic crosswalk, name-based merge, or threshold change. | Reran the CRM with the same February 15, 2026 report date. | No catering data changed. |
| **Observed (after fix)** | CLI output and the supplied after-fix browser screenshot show Mai and Anh regular; Anh has 3 eligible visits and last visit January 15. | Both show one entry: Anh Nguyen, `555-203-0003`, 31 days since last visit; one draft labeled DRAFT -- NOT SENT. | Unchanged in CLI and browser: February 14, 18:00–20:00 has 3 bookings; 14:00–16:00 has 1 and is suggested. |

## Confirm

Does the after-fix result match what you would now expect, given the corrected data? Explain any remaining gap.

Yes. The post-fix CLI result matches the expected regular status, lapse interval, draft count, and unchanged capacity result. The consent audit still excludes 4 records. All 15 dependency-free CRM tests passed, including a test that reproduces the original split identity in memory and verifies that the code does not silently merge it.

The user subsequently supplied an after-fix browser screenshot confirming the same results at `/crm`. Screenshot review verifies the displayed normal case. The user's later [terminal screenshot](inventory-automated-test-passed.png) confirms the automated inventory suite passed.

## Screenshot evidence

- [Before fix](crm-before-fix.png): split Anh identities, empty follow-up queue, no drafts.
- [After fix](crm-after-fix.png): unified Anh identity, 3 visits, regular status, 31-day lapse, and one unsent draft; unchanged capacity and consent-exclusion count.

## Exact draft observed after correction

``` text
DRAFT -- NOT SENT
Hi Anh Nguyen, we haven't seen you at Pho65 for a while and would love to welcome you back whenever it suits you.
Best wishes, the Pho65 team
```

## Reproduction

From `docker/app`, run `python -m unittest -v test_crm_copilot.CRMTests`. From the project root, run `python docker/app/crm_copilot.py sample-data/pho65-week5-seed.csv 2026-02-15`.