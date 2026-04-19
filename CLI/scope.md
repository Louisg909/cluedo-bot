# CLI

## Purpose
The user-facing shell.

This module turns user commands into structured application calls, and structured results into readable output.

It should remain extremely thin.

## Owns
- Command parsing
- Prompting
- Help text
- Pretty-printing
- Tables and status displays
- Validation of superficial input shape
- Command aliases and shortcuts

## Inputs
Raw user input, such as:
- setup commands
- turn entry commands
- correction commands
- query commands such as `status`, `show`, `suggest`

## Outputs
- structured calls into the app/game_flow/state
- human-readable terminal output

## Must Do
- Be fast in live use
- Be easy to type
- Show the important information clearly
- Stay simple

## Must Not Do
- Contain game rules logic
- Contain deduction logic
- Contain probability logic
- Mutate state directly in complicated ways

## Mental Model
`CLI` is the keyboard-and-screen adapter.
