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
    def __init__(self,no_players, users_hand:set, public_hand:set=None):
        self.state = GameState(no_players, user_hand, public_hand)


    def record_guess(self, guesser, guess_items:set, responder:int=None):
        if responder == None:
            # go through all holders except the first three (user, public, and hidden) and set to NO for all the cards - EXCEPT the guesser!!!

            verified_holders =  set(range(2, n+1)) # all minus private (0), and holder (1)
            verified_holders.remove(guesser) # removes the guesser from the set
        else:
            if guesser < responder:
                verified_holders = set(range(G+1, r))
            else:
                verified_holders = set(range(G + 1, n + 1)) | set(range(2, r))

            self.state.add_constraint(responder, *guess_items) # add the constraints on the responder

        self.state.set_all_nos(verified_holders, guess_items)




        # run logical deductions ?




def main():
    # some sort of loop - this will pull from the CLI but thought I would make stuff here first to understand what the CLI should be doing. The CLI is the interaction between the backend and the user.
    # I am thinking a loop that just waits for a command that could be one of a few things - most likely in the form of a blind guess (someone else), or a non-blind guess (when I guess, I can see what the final person shows), or an input of a random card incase anything is shown
    pass




if __name__==`__main__`:
    main()

