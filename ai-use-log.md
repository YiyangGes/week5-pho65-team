# AI-Use Log (Pho65 CRM Co-Pilot Team)

Update this log in real time while your team works. Record real interactions with your AI coding agent.

> **Instructions for Student Teams:** - **Log in real time**, not reconstructed afterward from memory. - **Accountability:** note which teammate initiated the prompt and what decision stayed human. - **The Step 2 auto-send rejection is a required row** — you must have at least one entry where the agent proposed something and your team rejected it for safety reasons. If your agent never proposes an auto-send step on its own, explicitly ask it to add one, then reject it, and log that. - **Never record** ngrok authtokens, passwords, private keys, or real customer data here.

## Team AI Interaction Log

| Date / Time | Teammate & Agent | Task & Prompt | What the Agent Proposed | What the Team Accepted | What the Team Rejected/Revised | How the Team Verified It | Decision That Stayed Human |
|---------|---------|---------|---------|---------|---------|---------|---------|
| 2026-10-17 | Flynn (role owner) / Codex | Step 1: Propose data loading. | Load the seed CSV and parse dates, consent values, and phone numbers. | Accepted: structured records support consistent calculations. | None. | Plan reviewed against the CSV and existing skeleton; implementation not yet tested. | Approve the input fields and parsing rules. |
| 2026-10-17 | Flynn (role owner) / Codex | Step 2: Propose regular flags. | Match by phone, require latest-record consent, and count only opted-in visits; use 3+ visits in 14 days. | Accepted: follows the matching rule and class default. | None; missing-phone and non-consenting records remain not eligible. | Compared the proposal with Workbook Section 1; implementation not yet tested. | Approve consent rules and the frequency threshold. |
| 2026-10-17 | Jonathon (role owner) / Codex | Step 3: Propose the follow-up queue. | Identify previously regular customers with no visit in 21+ days. | Accepted: highlights lapsed regulars using the default threshold. | None. | Compared the proposal with the workbook threshold; implementation not yet tested. | Approve the lapse threshold and review follow-up candidates. |
| 2026-10-17 | Jonathon (role owner) / Codex | Step 4: Propose capacity checks. | Count all catering bookings in 2-hour windows, flag more than 2, and suggest a quieter same-day slot. | Accepted: supports demand shaping and counts workload regardless of consent. | None. | Seed records R016–R018 give 3 bookings in the February 14, 2026, 18:00–20:00 window; implementation not yet tested. | Approve capacity limits and any proposed booking changes. |
| 2026-10-17 | Jonathon (role owner) / Codex | Step 5: Propose draft messages. | Generate eligible-customer follow-up and alternate-slot drafts labeled DRAFT — NOT SENT, with no sending function. | Accepted: keeps messages available for human review. | No auto-send was proposed; any future sending step is disallowed because dispatch is not authorized. | Reviewed the plan wording; code-level verification remains pending. | Review and approve any message outside this draft-only tool. |
| 2026-10-17 | Jonathon (role owner) / Codex | Step 6: Propose the narrative brief. | Summarize regulars, lapsed customers, busy slots, and suggested actions in one paragraph. | Accepted: gives the manager a concise weekly overview. | None. | Checked that the proposal covers the required outputs; implementation not yet tested. | Review the brief and choose actions. |
| 2026-10-17 | Yiyang (role owner) / Codex | Step 7: Propose integration and checks. | Combine outputs in run(), display them through a new /crm route, and verify consent, thresholds, and regression behavior. | Accepted with revision: keep the new feature separate from existing route logic. | Revised to explicitly preserve /, /inventory, /inventory/scan, and all other Week 3/4 routes because existing workflows must keep working. | Reviewed the plan and existing route declarations; implementation and regression tests remain pending. | Approve the additive scope and review test results. |
| 2026-10-17 | Flynn / Jonathon / Yiyang (role owner) / Codex | Code generation: implement the reviewed CRM proposal. | Implement the supplied CRM functions and add `/crm`, with clear errors for malformed CSV rows. | User approved implementation before execution. | Revised CSV validation to report incomplete rows clearly. | All 12 supplied signatures and 18 existing Flask functions preserved; 15 CRM tests passed after the approved data correction. | Approve reviewed code before execution. |
| 2026-10-17 | Jonathon (role owner) / Codex | Message drafting: prepare the lapsed-customer invitation. | Generate Anh's friendly invitation labeled `DRAFT -- NOT SENT`; add no sending function. | Draft-only generation accepted as part of the approved implementation. | No automatic delivery allowed. | CLI output and the subsequently supplied browser screenshot showed one labeled, unsent draft. | Review message wording and decide any delivery outside this tool. |
| 2026-10-18 | Jonathon (role owner) / Codex | Required Step 2 rejection exercise, completed after implementation. | Review-only proposal: automatically send follow-up messages to lapsed regulars without staff review. | Retain drafts for staff review only. | User explicitly rejected: “I reject automatic sending; all messages must remain drafts for staff review.” | Rejection recorded in the conversation; no automatic-sending code was implemented. | Reject automatic sending and retain human review. |

### Step 3 implementation follow-up — October 17, 2026

For any agent-proposed command or file change beyond ordinary code edits, log it here before running it.

| Command/Action | Target | Purpose | Risk | Recovery | Decision |
|------------|------------|------------|------------|------------|------------|
| `docker compose up -d --build app` | app container | rebuild with new /crm route | low — isolated to app image, no data loss | `docker compose down` reverts to no running container | Approved |
|  |  |  |  |  |  |

## Safety Checklist (Stop Signs)

Before considering this project done, confirm:

1.  **Does any file contain a function that sends an email, SMS, or push notification?** *(Answer: No — verified by searching for `send_`, `smtplib`, `requests.post` across `docker/app/`.)*
2.  **Were Week 3 and Week 4 routes (`/`, `/inventory`) preserved without modification?** *(Answer: Yes — see `evidence/regression-check.md`.)*
3.  **Is every `opted_in = false` record excluded from `regular_status`?** *(Answer: Yes — see `evidence/consent-and-capacity.md`.)*
4.  **Did the team log at least one rejected agent proposal?** *(Answer: Yes — see row above.)*