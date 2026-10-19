# Stakeholder and Support-Burden Analysis (ADI501)

> **Instructions:** For each stakeholder, describe a concrete failure mode when phone-matching fails — not a vague "confusion." Each cell should describe something that actually happens to that person.

| Stakeholder | How they use the tool | What happens when the phone-matching rule fails for them |
|------------------------|------------------------|------------------------|
| Owner | Reads the weekly narrative brief and reviews the lapsed-regulars follow-up queue to personally approve and send warm check-in texts. | If a typo splits a customer's records (as with Anh Nguyen), the owner may mistakenly send a "we miss you" message to a guest who just dined in yesterday, creating an awkward customer experience and destroying trust in the tool's recommendations. |
| Counter staff | Collects 10-digit phone numbers and verbal consent (`opted_in`) during POS checkout amidst busy service hours. | Has no live validation UI at checkout to detect single-digit typos or duplicates, leading to unprompted customer complaints when repeat guests find their visits were not recognized or rewards were omitted. |
| Kitchen lead | Monitors the catering capacity schedule to throttle broth production, stage ingredients, and schedule cook staffing across peak slots. | While phone matching primarily impacts loyalty, if a large corporate client splits an oversized order across two phone numbers to bypass capacity limits, the matching logic fails to aggregate them, leaving the kitchen understaffed for sudden volume. |