"""Pho65 Week 5: CRM co-pilot -- regulars, capacity, follow-up, narrative brief.

CSV reading happens in load_records; calculations return data without changing
the source records. Both the CLI and the Flask /crm route use run().

Consent boundary (load-bearing, do not relax): a record can only ever
contribute to `regular_status` when `opted_in` is true. Do not add a
send_email / send_sms / auto-dispatch function anywhere in this module --
draft messages must be plain strings labeled DRAFT -- NOT SENT and nothing
may transmit them.
"""
import csv
from collections import defaultdict
from datetime import datetime, timedelta

# Class defaults -- justify your own values in the workbook if you change these.
VISIT_FREQUENCY_THRESHOLD = 3      # visits...
VISIT_FREQUENCY_WINDOW_DAYS = 14   # ...within this many days => regular_status
LAPSED_WINDOW_DAYS = 21            # no visit in this many days => lapsed regular
CAPACITY_THRESHOLD = 2             # more than this many catering bookings...
SLOT_BUCKET_HOURS = 2              # ...in one bucket of this many hours => over capacity

DATE_FMT = "%Y-%m-%d"
SLOT_FMT = "%Y-%m-%d %H:%M"


def load_records(csv_path):
    """Load the seed CSV into a list of dicts with parsed types.

    Each dict should have: record_id, customer_name, phone_number (str,
    possibly empty), opted_in (bool), visit_date (datetime), order_type
    (str), catering_slot (datetime or None if the row isn't a catering row).
    """
    records = []
    required = {
        "record_id", "customer_name", "phone_number", "opted_in",
        "visit_date", "order_type", "catering_slot",
    }
    with open(csv_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("The seed CSV is missing required columns.")

        for row in reader:
            if None in row or any(row[column] is None for column in required):
                raise ValueError(
                    f"CSV row ending at line {reader.line_num}: incomplete or extra cells."
                )
            consent = row["opted_in"]
            if consent not in ("true", "false"):
                raise ValueError(
                    f"{row['record_id']}: opted_in must be true or false."
                )

            slot = None
            if row["order_type"] == "catering":
                if not row["catering_slot"]:
                    raise ValueError(
                        f"{row['record_id']}: catering booking has no slot."
                    )
                slot = datetime.strptime(row["catering_slot"], SLOT_FMT)
            elif row["catering_slot"]:
                raise ValueError(
                    f"{row['record_id']}: non-catering row has a catering slot."
                )

            records.append({
                "record_id": row["record_id"],
                "customer_name": row["customer_name"],
                "phone_number": row["phone_number"],
                "opted_in": consent == "true",
                "visit_date": datetime.strptime(row["visit_date"], DATE_FMT),
                "order_type": row["order_type"],
                "catering_slot": slot,
            })
    return records


def eligible_records(records):
    """Return only records that may ever be considered for regular_status.

    Consent-first rule: a record is eligible only if it has a phone number
    AND opted_in is true. Everything else is "not eligible," never "not a
    regular" -- do not silently treat exclusion as a negative computation.
    """
    return [
        record for record in records
        if record["phone_number"].strip() and record["opted_in"]
    ]


def group_by_phone(records):
    """Group a list of records into {phone_number: [records]}."""
    groups = defaultdict(list)
    for record in records:
        groups[record["phone_number"]].append(record)
    return dict(groups)


def has_three_in_window(visit_dates, window_days=VISIT_FREQUENCY_WINDOW_DAYS,
                         threshold=VISIT_FREQUENCY_THRESHOLD):
    """Return True if any window_days-wide window contains >= threshold visits."""
    dates = sorted(visit_dates)
    window = timedelta(days=window_days)
    for start in range(len(dates) - threshold + 1):
        end = start + threshold - 1
        if dates[end] - dates[start] <= window:
            return True
    return False


def compute_regular_status(records, as_of):
    """Compute regular_status per phone number.

    Returns (result, excluded_non_opted_in) where result is
    {phone_number: {name, visit_count, last_visit, is_regular}} and
    excluded_non_opted_in is the list of non-opted-in records that would
    have satisfied the frequency rule anyway (the consent-leakage check --
    this is deliberately narrower than "every opted_in=false record").
    """
    result = {}
    excluded_non_opted_in = []
    history = [record for record in records if record["visit_date"] <= as_of]

    for phone, customer_records in group_by_phone(history).items():
        if not phone.strip():
            continue

        # With conflicting consent on the same day, an opt-out takes precedence.
        latest = max(
            customer_records,
            key=lambda record: (record["visit_date"], not record["opted_in"]),
        )

        # Audit frequency without consent separately from actual status flags.
        all_dates = [record["visit_date"] for record in customer_records]
        if has_three_in_window(all_dates):
            excluded_non_opted_in.extend(
                record for record in customer_records if not record["opted_in"]
            )
        if not latest["opted_in"]:
            continue

        visits = eligible_records(customer_records)
        dates = [record["visit_date"] for record in visits]
        result[phone] = {
            "name": latest["customer_name"],
            "visit_count": len(visits),
            "last_visit": max(dates),
            "is_regular": has_three_in_window(dates),
        }
    return result, excluded_non_opted_in


def lapsed_followup_queue(regular_status, as_of, lapsed_days=LAPSED_WINDOW_DAYS):
    """Return customers who WERE flagged regular and haven't visited in lapsed_days+."""
    queue = []
    for phone, customer in regular_status.items():
        days_since_visit = (as_of - customer["last_visit"]).days
        if customer["is_regular"] and days_since_visit >= lapsed_days:
            queue.append({
                **customer,
                "phone_number": phone,
                "days_since_visit": days_since_visit,
            })
    return sorted(
        queue,
        key=lambda customer: (-customer["days_since_visit"], customer["phone_number"]),
    )


def slot_bucket(dt, bucket_hours=SLOT_BUCKET_HOURS):
    """Round a datetime down to its bucket_hours-wide window, anchored at midnight."""
    return dt.replace(
        hour=(dt.hour // bucket_hours) * bucket_hours,
        minute=0, second=0, microsecond=0,
    )


def capacity_view(records, threshold=CAPACITY_THRESHOLD):
    """Return a list of {bucket_start, count, over_capacity, records} for catering rows."""
    buckets = defaultdict(list)
    # Every catering booking consumes capacity, regardless of consent.
    for record in records:
        if record["order_type"] == "catering":
            if record["catering_slot"] is None:
                raise ValueError("A catering booking is missing its slot.")
            buckets[slot_bucket(record["catering_slot"])].append(record)
    return [
        {
            "bucket_start": start,
            "count": len(bookings),
            "over_capacity": len(bookings) > threshold,
            "records": bookings,
        }
        for start, bookings in sorted(buckets.items())
    ]


def suggest_alternate_slot(capacity, over_capacity_bucket):
    """Return the same-day bucket with the lowest booking count, excluding the overbooked one."""
    candidates = [
        bucket for bucket in capacity
        if bucket["bucket_start"].date() == over_capacity_bucket.date()
        and bucket["bucket_start"] != over_capacity_bucket
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda bucket: (bucket["count"], bucket["bucket_start"]),
    )["bucket_start"]


def _available_alternate_slot(capacity, bucket_start):
    """Check room for one moved booking after ranking the observed slots."""
    alternate = suggest_alternate_slot(capacity, bucket_start)
    for bucket in capacity:
        if bucket["bucket_start"] == alternate:
            if bucket["count"] + 1 <= CAPACITY_THRESHOLD:
                return alternate
    return None


def draft_message(customer_name, reason):
    """Return a labeled draft string. NEVER send it -- do not add a transport call here."""
    return (
        f"DRAFT -- NOT SENT\n"
        f"Hi {customer_name}, {reason}\n"
        "Best wishes, the Pho65 team"
    )


def narrative_brief(regular_status, followup_queue, capacity, as_of):
    """Return one plain-language paragraph summarizing regulars, follow-ups, and capacity."""
    regular_count = sum(
        customer["is_regular"] for customer in regular_status.values()
    )
    conflicts = [bucket for bucket in capacity if bucket["over_capacity"]]
    sentences = [
        f"Weekly review as of {as_of.strftime(DATE_FMT)}: "
        f"{regular_count} consenting "
        f"{'customer meets' if regular_count == 1 else 'customers meet'} the regular-visit rule "
        "in their recorded history.",
        f"{len(followup_queue)} "
        f"{'regular has' if len(followup_queue) == 1 else 'regulars have'} gone at least "
        f"{LAPSED_WINDOW_DAYS} days without a visit and have follow-up "
        "drafts ready for staff review.",
    ]
    if not conflicts:
        sentences.append("The booking data shows no catering capacity conflicts.")
    for bucket in conflicts:
        start = bucket["bucket_start"]
        sentences.append(
            f"The catering window starting {start.strftime(SLOT_FMT)} "
            f"has {bucket['count']} bookings, above the limit of "
            f"{CAPACITY_THRESHOLD}."
        )
        alternate = _available_alternate_slot(capacity, start)
        if alternate is None:
            sentences.append(
                "No observed same-day alternative has room for another booking."
            )
        else:
            sentences.append(
                f"The quieter observed window starting {alternate.strftime(SLOT_FMT)} "
                "is a possible alternative; staff should confirm availability."
            )
    sentences.append("All messages remain drafts; nothing has been sent.")
    return " ".join(sentences)


def run(csv_path, as_of):
    """Wire the pieces above together. Returns a dict with all the fields the
    /crm route needs to render: regular_status, excluded_non_opted_in_count,
    excluded_non_opted_in, followup_queue, capacity, drafts, narrative_brief.
    """
    records = load_records(csv_path)
    regular_status, excluded = compute_regular_status(records, as_of)
    followup_queue = lapsed_followup_queue(regular_status, as_of)
    capacity = capacity_view(records)
    for bucket in capacity:
        bucket["alternate_slot"] = (
            _available_alternate_slot(capacity, bucket["bucket_start"])
            if bucket["over_capacity"] else None
        )
    drafts = [
        {
            "phone_number": customer["phone_number"],
            "text": draft_message(
                customer["name"],
                "we haven't seen you at Pho65 for a while and would love "
                "to welcome you back whenever it suits you.",
            ),
        }
        for customer in followup_queue
    ]
    return {
        "regular_status": regular_status,
        "excluded_non_opted_in_count": len(excluded),
        "excluded_non_opted_in": excluded,
        "followup_queue": followup_queue,
        "capacity": capacity,
        "drafts": drafts,
        "narrative_brief": narrative_brief(
            regular_status, followup_queue, capacity, as_of
        ),
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "/data/pho65-week5-seed.csv"
    as_of = datetime.strptime(sys.argv[2], DATE_FMT) if len(sys.argv) > 2 else datetime(2026, 2, 15)
    result = run(path, as_of)
    print(result)
