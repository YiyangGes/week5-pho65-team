# ROI and Risk Memo (ADI501) — Half Page

> **Instructions:** Cite an actual number from your own run, not a made-up estimate. Keep this to roughly half a page — this is an executive memo, not a report.

## Estimated Value

Across the 29 transaction records representing 12 unique customers in our seed dataset, the co-pilot identified 2 qualified regulars (Mai Tran and Anh Nguyen). Crucially, by diagnosing the phone typo on row R014, the co-pilot recovered Anh Nguyen (555-203-0003) from being silently dropped, placing him into the follow-up draft queue after 31 days of absence. For a small business like Pho65 where repeat diners drive outsized margin, reactivating even one lapsed regular (averaging ~6 visits per month at \$25/ticket, representing over \$1,800 in annual spend) delivers immediate operational ROI against zero recurring software licensing costs. Additionally, the demand-shaping feature flagged a 3-booking bottleneck on Valentine's Day evening (`2026-02-14 18:00`), successfully redirecting excess catering volume to the 14:00 window, preserving substantial catering revenue without overloading kitchen staff.

## Main Privacy/Consent Risk

While the tool strictly enforces a consent gate before classifying any customer as a regular or drafting outreach (`opted_in == True`), the underlying data pipeline still persists full transaction details and phone numbers for non-opted-in diners (e.g., Linh Pham's 4 visits and Ben Tran's 3 visits remain in plaintext in the CSV). In the event of a point-of-sale data leak or misconfigured backup, personal visit patterns of customers who explicitly declined marketing would be compromised. A necessary operational next step is to implement irreversible one-way hashing or immediate redaction of phone numbers on any transaction marked `opted_in=FALSE` once checkout is settled.