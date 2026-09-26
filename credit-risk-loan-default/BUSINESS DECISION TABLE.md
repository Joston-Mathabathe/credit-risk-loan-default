# Business Decision Table

This table demonstrates how technical outputs can be translated into business questions.

| Analytical finding/output | Business question | Possible action |
|---|---|---|
| High default rate in a credit-score band | Is this segment materially higher risk? | Investigate the segment and monitor it |
| High DTI default rate | Is repayment pressure associated with higher observed risk? | Review affordability/risk indicators |
| Model has higher recall | How many actual defaults are being identified? | Consider whether additional review capacity is justified |
| Model has low precision | How many flagged applications are false positives? | Assess customer and operational impact |
| Different models perform differently | Which model characteristics suit the business objective? | Compare performance, interpretability and governance needs |
| Risk group is large | Can operations handle additional manual reviews? | Consider workflow capacity before changing thresholds |
| Model performance changes over time | Is model drift or changing customer behaviour occurring? | Monitor and investigate model performance |

## Important

The table intentionally does not prescribe an automatic lending decision. In a real bank, business, risk, compliance and governance teams would determine the appropriate policy and controls.
