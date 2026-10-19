# Pilot Recommendation Memo (ADI501)

> **Instructions:** Thresholds must be numeric and falsifiable — "if it seems to work" is not acceptable.

## 4-Week Trial Thresholds

- **Continue if:** Customer consent opt-in rate remains $\ge 45\%$ of total checkout transactions, follow-up draft accuracy is $\ge 90\%$ (no more than 1 false-positive regular alert per month), and $100\%$ of flagged capacity bottlenecks are successfully steered without kitchen delays.
- **Revise if:** Opt-in rate lands between $25\% - 44\%$, or phone typos cause 1–2 false lapsed alerts per month, or checkout staff report phone collection adds $>15$ seconds per transaction. *(Action: revise POS entry screen with phone number formatting validation and retrain staff).*
- **Stop if:** Opt-in rate falls below $25\%$ (rendering cohort tracking statistically unviable), any message is dispatched without manual owner approval (strict zero-tolerance boundary), or $\ge 2$ unflagged catering overages cause kitchen service failure.

## Justification

These numeric thresholds balance customer goodwill against kitchen throughput protection. A 45% opt-in baseline is the minimum threshold required for frequency-based clustering to accurately detect true store regulars without sampling bias. The strict stop condition around unauthorized messaging protects customer privacy and legal compliance, ensuring the co-pilot remains strictly human-in-the-loop and maintains the owner's complete confidence throughout the pilot.