# Regression Check — Week 3/4 Features After the Week 5 Extension

Use this to prove your Week 5 `/crm` addition did NOT break the Week 3 order tracker or the Week 4 inventory ledger.

> **Instructions:** 1. Complete the "Before" rows at Step 0, before writing any Week 5 code. 2. Complete the "After" rows at Step 8, once `/crm` is built. 3. If any "After" row does not match its "Before" row, fix the regression before continuing — do not submit a failing row.

## Regression Matrix

The user identifies **Salt as the before test item** and **Carrot as the after test item**. The [combined inventory screenshot](week4-inventory-before-after.png) shows both items together with matching results: 8 each, average cost \$2.25, value \$18.00, and status OK. The before/after assignment follows the user's clarification; the screenshot records the displayed totals for both items.

| \# | Check | Command / URL | Before (Step 0) | After (Step 8) | Pass/Fail |
|------------|------------|------------|------------|------------|------------|
| 1 | Week 3 order tracker loads | `http://localhost:5050/` | Pre-edit HTTP check returned 200 and “10 fixture orders still load.” [Earlier screenshot](week3-order-tracker.png). | Same heading and “10 fixture orders still load,” with the CRM navigation link present. [After screenshot](week3-orders-after.png). | Pass — fixture count and order page preserved. |
| 2 | Week 4 inventory page loads | `http://localhost:5050/inventory` | Salt, `PHO65-INV-000101`: 8 each, average \$2.25, value \$18.00, status OK. Identified by the user as the before result. [Combined screenshot](week4-inventory-before-after.png). | Carrot, `PHO65-INV-000102`: 8 each, average \$2.25, value \$18.00, status OK. Identified by the user as the after result. [Combined screenshot](week4-inventory-before-after.png). | Pass — inventory loads and both test items show the expected values. |
| 3 | Week 4 known-answer cost test (fresh item) | Receive 10 at \$2.00; receive 10 at \$2.50; use 12 | Salt's history shows received +10 at \$2.00, received +10 at \$2.50, then used −12. Result: 8 each, average \$2.25, value \$18.00. [Before item and ledger screenshot](week4-cost-test-salt.png). The [combined screenshot](week4-inventory-before-after.png) also confirms these totals. | Carrot's history shows received +10 at \$2.00, received +10 at \$2.50, then used −12. Result: 8 each, average \$2.25, value \$18.00. [After item and ledger screenshot](week4-cost-test-carrot.png). | Pass — both ledgers confirm the expected transaction sequence and all three known-answer values match before and after. |
| 4 | Automated inventory test suite | `docker compose exec app python test_inventory.py` | Not required. | User's terminal shows the command completed with `inventory known-answer and guard tests passed`. [Test-output screenshot](inventory-automated-test-passed.png). | Pass — known-answer costing, QR label response, duplicate-request guard, and negative-stock guard passed. |