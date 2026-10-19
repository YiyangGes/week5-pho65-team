# Innovation Requirements Evidence — Step 7

> **Instructions:** For each requirement, state the exact number or slot your build produced (not an estimate), and name the file/function/URL where it's visible.

**Confirmed:** all three requirements are implemented and visible in the [after-fix `/crm` screenshot](crm-after-fix.png). The recorded CLI and 15 passing CRM tests support the rule checks. The user's [terminal screenshot](inventory-automated-test-passed.png) separately confirms the inventory suite passed; automated CRM Flask tests remain unverified.

## 1. Consent-First Regulars Detection

- Number of records excluded as non-opted-in: **4**, Linh Pham's R009–R012. Visits on February 3, 6, 10, and 13 span 10 days, meeting frequency without consent. This is not a count of every opt-out in the CSV.
- Code location: `docker/app/crm_copilot.py`, `eligible_records()` requires a phone and opted-in visits; `compute_regular_status()` also requires latest-record consent and returns the excluded audit list. `run()` returns `excluded_non_opted_in_count`.
- Output location: `docker/app/app.py`, `crm()` renders the exact count **4** below **Eligible customers** at `/crm`, above the status table.
- Verification: the CLI audit identifies exactly R009–R012. The [after-fix screenshot](crm-after-fix.png) shows 4 exclusions and only Mai and Anh marked Regular. Passing CRM tests also check that non-consenting visits never establish regular status and that latest opt-out removes eligibility.

## 2. Demand-Shaping Catering Suggestion

- Over-capacity request: **Saturday, February 14, 2026, 18:00–20:00; 3 bookings**, above the limit of 2. R016–R018 count regardless of consent.
- Suggested alternate slot: **February 14, 14:00–16:00; 1 booking**, with capacity for one additional booking.
- Why this slot was chosen: `suggest_alternate_slot()` ranks observed same-day buckets by count; `_available_alternate_slot()` checks room for one moved booking. This is a suggestion requiring staff confirmation, not an automatic booking change. Visible in the [after-fix screenshot](crm-after-fix.png).
- Code location: `docker/app/crm_copilot.py`, `capacity_view()`, `suggest_alternate_slot()`, `_available_alternate_slot()`, and the `alternate_slot` field added by `run()`.
- Output location: `docker/app/app.py`, `crm()` renders the **Catering capacity** table and its **Suggested alternative** column at `/crm`. The owner brief also names `2026-02-14 14:00`.

## 3. Weekly Narrative Brief

Paste the exact paragraph your co-pilot generated at `/crm`:

Exact text from the [after-fix screenshot](crm-after-fix.png):

Weekly review as of 2026-02-15: 2 consenting customers meet the regular-visit rule in their recorded history. 1 regular has gone at least 21 days without a visit and have follow-up drafts ready for staff review. The catering window starting 2026-02-14 18:00 has 3 bookings, above the limit of 2. The quieter observed window starting 2026-02-14 14:00 is a possible alternative; staff should confirm availability. All messages remain drafts; nothing has been sent.

Yes: the brief is a plain-language paragraph, not a chart. Code location: `docker/app/crm_copilot.py`, `narrative_brief()` and its `run()` return field. Output location: `docker/app/app.py`, `crm()` renders `<p>{{narrative_brief}}</p>` in the **Weekly owner brief** card directly below the page title and before the tables at `/crm`. This makes it the primary owner-facing output. The transcription preserves the displayed wording.
