# Step 3 implementation and verification

Date: October 17, 2026. CRM report date: February 15, 2026.

## October 18 regression evidence update

User-supplied screenshots now confirm the order page still shows 10 fixture orders, inventory loads, and Salt's ledger produces 8 units at average $2.25 and value $18.00. A [terminal screenshot](inventory-automated-test-passed.png) shows `docker compose exec app python test_inventory.py` completed with `inventory known-answer and guard tests passed`. All four rows in the [regression table](regression-check.md) pass. Earlier statements below about unverified inventory checks describe the original checkpoint and are superseded by this evidence. Automated CRM Flask tests remain unverified.

## Subsequent approved data correction

Browser evidence update: the user supplied an [after-fix screenshot](crm-after-fix.png) showing two regulars, Anh's 31-day lapse and unsent draft, the 4-record consent exclusion, and unchanged catering results. This confirms the normal `/crm` display after correction. It does not establish that the automated Flask tests, inventory tests, or a particular Docker rebuild command ran. The remaining sections retain the earlier implementation history.

After reviewing the before-fix screenshot and diagnosis, the user approved correcting R014's phone to `555-203-0003`. The post-fix CLI run shows Anh with 3 eligible visits, regular status, a 31-day lapse, and one unsent draft. Capacity and the 4-record consent audit are unchanged. All 15 CRM tests passed. See [before/after results](known-answer-test.md). The original Step 3 results and unchanged-seed hash below are historical, before this explicit correction; they do not describe the current CSV.

## Implemented

- All 12 supplied CRM functions, with unchanged signatures and Step 1 thresholds.
- Latest-record consent, opted-in visit counting, exact phone matching, and historical frequency windows.
- All-booking catering capacity, observed same-day alternatives, and a separate room-for-one-booking check.
- Lapsed regular queue, plain-text unsent drafts, and one owner-facing paragraph.
- Additive `/crm` route, navigation link, and clear missing-file/data-error pages.
- Explicit malformed-row errors. Seed identities are preserved.

## Executed checks

From `docker/app`, `python -m unittest -v test_crm_copilot.CRMTests` passed all 14 tests:

| Check | Result |
|------------------------------------|------------------------------------|
| Seed parsing, types, and original phone identities | Pass |
| Seed regulars, consent audit, capacity, and alternative | Pass |
| Frequency at exactly 14 days, beyond 14 days, and custom arguments | Pass |
| Non-consenting visits cannot establish regular status | Pass |
| Latest opt-out revokes eligibility | Pass |
| Same-day conflicting consent favors opt-out in either input order | Pass |
| Future records cannot change historical consent | Pass |
| Missing phones excluded; different phones remain separate | Pass |
| Lapse at exactly 21 days; synthetic lapsed customer gets a labeled draft | Pass |
| Midnight-anchored bucket boundaries, dates, and custom capacity threshold | Pass |
| Alternate ranking independent of default capacity, with deterministic ties | Pass |
| A full alternative is not advertised as available | Pass |
| Malformed cells, consent, dates, slots, and missing columns report errors | Pass |
| Empty inputs and input-record preservation | Pass |

All Python files under `docker/app` also compiled successfully without importing the Flask application. Syntax-tree comparison against pre-edit snapshots confirmed all 18 original Flask functions unchanged, including their decorators and bodies. All 12 supplied CRM argument signatures match the starter. Only the shared navigation and the added CRM route change Flask source behavior. The CRM module imports standard-library CSV, collections, datetime, and CLI support; its code has no transport or dispatch call.

Seed SHA-256 before and after: `A4FCF8E9658B3111ABC74F9C6E81BDD03F181E42F116369B13F21F3ADAE6F5AF`.

## Observed seed results

These results were produced by running `crm_copilot.py` against the unchanged seed; they were not obtained from a rebuilt `/crm` page.

| Field | Observed |
|------------------------------------|------------------------------------|
| Parsed rows | 29 |
| Qualified regulars | 1: Mai Tran, 8 opted-in visits; last visit February 12 |
| Non-opted-in frequency-qualified records excluded | 4: R009–R012 |
| Over-capacity bucket | February 14, 18:00–20:00: 3 bookings |
| Observed same-day alternative | February 14, 14:00–16:00: 1 booking; room for one more |
| Seed follow-up queue | Empty |
| Seed drafts | Empty |

Anh Nguyen remains two identities: `555-203-0003` has two visits and `555-203-0009` has one. No merge or seed correction was performed. Fabricated clean data independently verified that a genuinely lapsed regular receives a draft.

Generated owner brief:

> Weekly review as of 2026-02-15: 1 consenting customer meets the regular-visit rule in their recorded history. 0 regulars have gone at least 21 days without a visit and have follow-up drafts ready for staff review. The catering window starting 2026-02-14 18:00 has 3 bookings, above the limit of 2. The quieter observed window starting 2026-02-14 14:00 is a possible alternative; staff should confirm availability. All messages remain drafts; nothing has been sent.

## Baseline and remaining runtime checks

Before edits, the existing service returned HTTP 200 for `/`, `/inventory`, `/inventory/scan`, and `/health`. The order page showed `10 fixture orders still load.` This is a baseline observation, not proof that the updated app was deployed.

Docker was not found in this shell, and the usual Windows Docker executable path was absent. The installed Python environments did not include Flask or qrcode. Downloading the existing project requirements into an isolated temporary directory failed under network restrictions; the escalation was not approved, and no alternative download was attempted.

The following remain **unverified**:

- Flask integration tests in `test_crm_copilot.FlaskTests`, including template escaping and HTTP error responses.
- Existing `test_inventory.py` known-answer, duplicate-request, stock-guard, and label checks.
- The Docker rebuild command itself; the new `/crm` normal-case display is now confirmed by the supplied after-fix screenshot.
- Week 3/4 runtime regression checks after the rebuild.

No live inventory transactions, database resets, messages, or seed corrections were performed. No test or deployment success is claimed for the unavailable runtime checks.

When Docker is available, rebuild only the app service using the existing project instructions. Run `docker compose exec app python test_inventory.py` and inspect `/crm`, `/`, `/inventory`, and `/inventory/scan`. The additional CRM test file lives in the source tree and is not included by the unchanged Dockerfile's explicit COPY list; run it locally with the existing requirements installed, or copy that test file into the container before invoking it there.
