# Build-vs-Buy Memo (ADI501)

> **Instructions:** Name one real product. Compare on cost, data ownership, and workflow fit — your recommendation is graded on reasoning quality, not on which product you pick.

**Named commercial product compared:** Square Loyalty

## Cost

Square Loyalty requires an ongoing SaaS subscription starting at \$45/month per location (for up to 500 enrolled customer profiles), totaling \$540 annually in recurring overhead. In contrast, our in-house Pho65 CRM prototype runs entirely on existing hardware with \$0 in marginal software fees, exchanging monthly SaaS fees for internal script maintainability and upfront developer setup.

## Data Ownership

Square Loyalty stores customer visit cadences, contact numbers, and consent records on Square's proprietary cloud servers under vendor-dictated terms of service, creating vendor lock-in. Our in-house build retains complete data sovereignty in local SQLite and CSV tables, guaranteeing that Pho65 owns every opt-in timestamp and transaction record without external data broker exposure.

## Workflow Fit

Commercial platforms like Square Loyalty operate primarily as transactional discount engines ("earn 1 point per dollar spent") rather than operational co-pilots. They offer zero native integration with Pho65's kitchen catering capacity thresholds (the 2-booking per 2-hour limit) or proactive demand-shaping alternate slot recommendations. Our custom tool is tightly integrated with Week 3 order logs and Week 4 inventory in a single familiar dashboard.

## Recommendation

**Recommendation: Build (Retain In-House Co-Pilot).** For an independent restaurant of Pho65's scale, the primary business risk is kitchen throughput collapse during peak catering windows rather than a lack of loyalty stamp cards. Off-the-shelf tools like Square Loyalty add recurring subscription costs without addressing catering bottlenecks. By retaining the in-house build, Pho65 saves \$540/year, maintains strict local data ownership over customer consent records, and preserves custom demand-shaping logic that directly protects kitchen operations.