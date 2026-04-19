# probability_engine/

## Purpose
Compute soft beliefs over unresolved possibilities after hard deduction has been applied.

This is a second reasoning layer over the remaining feasible uncertainty.

It must respect all hard constraints from `state` and `deduction_engine`.

## Owns
- Representation of remaining uncertainty
- Probability computation over card ownership and envelope contents
- Marginal probabilities
- Ranking of likely solutions
- Optional expected-information calculations for future suggestions

## Inputs
From `state` after deduction:
- all known hard facts
- all remaining possible ownership assignments
- player/card/category structure
- hand sizes
- envelope constraints
- optional event history

## Outputs
Structured probabilistic views, such as:
- `P(card in envelope)`
- `P(player holds card)`
- ranked candidate solutions
- confidence scores
- expected value of possible suggestions

## Must Do
- Respect hard constraints fully
- Produce coherent probabilities
- Remain optional
- Be separable from MVP_v1

## Must Not Do
- Mutate truth casually
- Override hard logic
- Depend on CLI or game flow
- Become required for core correctness

## Important Design Rule
The probability engine works from the same canonical state as the deduction engine.

The deduction engine collapses uncertainty by adding hard facts to state.
The probability engine reasons over whatever remains possible.

## Mental Model
`probability_engine` answers:

> Given everything still possible, what is most likely?
