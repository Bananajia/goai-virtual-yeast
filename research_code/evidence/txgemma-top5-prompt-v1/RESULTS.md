# TxGemma categorical top-five prompt audit

Date: 2026-08-14

## Frozen scope

- Predeclared mechanism-informed candidates: **43**
- Candidates passing the control detectability gate: **28**
- Cyclic answer orders per candidate: **5**
- Prompt evaluations: **140**
- Treated TRAIN numeric rows decoded: **0**
- Non-TRAIN numeric rows decoded: **0**
- Candidate response values used to build prompts: **0**

## Option-order audit

| Diagnostic | Count |
|---|---:|
| accepted categorical predictions | 0 |
| strict abstentions | 28 |
| raw argmax at option A | 107 |
| raw argmax at option B | 33 |
| raw argmax at options C--E | 0 |

For the highest raw panel item, the post-cycle maximum conditional score was
**0.2241**, answer-order agreement was **0.40**, and normalized entropy was
**0.9952**. A perfectly uniform five-way score has normalized entropy 1.0.
Cycling answer labels therefore spread an A/B positional preference across the
five biological labels; it did not establish calibrated biological
uncertainty.

## Decision and boundary

**VALIDATED_REJECTED / ALL ABSTAIN.** This checkpoint-plus-prompt-plus-logit
scorer did not produce a valid direction/magnitude prediction, so its raw panel
ordering is not an accepted top-five response prediction. The result does not
show that every TxGemma use, every language model, or a separately trained
numeric head must fail.

The clean evidence stores no query identity, protein name, molecular string,
prompt text, token logit vector, response value, prediction vector, or machine-
local path. The public model revision and exact prompt hash remain documented
in the source audit, while this Adapter verifies only anonymous aggregates.
