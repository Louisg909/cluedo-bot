# state/

## Purpose
The canonical source of truth for the whole application.

This module contains the data structures representing:
- the game setup
- the event history
- the current knowledge state
- optionally any derived facts or probability views

## Owns
- Player definitions
- Card definitions
- Card categories
- Turn order
- Hand sizes
- Envelope slot definitions
- Event records
- Knowledge matrix / constraint store
- Reason/provenance records for conclusions, if stored centrally
- Snapshots or reversible state for undo/edit support

## Inputs
Structured data only:
- player list
- user player identity
- user cards
- structured events from `game_flow`
- hard conclusions from `deduction_engine`
- optional probability results from `probability_engine`

## Outputs
Structured state views only:
- current game state object
- current knowledge matrix
- known ownership facts
- impossible ownership facts
- unresolved possibilities
- event history
- contradiction flags
- immutable views for display

## Must Do
- Store facts consistently
- Enforce structural validity where appropriate
- Provide a clean API for reading and updating state
- Remain simple and boring

## Must Not Do
- Parse commands
- Infer game events from user text
- Perform deduction
- Compute probabilities
- Decide recommendations

## Mental Model
`state` is the in-memory database and single source of truth.
