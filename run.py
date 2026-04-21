"""
# run.py

## Purpose
Composition root and application bootstrapper.

This file assembles the application and wires the modules together.

## Owns
- constructing the main state object
- creating engine instances
- dependency wiring
- starting the CLI loop
- selecting configuration (e.g. MVP_v1 vs MVP_v2)

## Inputs
- configuration
- startup options
- module instances

## Outputs
- running application

## Must Do
- Wire modules together cleanly
- Contain almost no domain logic

## Must Not Do
- Become a dumping ground
- Contain inference logic
- Contain game-processing logic

## Mental Model
`run.py` is the bootstrapper.
"""

from .deduction_engine import deduct
from .state import GameState



class CluedoBot:
    def __init__(self, no_players:int, user_hand:set, public_hand:set|None):
        self.state = GameState(no_players, user_hand, public_hand)


    def record_guess(self, guesser, guess_items:set, responder:int=None):
        if responder is None:
            verified_holders = set(range(2, self.state.n_holders))
            verified_holders.remove(guesser)
        else:
            if responder == guesser:
                raise ValueError("responder cannot be the same as guesser")

            verified_holders = self._holders_between(guesser, responder)
            self.state.add_constraint(responder, *guess_items)

        # run logical deductions ?

        return None


    def _holders_between(self, start: int, end: int) -> set:
        """
        Return the set of agent-holder indices strictly between start and end in forward circular order.

        Holder convention:
        - 0 = hidden
        - 1 = public
        - 2.. = player holders
        """
        holders = []
        current = start

        while True:
            current += 1
            if current >= self.state.n_holders:
                current = 2

            if current == end:
                break
            
            holders.append(current)

        return set(holders)






def main():
    # some sort of loop - this will pull from the CLI but thought I would make stuff here first to understand what the CLI should be doing. The CLI is the interaction between the backend and the user.
    # I am thinking a loop that just waits for a command that could be one of a few things - most likely in the form of a blind guess (someone else), or a non-blind guess (when I guess, I can see what the final person shows), or an input of a random card incase anything is shown
    pass




if __name__==`__main__`:
    main()

