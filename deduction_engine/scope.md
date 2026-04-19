# deduction_engine/

## Purpose
Take the current known facts and constraints, and derive all hard logical consequences.

This is the MVP_v1 reasoning engine.

It operates on structured state, not raw CLI input.

## Owns
- Constraint propagation
- Hard deductions
- Contradiction detection
- Explanation/provenance of logical conclusions
- Fixpoint iteration until no more deductions are possible

## Inputs
From `state`:
- player/card structure
- known ownership facts
- known impossibilities
- event-derived constraints
- hand sizes
- envelope rules

Optionally:
- freshly generated constraints from `game_flow`

## Outputs
Structured deduction results, such as:
- new certainties
- new impossibilities
- contradiction reports
- explanations for each new conclusion
- summary of what changed this pass

## Must Do
- Respect only hard rules and hard evidence
- Be deterministic
- Be explainable
- Reach a stable state before returning

## Must Not Do
- Guess
- Assign soft confidence
- Parse commands
- Handle turn sequencing
- Compute probabilities

## Mental Model
`deduction_engine` answers:

> What must be true now?
