



class turn_tracker:
    def __init__(self):
        pass

    # this is meant to just tick around the circle. Probably won't be its own class but just thinking out loud.


class GameEngine:
    def __init__(self, no_agents):
        self.no_angents = no_angents

    def guess_answer(guesser_index, shower_index=None):
        # return list - 1 at shower_index, and 0 inbetween guesser_index and None everywhere else? if shower_index = None then everyone except the guesser is 0
        if shower_index = None:
            return [0 if n != guesser_index else None for n in range(self.no_agenets)]






