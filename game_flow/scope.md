# game_flow/

## Purpose
Translate real game happenings into structured domain events and immediate raw constraints.

This module is the live-play coordinator. It knows:
- whose turn it is
- who could have shown
- who definitely could not have shown
- what a suggestion event implies mechanically
- how to handle skipped turns, edits, and deviations

It does not do deep deduction or probability.

## Owns
- Turn progression
- Around-the-room responder ordering
- Recording suggestions
- Recording disprovals
- Recording seen cards
- Manual overrides and edits
- Undo/repair of event sequence
- Conversion from observed gameplay into structured event objects

## Inputs
From CLI or app layer:
- "Player X suggested Scarlet, Rope, Library"
- "Player Y disproved"
- "No one disproved"
- "I saw the shown card and it was Rope"
- "Skip to player Z"
- "Undo last event"
- "Correct turn 8"
- current state

## Outputs
Structured domain events and raw constraints, such as:
- `SuggestionMade`
- `CardShown`
- `NoDisproof`
- `CardSeen`
- `TurnAdvanced`
- list of players who failed to show
- event sequences ready to commit into `state`

## Must Do
- Be fast and ergonomic
- Encode the mechanical flow of play
- Handle messy real life
- Minimise required input
- Produce clean structured events

## Must Not Do
- Store canonical truth itself
- Perform multi-step deduction
- Compute probabilities
- Format terminal output

## Mental Model
`game_flow` is the rules-aware event interpreter.
