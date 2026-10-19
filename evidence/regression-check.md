# Regression Check — Week 3/4 Features After the Week 5 Extension

Use this to prove your Week 5 `/crm` addition did NOT break the Week 3 order tracker or the Week 4 inventory ledger.

> **Instructions:** 1. Complete the "Before" rows at Step 0, before writing any Week 5 code. 2. Complete the "After" rows at Step 8, once `/crm` is built. 3. If any "After" row does not match its "Before" row, fix the regression before continuing — do not submit a failing row.

## Regression Matrix

After evidence supplied by the user on October 18, 2026. Browser screenshots document the manual checks; a terminal screenshot documents the user's automated inventory test run. Codex did not rerun these checks for this documentation update.

| \# | Check | Command / URL | Before (Step 0) | After (Step 8) | Pass/Fail |
|------------|------------|------------|------------|------------|:----------:|
| 1 | Week 3 order tracker loads | `http://localhost:5050/` | Pre-edit HTTP check returned 200 and “10 fixture orders still load.” [Earlier screenshot](week3-order-tracker.png); its capture timing is not established. | Same heading and “10 fixture orders still load,” with the CRM navigation link present. [After screenshot](week3-orders-after.png). | Pass — fixture count and order page preserved. |
| 2 | Week 4 inventory page loads | `http://localhost:5050/inventory` | Pre-edit HTTP check returned 200. Workbook Section 0 records an empty table. [Earlier screenshot](week4-inventory.png); its capture timing is not established. | Inventory table loads with Salt, `PHO65-INV-000101`: 8 each, average \$2.25, value \$18.00, status OK. [After screenshot](week4-inventory-after.png). | Pass — page loads and displays the added test item correctly. |
| 3 | Week 4 known-answer cost test (fresh item) | Receive 10 at \$2.00; receive 10 at \$2.50; use 12 | Not required before Step 3; no baseline cost-test result recorded. | Salt's history shows received +10 at \$2.00, received +10 at \$2.50, then used −12. Result: 8 each, average \$2.25, value \$18.00. [Item and ledger screenshot](week4-cost-test-after.png). | Pass — ledger sequence and all three expected values match. |
| 4 | Automated inventory test suite | `docker compose exec app python test_inventory.py` | Not required | User's terminal shows the command completed with `inventory known-answer and guard tests passed`. [Test-output screenshot](inventory-automated-test-passed.png). | Pass — known-answer costing, QR label response, duplicate-request guard, and negative-stock guard passed. |

## If Something Failed

No regressions found in the three evidenced manual checks: the order page still shows 10 fixture orders, inventory loads, and the Salt ledger produces 8 units at average \$2.25 and value \$18.00. The inventory table now contains the test item rather than being empty, as expected after recording the transactions. Earlier source comparison also confirmed that all existing Flask functions were unchanged.

All four regression checks now pass. The user's terminal screenshot confirms the automated inventory suite completed successfully; the script prints its success message only after its costing, label, duplicate-request, and negative-stock assertions pass. No application code or live inventory records were changed for this documentation update.