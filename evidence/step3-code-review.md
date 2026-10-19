# Step 3: Detailed code review

Review date: October 17, 2026.

Browser evidence update: the user's subsequent [after-fix screenshot](crm-after-fix.png) confirms the corrected normal `/crm` display, including Anh's queue entry and draft. Automated Flask and inventory runtime checks remain unverified. References below to unavailable browser evidence describe earlier checkpoints.

Subsequent data correction: after the original implementation and before-fix screenshot, the user explicitly approved changing R014's phone to `555-203-0003`. This correction is now applied and verified by a CLI rerun and 15 passing CRM tests. References below to preserving the original inconsistent seed describe the earlier review checkpoint. See [before/after evidence](known-answer-test.md).

## Implementation update after approval

The user subsequently approved implementation and checks with “ok do it.” The reviewed functions and Flask route are now implemented. Both recommended corrections below are applied: malformed-row validation and separate alternate-slot ranking/feasibility. A small shared helper, `_available_alternate_slot`, calls the ranking function, checks whether adding one booking stays within the Step 1 limit, and returns a datetime or `None`; both `run` and `narrative_brief` use that same check. Brief wording handles singular counts.

Fourteen CRM tests passed. All 18 existing Flask functions are unchanged by syntax-tree comparison, and all 12 supplied CRM signatures are preserved. Flask runtime tests, the inventory test, and the Docker rebuild remain unverified because Docker is unavailable in this shell and the dependency download was not approved. The seed CSV is byte-for-byte unchanged. See [verification results](step3-verification.md).

The remaining sections preserve the original pre-execution review and its proposed decisions as a historical record. Statements below about pending implementation or execution describe that earlier checkpoint, not the current state.

## Scope and status

This is a static, statement-by-statement review of the implementation proposed in this chat, including its Flask integration. The files on disk still contain the original CRM skeleton and route placeholder. No implementation, imports, tests, container rebuilds, or message transmission were executed for this review. Only this document and Workbook Section 3 were edited.

Accepted means recommended by the reviewing agent, not approval attributed to the student. Edited means a revision is recommended below and awaits approval. Rejected means a prohibited action, not a claim that such code was proposed. These notes are not test evidence.

The tables follow source order. Multiline expressions, dictionary entries, and template branches are reviewed together where they perform one operation. Blank lines and closing delimiters have no independent behavior. References name exact functions and statements because the proposed implementation has not been saved and therefore has no reliable file line numbers.

## Existing imports, constants, signatures, and entry point

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| `import csv` | Accept | Standard-library CSV reader; no network activity. |
| `from collections import defaultdict` | Accept | Simple grouping without shared global state. |
| `from datetime import datetime, timedelta` | Accept | Parses dates and compares elapsed days. |
| Frequency constants: `3`, `14` | Accept | Match Workbook Section 1. |
| Lapse constant: `21` | Accept | Matches Workbook Section 1; equality qualifies. |
| Capacity constants: `2`, `2` | Accept | More than two bookings per midnight-anchored two-hour bucket. |
| `DATE_FMT`, `SLOT_FMT` | Accept | Match the provided CSV formats. |
| All supplied function signatures | Accept | Preserve names, arguments, defaults, and required return fields. |
| Existing `if __name__ == "__main__"` block | Accept | Parses optional arguments, calls `run`, and prints results only when invoked directly. Not invoked during review. |
| Existing Flask import and CRM environment variables | Accept | Already present; no dependency or deployment configuration changes needed. |

## `load_records(csv_path)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| `records = []` | Accept | New result list for each call. |
| `required = {...}` | Accept | Includes all seven supplied columns. |
| `open(..., newline="", encoding="utf-8-sig")` | Accept | Read-only access; handles a UTF-8 byte-order mark. |
| `reader = csv.DictReader(source)` | Accept | Uses column names rather than fragile positions. |
| Required-header subset check and `ValueError` | Accept | Missing columns produce a clear error. Extra named columns are ignored. |
| `for row in reader` | Edit | Add a structural check before reading cells; short rows produce `None`, and extra cells use a `None` key. |
| `consent = row["opted_in"]` | Accept | Reads the provided value without rewriting it. |
| Consent check and `ValueError` | Accept | Only literal `true` and `false` qualify; ambiguous values are rejected. |
| `slot = None` | Accept | Non-catering rows have no parsed catering slot. |
| Catering branch and missing-slot error | Accept | A catering booking must specify a slot. |
| `datetime.strptime(..., SLOT_FMT)` | Accept | Invalid slot dates raise an error rather than being guessed. |
| Non-catering slot check and error | Accept | Reports contradictory source data; does not silently discard it. |
| Dictionary string fields | Accept | Preserve record ID, name, phone, and order type exactly. No name-based merge or phone correction. |
| `"opted_in": consent == "true"` | Accept | Produces a real Boolean after validation. |
| Parsed `visit_date` | Accept | Invalid dates raise `ValueError`. |
| Parsed `catering_slot` | Accept | Returns a datetime or `None`, as required. |
| `records.append(...)`, `return records` | Accept | Returns parsed records without changing the source CSV. |

Recommended insertion at the start of the row loop:

``` python
if None in row or any(row[column] is None for column in required):
    raise ValueError(
        f"CSV row ending at line {reader.line_num}: incomplete or extra cells."
    )
```

This prevents an incomplete phone cell from reaching `.strip()` and producing an unhandled `AttributeError`. A deliberately empty phone cell remains `""` and is handled as not eligible. This revision is documentation only and has not been applied.

## `eligible_records(records)` and `group_by_phone(records)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Eligible-record list comprehension | Accept | Builds a new list; does not modify records. |
| `phone_number.strip()` condition | Accept | Rejects empty or whitespace-only phones. Uses stripping only to test presence; does not normalize the matching key. |
| `and record["opted_in"]` | Accept | Explicit consent is mandatory for frequency calculations. |
| `groups = defaultdict(list)` | Accept | Creates an independent customer grouping. |
| Loop and `groups[phone].append(record)` | Accept | Uses exact phone strings. Same names under different numbers remain separate. |
| `return dict(groups)` | Accept | Returns the requested ordinary dictionary. Callers handle consent and missing phones. |

## `has_three_in_window(...)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| `dates = sorted(visit_dates)` | Accept | Orders a copy; input ordering cannot change the answer. |
| `window = timedelta(days=window_days)` | Accept | Uses the supplied window argument. |
| `range(len(dates) - threshold + 1)` | Accept | Checks each possible group; fewer than three visits produces no iterations. |
| `end = start + threshold - 1` | Accept | Selects the third visit for the default threshold. |
| Date span `<= window` | Accept | Exactly 14 elapsed days qualifies. This is the explicit boundary interpretation for Step 1. |
| `return True`, final `return False` | Accept | Any historical qualifying window is enough; this supports lapsed regulars. |

Each CSV row is treated as a visit. Multiple rows on one date count separately. The supplied positive thresholds are assumed; this prototype does not add configurable-input validation.

## `compute_regular_status(records, as_of)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Empty result dictionary and audit list | Accept | Separates eligible customer status from excluded-record evidence. |
| History filter `visit_date <= as_of` | Accept | Future visits cannot establish historical regular status or change historical consent. The report uses the supplied date at midnight. |
| Group-history loop | Accept | Keeps exact phone identities separate. |
| Missing-phone check and `continue` | Accept | Missing-phone rows receive no status flag. |
| Latest-record `max(...)` | Accept | Most recent visit date governs current consent. |
| Secondary key `not record["opted_in"]` | Accept | With conflicting consent on the same date, opt-out wins. The CSV has no finer timestamp. |
| `all_dates` and frequency-only audit check | Accept | Calculates the requested leakage check separately; it never assigns regular status. |
| Audit `extend` for non-opted-in rows | Accept | Counts non-consenting records belonging to a phone group that meets frequency without consent filtering. It does not count every opt-out in the file. |
| Latest opt-out check and `continue` | Accept | Revoked consent excludes the whole phone group from status and follow-up. Earlier opt-ins do not override it. |
| `visits = eligible_records(customer_records)` | Accept | Non-consenting visits never contribute to the actual regular flag. |
| Eligible date list | Accept | A currently consenting group has at least its latest consenting visit, so the list is nonempty. |
| `name` from latest record | Accept | Shows the current recorded name without merging identities. |
| `visit_count = len(visits)` | Accept | Counts all eligible historical visits, not just the qualifying window. UI labels it accordingly. |
| `last_visit = max(dates)` | Accept | Uses only eligible visits for an eligible customer. |
| `is_regular = has_three_in_window(dates)` | Accept | Historical frequency supports later lapse detection. |
| Tuple return | Accept | Preserves the supplied return contract. |

An excluded customer is absent from the status mapping, not assigned `is_regular=False`. A consenting customer below the frequency threshold can receive `False`.

## `lapsed_followup_queue(...)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Empty queue and customer loop | Accept | Works from consent-filtered status only. |
| `(as_of - last_visit).days` | Accept | Calculates elapsed whole days. |
| `is_regular and days_since_visit >= lapsed_days` | Accept | Requires both historical regular status and the full lapse threshold. Exactly 21 days qualifies. |
| Queue dictionary expansion | Accept | Adds phone and elapsed days without mutating the customer mapping. |
| Sorting by negative days, then phone | Accept | Longest-lapsed first; deterministic ordering for ties. |

## `slot_bucket(...)` and `capacity_view(...)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Hour calculation `(dt.hour // bucket_hours) * bucket_hours` | Accept | Floors to a midnight-anchored bucket. 18:45 and 19:30 both map to 18:00. |
| Zero minute, second, microsecond | Accept | Makes equivalent buckets share an identical datetime key. |
| `buckets = defaultdict(list)` | Accept | Groups bookings by date and bucket, not by time alone. |
| Catering-only condition | Accept | Dine-in and takeout do not consume catering slots. |
| Missing-slot check | Accept | Direct function callers receive a clear error even without CSV parsing. |
| Bucket append | Accept | Includes consenting and non-consenting bookings equally in kitchen workload. |
| Sorted bucket comprehension | Accept | Stable chronological output. |
| `bucket_start`, `count`, `records` fields | Accept | Preserve the required result structure and supporting source records. |
| `len(bookings) > threshold` | Accept | Exactly two bookings is allowed; three is a conflict. Uses the function argument. |

Capacity intentionally covers all catering records supplied, including future bookings; the customer-history `as_of` filter does not remove operational bookings. The brief describes these as booking-data counts, not as bookings placed during the report week.

## `suggest_alternate_slot(...)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Candidate list from existing capacity buckets | Accept | Uses observed slots; no unsupported opening hours are invented. |
| Same-date condition | Accept | Alternative remains on the requested day. |
| Exclude the overbooked bucket | Accept | Cannot suggest the conflicting bucket itself. |
| `bucket["count"] < CAPACITY_THRESHOLD` | Edit | Mixes ranking with feasibility and hard-codes the default even if `capacity_view` used a different threshold. |
| Empty candidates return `None` | Accept | Handles a day without an observed alternative. |
| Minimum by count, then start time | Accept | Selects lowest historical traffic; earliest start breaks ties. |
| Return `bucket_start` | Accept | Returns a specific datetime for the interface. |

Recommended revision: remove the threshold filter from this helper so it follows its supplied signature and docstring: return the lowest-count observed same-day alternative. In `run()` and `narrative_brief()`, check that the selected bucket has room for one more booking under the Step 1 threshold before presenting it as actionable. Use the same check in both places; show no available observed alternative if it fails. Retain all supplied signatures. This revision has not been applied.

Unobserved buckets are not assumed to be open or empty. The suggestion is a candidate for staff review, not a reservation or schedule change.

## `draft_message(...)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| `DRAFT -- NOT SENT` prefix | Accept | Exact required label appears in every message. |
| Name, supplied reason, and café sign-off | Accept | Produces plain text; includes no unapproved offer or discount. |
| String return | Accept | No transport call, API, outbox, or sending function. |

## `narrative_brief(...)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Sum `is_regular` | Accept | Counts qualified consenting customers, not visit rows. |
| Conflict list | Accept | Uses the capacity flags already calculated. |
| Review date sentence | Accept | Labels the report date and historical qualification clearly. |
| Follow-up count sentence | Accept | Identifies regulars at risk using the 21-day threshold. |
| No-conflicts branch | Accept | Gives a useful result for empty or within-capacity data. |
| Conflict loop, start, count, and threshold sentence | Accept | Names the specific booking window and overload. |
| Alternate lookup and branch | Edit | Apply the feasibility check described above before calling a ranked alternative available. |
| Alternative sentence and staff confirmation | Accept | Names a quieter observed slot and leaves scheduling to staff. |
| Draft-only final sentence | Accept | Matches the proposed execution paths. |
| `" ".join(sentences)` | Accept | Produces the required single plain-language paragraph. |

This is a weekly review snapshot of historical customer behavior and supplied booking data. It does not claim the historical regular count is a count of visits made this week. Slow-slot suggestions appear when a conflict needs an alternative.

## `run(csv_path, as_of)`

| Statement | Decision | Review |
|------------------------|------------------------|------------------------|
| Load records | Accept | Reads the seed once per call. |
| Compute status and excluded audit | Accept | Keeps consent decisions in the dedicated function. |
| Build follow-up queue | Accept | Uses only computed eligible status. |
| Build capacity view | Accept | Uses all bookings, independent of consent. |
| Capacity loop and conditional alternative assignment | Edit | Add the separate feasibility check noted above; keep the extra field additive to the required capacity structure. |
| Draft list over queue | Accept | Exactly one draft per lapsed eligible customer; none for excluded customers. |
| Phone field and `draft_message(...)` call | Accept | Makes staff review possible without sending anything. |
| Follow-up reason text | Accept | Friendly invitation; no automatic discount or promise. |
| Seven returned fields | Accept | Matches the starter's required Flask inputs, including both audit count and audit records. |
| `len(excluded)` | Accept | Counts records, not distinct customers. |
| Narrative call | Accept | Uses the same calculated status, queue, and capacity. |

Only locally created output dictionaries are enriched. Input records and source files remain unchanged. `load_records` is the intentional file-reading boundary; the computation functions do not perform I/O.

## Flask integration and template

| Statement or template line | Decision | Review |
|------------------------|------------------------|------------------------|
| Navigation link to `/crm` | Accept | Adds access through the shared navigation without changing existing route logic. |
| `@app.route("/crm")`, `def crm()` | Accept | Adds a GET page; no POST or send endpoint. |
| `try` and parsing `CRM_AS_OF` | Accept | Invalid configuration reaches the clear data-error page. |
| `crm_copilot.run(CRM_SEED_CSV, as_of)` | Accept | Uses the existing environment configuration and provided entry point. |
| `except FileNotFoundError` and HTTP 404 | Accept | Displays an actionable seed-path and volume-mount explanation. |
| `except (ValueError, csv.Error)` and HTTP 400 | Accept | Displays parsing and validation problems rather than silently fixing them. |
| Error text passed as template context | Accept | Rendered by the existing template helper with escaping. |
| Heading and owner-brief card | Accept | Makes the plain-language paragraph the primary output. |
| Exact-phone and exclusion hint | Accept | Explains identity preservation and eligibility. |
| Excluded count and explanatory text | Accept | Makes the narrower frequency-qualified audit count explicit. |
| Eligible-customer table header | Accept | Distinguishes eligible visits from total source rows. |
| Status loop and name/phone cells | Accept | Iterates only the consent-filtered mapping; values remain escaped. |
| Visit count and formatted last date | Accept | Uses the typed status fields. |
| Regular/frequency-threshold conditional | Accept | Uses a negative frequency label only for eligible customers. |
| Empty eligible-table branch | Accept | Keeps a valid, understandable empty state. |
| Capacity heading and two-hour explanation | Accept | Explains bucket size and consent-independent workload. |
| Capacity table loop, formatted start, and count | Accept | Shows chronological bucket results. |
| Capacity-status conditional | Accept | Clearly distinguishes an overload. |
| Alternate-slot conditional and formatted datetime | Accept | Displays the reviewed feasible suggestion supplied by `run`. |
| Staff-confirmation text | Accept | Does not claim availability is guaranteed. |
| No-alternative, within-capacity, and empty-table branches | Accept | Handle all result states without inventing bookings. |
| Follow-up loop and elapsed-day text | Accept | Shows only actual queue entries. |
| Empty follow-up branch | Accept | Explicitly allows an empty queue under the current matching rule. |
| Draft loop and phone display | Accept | Identifies each draft for staff review. |
| `white-space:pre-wrap` text paragraph | Accept | Preserves draft line breaks without marking customer content as safe HTML. |
| Empty draft branch | Accept | Does not manufacture messages to fill the page. |
| `page(..., **result)` | Accept | Reuses the existing presentation helper. No inventory transaction or schema changes. |

The existing helper renders escaped customer values in the inner template, then inserts the rendered page body into the outer layout. No new `safe` filter is proposed for raw customer values. Existing `/`, inventory, scanning, label, transaction, and health route logic remains untouched. Runtime regression behavior has not been verified.

## Seed-data review and prohibited changes

| Item | Decision | Reason |
|------------------------|------------------------|------------------------|
| Keep Anh Nguyen's two phone numbers separate | Accept | R013/R015 use `555-203-0003`; R014 uses `555-203-0009`. Exact-phone matching must preserve this inconsistency. |
| Automatic phone correction or name-based merging | Reject as a boundary | Would hide the seeded data problem; no such correction was included in the proposed code. |
| Automatic email, SMS, push, or other message dispatch | Reject as a boundary | Messages must remain drafts; no sending code was included in the proposal. |
| Membership enrollment | Reject as a boundary | Outside this project's scope. |
| Changes to Week 3/4 route logic or the inventory database | Reject as a boundary | Preserve existing features and ledger history. |

## Predictions from manual inspection only

| Output | Prediction | Reason |
|------------------------|------------------------|------------------------|
| Over-capacity bucket | February 14, 2026, 18:00–20:00; 3 bookings | R016, R017, and R018 share the midnight-anchored bucket. |
| Alternative | February 14, 2026, 14:00–16:00; 1 booking | R019 is the quieter observed same-day bucket and has room for one additional booking. |
| Regular customers | Mai Tran qualifies | Consenting history contains qualifying 14-day windows. |
| Consent audit | 4 non-opted-in records | Linh Pham's R009–R012 meet frequency without consent; Ben Tran's spaced visits do not. |
| Follow-up queue and drafts | Empty with the unchanged seed | Mai visited recently; Anh's split identities do not individually reach three visits. |

These are predictions, not observed results. Workbook Section 4 and test-evidence files have not been filled with invented outputs.

## Checks pending approval

Before implementation, check the existing Week 3/4 pages to establish their current baseline. After applying reviewed code, verify consent revocation, same-day consent conflicts, missing phones, future visits, the 14-day frequency boundary, the 21-day lapse boundary, exact phone grouping, malformed CSV rows, catering bucket boundaries, alternate ranking and feasibility, missing-file handling, and draft labels. Use fabricated examples where the seed cannot exercise a rule.

Run the existing inventory test with an isolated temporary database, compare the old routes against their baseline, and rebuild only the app service. None of these checks has been run or reported as passing.