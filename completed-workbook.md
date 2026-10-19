# Week 5 Completed Workbook — Pho65 CRM Co-Pilot

Type your team's actual answers directly into this file as you work through `week5-project-assignment.qmd` (rendered as `START-HERE.html`). This is your one editable workbook — the rendered `week5-student-workbook.html` is a reference copy of the same questions, not a second place to answer them.

## Evidence Routing Table

| Workbook section | Summarize here | Full detail goes in |
|------------------------|------------------------|------------------------|
| Section 0 (Regression) | Pass/fail + one-line result for each check | `evidence/regression-check.md` |
| Section 1 (Schema) | Your definitions, matching rule, thresholds | (this file only) |
| Section 2 (Plan review) | Plan summary + reject/accept decision | `ai-use-log.md` (full prompt/response) |
| Section 3 (Build log) | Component-by-component decision table | `evidence/step3-code-review.md` |
| Section 4 (Known-answer test) | Prediction/observed/diagnosis/fix summary | `evidence/known-answer-test.md` (full table) |
| Section 5 (Innovation evidence) | Where each requirement lives, key numbers | `evidence/consent-and-capacity.md` |
| Section 6 (Manager README draft) | Draft text | `README.md` (final) |
| Section 7 (Reflection) | Your answers | (this file only) |
| ADI501 sections | Summary + thresholds | `evidence/roi-risk-memo.md`, `stakeholder-support.md`, `build-vs-buy.md`, `pilot-memo.md` |

## Section 0: Regression Check (Before You Build Anything New)

**0.1** Before touching `app.py`, what did `http://localhost:5050/` show?

Pho65 order tracker (Week 3 regression)

**0.2** Before touching `app.py`, what did `http://localhost:5050/inventory` show?s

Empty inventory table.

## Section 1: Schema Worksheet

**1.1** In your own words, what is the difference between `regular_status` and `member_status`?

`regular_status`: Computed from visit frequency for customers with a phone number who opted in.

`member_status`: Set only when a customer explicitly signs up for membership; this project does not build membership.

**1.2** Write your exact "same customer" matching rule: *(e.g., "same phone_number AND opted_in=true on the most recent record for that number")*

Two orders belong to the same customer only if they share the same `phone_number` and the most recent record has `opted_in = true`. Records with no phone number or `opted_in = false` are “not eligible” and never receive a `regular_status` flag.

**1.3** Your thresholds and justification:

| Threshold | Value | Justification |
|----------------------------------|-------------------|-------------------|
| Visit frequency for `regular_status` | 3+ visits in 14 days | This identifies eligible customers who visit frequently within two weeks. |
| Lapsed-regular window (narrative brief) | No visit in 21+ days | Three weeks without a visit signals that a previously regular customer may need follow-up. |
| Capacity limit per time slot | More than 2 catering bookings in one 2-hour window | This flags busy periods for demand shaping, including the 3 seed bookings on February 14, 2026, from 18:00 to 20:00. |

## Section 2: Agent Plan Review

**2.1** Summarize the agent's proposed plan for the co-pilot.

Keep the proposed CSV loading, consent-based regular flags, lapsed follow-up queue, 2-hour capacity checks, unsent drafts, and narrative brief in `crm_copilot.py`, displayed through a new `/crm` route.

**2.2** Does the plan include any auto-send step? (It must not.) How did you confirm this?

No; the plan explicitly labels messages “DRAFT — NOT SENT” and includes no sending function, and review of all seven steps found no auto-send action (implementation still needs verification).

**2.3** What did you change in the plan before approving it, and why?

Accept the structure with an explicit constraint: add `/crm` without changing existing routes, including `/`, `/inventory`, and `/inventory/scan`; reject any future auto-send step or edits to Week 3/4 route logic to preserve human control and existing workflows (neither was proposed in this plan).

## Section 3: Build Log

Reviewed before execution; user approved implementation and checks on October 17, 2026. Both proposed corrections are now applied.

| Component | Decision (accepted as-is / edited / rejected) | Reason |
|------------------------|------------------------|------------------------|
| Data loading | Edited | Reject incomplete rows clearly; preserve seed values. |
| `regular_status` computation | Accepted as-is | Exact phone; latest consent; 3 visits within 14 days. |
| Capacity check | Edited | Count all bookings; separate slot ranking from capacity checks. |
| Lapsed follow-up queue | Accepted as-is | Historical regular; absent 21+ days. |
| Draft-message generation | Accepted as-is | Labeled drafts; no sending code. |
| Narrative brief | Accepted as-is | One paragraph; historical counts and suggested action. |
| Flask integration | Accepted as-is | Add `/crm` and navigation; preserve existing routes. |

Detailed review: [Step 3 code review](evidence/step3-code-review.md). Verification: [Step 3 results](evidence/step3-verification.md). No proposed code was rejected outright; automatic sending and silent identity correction remain prohibited.

## Section 4: Known-Answer Test

**4.1** Prediction (before running, capacity only):

- Expected over-capacity day/slot: Saturday, February 14, 2026, 18:00–20:00.
- Expected count in that slot: 3 bookings (R016, R017, R018), exceeding the limit of 2.

Prediction first stated in chat before execution; transcribed here after the run.

**4.2** Observed result (first run):

- Actual over-capacity flag output: February 14, 2026, 18:00–20:00: 3 bookings, flagged OVER CAPACITY. Suggested alternative: 14:00–16:00, with 1 booking.
- Actual follow-up queue output: Empty; no lapsed regulars or follow-up drafts. The supplied `/crm` screenshot confirms both results.

**4.3** Diagnosis: data / logic / interface issue? Explain how you determined this.

Data issue: Anh Nguyen's visits are split between `555-203-0003` (R013, R015) and `555-203-0009` (R014). The screenshot shows separate histories of 2 and 1 visits; neither meets the 3-visit threshold. Combined, the opted-in visits span January 5–15, within 14 days, and the last visit is 31 days before February 15. Exact-phone grouping correctly preserves the inconsistent keys; the interface displays that result.

**4.4** Fix applied (smallest correction):

With user approval, changed only R014's phone number from `555-203-0009` to `555-203-0003`. Thresholds and grouping logic are unchanged.

**4.5** Observed result (after fix):

The command-line rerun and [after-fix browser screenshot](evidence/crm-after-fix.png), both using report date February 15, 2026, show Anh with 3 eligible visits, regular status, and a 31-day lapse. The queue contains Anh and one DRAFT -- NOT SENT message. Catering remains 3 bookings at 18:00–20:00, with 14:00–16:00 suggested; 4 non-opted-in records remain excluded. All 15 CRM tests passed.

**4.6** Does the re-run now match what you expected? If not, explain the remaining gap.

Yes: the CLI result and after-fix screenshot match the expected regular flag, 31-day lapse, single unsent draft, and unchanged capacity result. Both [before](evidence/crm-before-fix.png) and [after](evidence/crm-after-fix.png) screenshots are saved. Full evidence: [known-answer test](evidence/known-answer-test.md). The user's subsequent terminal screenshot confirms the inventory suite passed; automated CRM Flask tests remain unverified.

## Section 5: Innovation Requirements Evidence

All three requirements are present, confirmed by the code, recorded CRM tests, and [after-fix output](evidence/crm-after-fix.png). Exact counts and slots are also recorded in [consent-and-capacity evidence](evidence/consent-and-capacity.md).

**5.1** Consent-first regulars detection — where does this happen, and how many records were excluded?

Code: `docker/app/crm_copilot.py`, `eligible_records()` filters out missing phones and non-opted-in visits; `compute_regular_status()` also requires latest-record consent. `run()` returns `excluded_non_opted_in_count`. Output: `docker/app/app.py`, `crm()` displays the count under **Eligible customers** at `/crm`. Exactly **4** non-opted-in records (Linh Pham, R009–R012) were excluded despite meeting frequency: February 3, 6, 10, and 13 span 10 days. No non-consenting customer is flagged regular.

**5.2** Demand-shaping catering suggestion — name the request and the suggested alternate slot, and why.

Code: `docker/app/crm_copilot.py`, `capacity_view()` flags overloads, `suggest_alternate_slot()` selects the lowest-count observed same-day bucket, and `_available_alternate_slot()` checks room for one more booking. Output: `docker/app/app.py`, `crm()` shows the **Suggested alternative** column under **Catering capacity** at `/crm`. February 14, 2026, **18:00–20:00 has 3 bookings**; the exact suggestion is **February 14, 14:00–16:00, with 1 booking**. Staff must confirm availability.

**5.3** Weekly narrative brief — paste your co-pilot's generated paragraph.

Code: `docker/app/crm_copilot.py`, `narrative_brief()` builds one plain-language paragraph and `run()` returns it. Output: `docker/app/app.py`, `crm()` renders it in the **Weekly owner brief** card immediately below the page title, before the tables, making it the primary owner-facing output at `/crm`.

Transcribed exactly from the [after-fix screenshot](evidence/crm-after-fix.png):

Weekly review as of 2026-02-15: 2 consenting customers meet the regular-visit rule in their recorded history. 1 regular has gone at least 21 days without a visit and have follow-up drafts ready for staff review. The catering window starting 2026-02-14 18:00 has 3 bookings, above the limit of 2. The quieter observed window starting 2026-02-14 14:00 is a possible alternative; staff should confirm availability. All messages remain drafts; nothing has been sent.

## Section 6: Manager-Facing README (Draft)

Final owner guide: [README](README.md). Matching evidence copy: [manager README](evidence/manager-readme.md).

Three "what it does" bullets:

- Shows which customers who agreed to follow-ups visit regularly and which have not returned recently.
- Warns when a catering time is too busy and suggests a quieter time on the same day.
- Gives you a short weekly update and writes follow-up drafts for you to review.

"What it does not do" statement: It never sends messages, runs a membership program, or tracks visit habits for customers who have not agreed. All messages remain drafts. Every catering booking still counts toward kitchen workload.

One known limitation: A mistyped phone number can make a returning customer look like two different people, causing a missed follow-up.

One next-step recommendation: Ask staff to double-check the phone number when a customer agrees to follow-ups.

## Section 7: Reflection

**7.1** What would break first if Pho65 actually deployed this tool tomorrow?

The recommendations would become outdated first because the tool reads a manually updated CSV and uses a fixed February 15, 2026 report date. New visits, bookings, and changes in permission would not be reflected automatically, so the owner could see incorrect follow-up suggestions or miss a busy catering period. A real trial would need a reliable way to update the records and report date before each review.

**7.2** Name one other small business (not Pho65) where this same workflow could apply, and what would need to change.

A small hair salon could use this workflow to recognize consenting repeat clients, spot overdue appointments, and draft reminders. Replace café visits and catering bookings with appointment history and stylist availability, use service lengths to check overlapping appointments, and choose longer return intervals suited to haircuts. Keep permission checks and staff-reviewed drafts.

**7.3** Feynman check: explain your matching rule and consent-first design to someone with no technical background, in three sentences or fewer.

We recognize a returning customer by the same phone number, and their latest entry must say they agreed to follow-ups. Only visits recorded with that agreement count toward becoming a regular: at least three visits within fourteen days. People without a phone number or whose latest entry says they have not agreed are left out of regular-customer tracking.

------------------------------------------------------------------------

## ADI501 Extension Worksheet

**G.1 ROI and Risk Memo** — Estimated value (cite a real number from your run), and the main privacy/consent risk.

Across 29 transaction records (12 unique customers), the tool identified 2 active regulars and, after fixing row R014, surfaced 1 lapsed regular (Anh Nguyen, 31 days absent). Re-engaging 1 lapsed regular preserves \~\$1,800+ in annual revenue at \$0 recurring SaaS cost, while demand-shaping redirected an over-capacity Valentine's Day catering slot (`2026-02-14 18:00`, 3 orders) to 14:00. The primary privacy risk is that raw CSV logs still persist non-opted-in customer phone numbers and dining histories in plaintext; a future iteration must purge or hash phone numbers for non-opted-in visits after checkout.

**G.2 Stakeholder and Support-Burden Analysis**

| Stakeholder | How they use the tool | What happens when phone-matching fails for them |
|------------------------|------------------------|------------------------|
| Owner | Reads the weekly brief and reviews follow-up drafts to personally approve and send warm outreach texts. | If a phone typo splits a regular's visits (e.g. Anh Nguyen), the owner may mistakenly send a "we miss you" text to a guest who visited yesterday, damaging customer trust. |
| Counter staff | Collects 10-digit phone numbers and verbal consent (`opted_in`) during register checkout. | Lacks a real-time validation prompt to catch mistyped digits, leading to unprompted customer inquiries when loyalty visits fail to record. |
| Kitchen lead | Checks the catering capacity calendar on `/crm` to schedule prep tables and broth simmering. | If a customer splits an oversized catering order across two phone numbers to bypass capacity caps, the system fails to aggregate demand, risking sudden kitchen understaffing. |

**G.3 Build-vs-Buy Memo** — Named product compared: Square Loyalty. Recommendation and justification:

Recommendation: Build (Retain In-House Co-Pilot). Square Loyalty charges \$45/month (\$540/year) and stores customer data in a proprietary vendor cloud, yet it completely lacks kitchen capacity threshold management (2 bookings per 2-hour window) and demand-shaping alternate slot suggestions. Building in-house retains full local data sovereignty, saves recurring SaaS overhead, and integrates CRM directly with Pho65's kitchen throughput constraints.

**G.4 Pilot Recommendation** — Explicit continue/revise/stop thresholds for a 4-week trial:

- Continue if: Customer opt-in rate remains $\ge 45\%$, follow-up draft accuracy is $\ge 90\%$ (no more than 1 false lapsed alert per month), and $100\%$ of capacity alerts are successfully redirected without kitchen bottlenecks.
- Revise if: Opt-in rate is between $25\% - 44\%$, or 1–2 false lapsed alerts occur per month due to phone typos, or phone collection adds $>15$ seconds to checkout. (Action: add input validation and retrain staff).
- Stop if: Opt-in rate falls below $25\%$, any automated message is transmitted without manual owner review (zero-tolerance safety breach), or $\ge 2$ unflagged catering overages cause kitchen service failure.