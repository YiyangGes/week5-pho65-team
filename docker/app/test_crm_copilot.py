"""Run with: python -m unittest -v test_crm_copilot.py.

All test data and inventory writes use temporary files, never the live ledger.
"""
import csv
import importlib
import os
from pathlib import Path
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

import crm_copilot as crm


SEED = Path(os.environ.get(
    "CRM_SEED_CSV",
    Path(__file__).resolve().parent / "../../sample-data/pho65-week5-seed.csv",
)).resolve()
ORDERS = SEED.with_name("pho65-orders-valid.csv")
AS_OF = datetime(2026, 2, 15)
FIELDS = [
    "record_id", "customer_name", "phone_number", "opted_in",
    "visit_date", "order_type", "catering_slot",
]


def visit(day, phone="test-phone", consent=True, slot=None, name="Test Customer"):
    """A fabricated visit for rule checks, independent of the seed identities."""
    return {
        "record_id": "TEST",
        "customer_name": name,
        "phone_number": phone,
        "opted_in": consent,
        "visit_date": datetime.strptime(day, crm.DATE_FMT),
        "order_type": "catering" if slot else "dine_in",
        "catering_slot": datetime.strptime(slot, crm.SLOT_FMT) if slot else None,
    }


def write_csv(path, records):
    with open(path, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({
                **record,
                "opted_in": "true" if record["opted_in"] else "false",
                "visit_date": record["visit_date"].strftime(crm.DATE_FMT),
                "catering_slot": (
                    record["catering_slot"].strftime(crm.SLOT_FMT)
                    if record["catering_slot"] else ""
                ),
            })


class CRMTests(unittest.TestCase):
    def test_seed_types_and_identity_preservation(self):
        before = SEED.read_bytes()
        records = crm.load_records(SEED)
        self.assertEqual(len(records), 29)
        self.assertIs(records[0]["opted_in"], True)
        self.assertIs(records[8]["opted_in"], False)
        self.assertIsInstance(records[0]["visit_date"], datetime)
        self.assertIsNone(records[0]["catering_slot"])
        self.assertIsInstance(records[15]["catering_slot"], datetime)
        self.assertEqual(records[12]["phone_number"], records[13]["phone_number"])
        self.assertEqual(records[13]["phone_number"], records[14]["phone_number"])
        self.assertEqual(SEED.read_bytes(), before)

    def test_seed_known_answers(self):
        result = crm.run(SEED, AS_OF)
        regulars = result["regular_status"]
        self.assertEqual(
            [phone for phone, customer in regulars.items() if customer["is_regular"]],
            ["555-201-0001", "555-203-0003"],
        )
        self.assertEqual(regulars["555-201-0001"]["visit_count"], 8)
        self.assertEqual(result["excluded_non_opted_in_count"], 4)
        self.assertEqual(
            {record["record_id"] for record in result["excluded_non_opted_in"]},
            {"R009", "R010", "R011", "R012"},
        )
        self.assertNotIn("555-202-0002", regulars)
        self.assertNotIn("", regulars)
        self.assertEqual(regulars["555-203-0003"]["visit_count"], 3)
        self.assertNotIn("555-203-0009", regulars)
        self.assertEqual(len(result["followup_queue"]), 1)
        self.assertEqual(result["followup_queue"][0]["name"], "Anh Nguyen")
        self.assertEqual(result["followup_queue"][0]["days_since_visit"], 31)
        self.assertEqual(len(result["drafts"]), 1)
        self.assertEqual(result["drafts"][0]["phone_number"], "555-203-0003")
        self.assertTrue(result["drafts"][0]["text"].startswith("DRAFT -- NOT SENT\n"))
        conflict = [bucket for bucket in result["capacity"] if bucket["over_capacity"]]
        self.assertEqual(len(conflict), 1)
        self.assertEqual(conflict[0]["count"], 3)
        self.assertEqual(conflict[0]["bucket_start"], datetime(2026, 2, 14, 18))
        self.assertEqual(conflict[0]["alternate_slot"], datetime(2026, 2, 14, 14))
        self.assertIn("2026-02-14 14:00", result["narrative_brief"])
        self.assertNotIn("\n", result["narrative_brief"])

    def test_original_split_identity_stays_separate_without_data_correction(self):
        # Reproduce the original inconsistency in memory, not in the source CSV.
        records = crm.load_records(SEED)
        for record in records:
            if record["record_id"] == "R014":
                record["phone_number"] = "555-203-0009"
        status, _ = crm.compute_regular_status(records, AS_OF)
        self.assertEqual(status["555-203-0003"]["visit_count"], 2)
        self.assertEqual(status["555-203-0009"]["visit_count"], 1)
        self.assertFalse(status["555-203-0003"]["is_regular"])
        self.assertFalse(status["555-203-0009"]["is_regular"])
        self.assertEqual(crm.lapsed_followup_queue(status, AS_OF), [])

    def test_frequency_boundaries_and_custom_arguments(self):
        self.assertTrue(crm.has_three_in_window([
            datetime(2026, 1, 15), datetime(2026, 1, 1), datetime(2026, 1, 8)
        ]))
        self.assertFalse(crm.has_three_in_window([
            datetime(2026, 1, 1), datetime(2026, 1, 8), datetime(2026, 1, 16)
        ]))
        self.assertFalse(crm.has_three_in_window([]))
        self.assertFalse(crm.has_three_in_window([datetime(2026, 1, 1)]))
        self.assertTrue(crm.has_three_in_window(
            [datetime(2026, 1, 1), datetime(2026, 1, 6)], window_days=5, threshold=2
        ))

    def test_nonconsenting_visits_never_establish_status(self):
        records = [
            visit("2026-01-01", consent=False),
            visit("2026-01-05"), visit("2026-01-10"),
        ]
        status, excluded = crm.compute_regular_status(records, AS_OF)
        self.assertFalse(status["test-phone"]["is_regular"])
        self.assertEqual(status["test-phone"]["visit_count"], 2)
        self.assertEqual(len(excluded), 1)

    def test_latest_optout_revokes_status(self):
        records = [visit(day) for day in ("2026-01-01", "2026-01-05", "2026-01-10")]
        records.append(visit("2026-01-11", consent=False))
        status, _ = crm.compute_regular_status(records, AS_OF)
        self.assertEqual(status, {})
        self.assertEqual(crm.lapsed_followup_queue(status, AS_OF), [])

    def test_same_day_optout_wins_in_either_input_order(self):
        records = [visit("2026-01-10"), visit("2026-01-10", consent=False)]
        for ordered in (records, list(reversed(records))):
            with self.subTest(ordered=ordered):
                self.assertEqual(crm.compute_regular_status(ordered, AS_OF)[0], {})

    def test_future_record_does_not_change_past_consent(self):
        records = [visit(day) for day in ("2026-01-01", "2026-01-05", "2026-01-10")]
        records.append(visit("2026-03-01", consent=False))
        status, _ = crm.compute_regular_status(records, AS_OF)
        self.assertTrue(status["test-phone"]["is_regular"])
        self.assertEqual(status["test-phone"]["visit_count"], 3)

    def test_missing_phones_and_exact_phone_matching(self):
        records = [visit("2026-01-01", phone=phone) for phone in ("", "  ")]
        self.assertEqual(crm.eligible_records(records), [])
        self.assertEqual(crm.compute_regular_status(records, AS_OF)[0], {})
        records = [
            visit("2026-01-01", phone="111"),
            visit("2026-01-05", phone="222"),
            visit("2026-01-10", phone="111"),
        ]
        status, _ = crm.compute_regular_status(records, AS_OF)
        self.assertEqual(set(status), {"111", "222"})
        self.assertFalse(any(customer["is_regular"] for customer in status.values()))

    def test_lapse_boundary_and_draft_generation(self):
        records = [visit(day) for day in ("2026-01-01", "2026-01-05", "2026-01-10")]
        status, _ = crm.compute_regular_status(records, AS_OF)
        self.assertEqual(crm.lapsed_followup_queue(status, datetime(2026, 1, 30)), [])
        queue = crm.lapsed_followup_queue(status, datetime(2026, 1, 31))
        self.assertEqual(queue[0]["days_since_visit"], 21)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fabricated.csv"
            write_csv(path, records)
            result = crm.run(path, AS_OF)
        self.assertEqual(len(result["drafts"]), 1)
        self.assertTrue(result["drafts"][0]["text"].startswith("DRAFT -- NOT SENT\n"))

    def test_bucket_boundaries_and_dates(self):
        self.assertEqual(crm.slot_bucket(datetime(2026, 2, 14, 17, 59)), datetime(2026, 2, 14, 16))
        self.assertEqual(crm.slot_bucket(datetime(2026, 2, 14, 18, 1)), datetime(2026, 2, 14, 18))
        self.assertEqual(crm.slot_bucket(datetime(2026, 2, 14, 23, 59)), datetime(2026, 2, 14, 22))
        records = [visit("2026-02-14", slot="2026-02-14 18:00", consent=False)] * 3
        records += [visit("2026-02-15", slot="2026-02-15 18:00")]
        capacity = crm.capacity_view(records)
        self.assertEqual([bucket["count"] for bucket in capacity], [3, 1])
        self.assertTrue(capacity[0]["over_capacity"])
        self.assertFalse(crm.capacity_view(records, threshold=3)[0]["over_capacity"])
        self.assertFalse(crm.capacity_view(records[:2])[0]["over_capacity"])

    def test_alternative_ranking_does_not_hardcode_capacity(self):
        capacity = [
            {"bucket_start": datetime(2026, 2, 14, 18), "count": 6},
            {"bucket_start": datetime(2026, 2, 14, 14), "count": 3},
            {"bucket_start": datetime(2026, 2, 14, 12), "count": 3},
            {"bucket_start": datetime(2026, 2, 15, 10), "count": 0},
        ]
        self.assertEqual(
            crm.suggest_alternate_slot(capacity, datetime(2026, 2, 14, 18)),
            datetime(2026, 2, 14, 12),
        )
        self.assertIsNone(crm.suggest_alternate_slot(capacity[:1], datetime(2026, 2, 14, 18)))

    def test_full_alternative_is_not_advertised_as_available(self):
        records = [visit("2026-02-14", slot="2026-02-14 18:00")] * 3
        records += [visit("2026-02-14", slot="2026-02-14 14:00")] * 2
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fabricated.csv"
            write_csv(path, records)
            result = crm.run(path, AS_OF)
        conflict = result["capacity"][1]
        self.assertIsNone(conflict["alternate_slot"])
        self.assertIn("No observed same-day alternative", result["narrative_brief"])

    def test_malformed_csv_reports_errors(self):
        header = ",".join(FIELDS) + "\n"
        bad_rows = [
            "TEST,Name,123,true,2026-01-01,dine_in\n",
            "TEST,Name,123,true,2026-01-01,dine_in,,extra\n",
            "TEST,Name,123,yes,2026-01-01,dine_in,\n",
            "TEST,Name,123,true,not-a-date,dine_in,\n",
            "TEST,Name,123,true,2026-01-01,catering,\n",
            "TEST,Name,123,true,2026-01-01,dine_in,2026-01-01 14:00\n",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            for row in bad_rows:
                with self.subTest(row=row):
                    path.write_text(header + row, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        crm.load_records(path)
            path.write_text("name,phone\nTest,123\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                crm.load_records(path)

    def test_empty_data_and_input_immutability(self):
        self.assertEqual(crm.capacity_view([]), [])
        self.assertEqual(crm.compute_regular_status([], AS_OF), ({}, []))
        self.assertIn("no catering capacity conflicts", crm.narrative_brief({}, [], [], AS_OF))
        records = [visit(day) for day in ("2026-01-01", "2026-01-05", "2026-01-10")]
        before = [record.copy() for record in records]
        crm.compute_regular_status(records, AS_OF)
        crm.capacity_view(records)
        self.assertEqual(records, before)


class FlaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        with patch.dict(os.environ, {
            "INVENTORY_DB": str(Path(cls.directory.name) / "inventory.db"),
            "ORDERS_CSV": str(ORDERS),
            "CRM_SEED_CSV": str(SEED),
            "CRM_AS_OF": "2026-02-15",
        }):
            cls.module = importlib.import_module("app")
        cls.client = cls.module.app.test_client()

    def test_crm_and_original_routes(self):
        response = self.client.get("/crm")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("OVER CAPACITY", text)
        self.assertIn("2026-02-14 14:00", text)
        self.assertIn("DRAFT -- NOT SENT", text)
        self.assertIn("31 days since last visit", text)
        for route, expected in (
            ("/", "10 fixture orders still load"),
            ("/inventory", "Pho65 mobile inventory"),
            ("/inventory/scan", "Scan or type a code"),
            ("/health", '"status":"ok"'),
        ):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected, response.get_data(as_text=True))
        self.assertEqual(self.client.post("/crm").status_code, 405)

    def test_missing_file_and_invalid_as_of(self):
        with patch.object(self.module, "CRM_SEED_CSV", str(Path(self.directory.name) / "missing.csv")):
            response = self.client.get("/crm")
            self.assertEqual(response.status_code, 404)
            self.assertIn("CRM seed file not found", response.get_data(as_text=True))
        with patch.object(self.module, "CRM_AS_OF", "invalid"):
            response = self.client.get("/crm")
            self.assertEqual(response.status_code, 400)
            self.assertIn("CRM data needs review", response.get_data(as_text=True))

    def test_drafts_are_visible_and_customer_html_is_escaped(self):
        path = Path(self.directory.name) / "fabricated.csv"
        write_csv(path, [
            visit(day, name="<script>alert(1)</script>")
            for day in ("2026-01-01", "2026-01-05", "2026-01-10")
        ])
        with patch.object(self.module, "CRM_SEED_CSV", str(path)):
            response = self.client.get("/crm")
        text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("DRAFT -- NOT SENT", text)
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("&lt;script&gt;", text)

    def test_malformed_csv_is_a_clear_error(self):
        path = Path(self.directory.name) / "invalid.csv"
        path.write_text("wrong,columns\nvalue,value\n", encoding="utf-8")
        with patch.object(self.module, "CRM_SEED_CSV", str(path)):
            response = self.client.get("/crm")
        self.assertEqual(response.status_code, 400)
        self.assertIn("missing required columns", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
