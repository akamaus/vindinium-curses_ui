#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
#
# Pure random A.I, you may NOT use it to win ;-)
#
########################################################################

import random
import numpy
import mapConverter
from mapConverter import MapConverter
import convNet
import math

EXAMPLE_MAP_SIZE = 16
UI_FORMATTING_STRING = "%0.3f"


class AI:
    """Pure random A.I, you may NOT use it to win ;-)"""
    def __init__(self):
        self.net = convNet.ConvNet()
        self.net_move_probability = 0.7

    def process(self, game):
        """Do whatever you need with the Game object game"""
        self.game = game

    def pad_map(self, state):
        # state = numpy.random.random_integers(0, 5, (self.game.board_size, self.game.board_size, 2))
        shape = state.shape
        top_pad = int(math.ceil(float(-shape[0] + convNet.MAX_MAP_SIZE) / 2))
        bottom_pad = int(math.floor(float(-shape[0] + convNet.MAX_MAP_SIZE) / 2))
        left_pad = int(math.ceil(float(-shape[1] + convNet.MAX_MAP_SIZE) / 2))
        right_pad = int(math.floor(float(-shape[1] + convNet.MAX_MAP_SIZE) / 2))
        state = numpy.lib.pad(state, ((top_pad, bottom_pad), (left_pad, right_pad), (0, 0)), 'constant',
                              constant_values=mapConverter.TERRAIN)
        return state

    def decide(self):
        """Must return a tuple containing in that order:
          1 - path_to_goal :
                  A list of coordinates representing the path to your
                 bot's goal for this turn:
                 - i.e: [(y, x) , (y, x), (y, x)]
                 where y is the vertical position from top and x the
                 horizontal position from left.

          2 - action:
                 A string that will be displayed in the 'Action' place.
                 - i.e: "Go to mine"

          3 - decision:
                 A list of tuples containing what would be useful to understand
                 the choice you're bot has made and that will be printed
                 at the 'Decision' place.

          4- hero_move:
                 A string in one of the following: West, East, North,
                 South, Stay

          5 - nearest_enemy_pos:
                 A tuple containing the nearest enenmy position (see above)

          6 - nearest_mine_pos:
                 A tuple containing the nearest enenmy position (see above)

          7 - nearest_tavern_pos:
                 A tuple containing the nearest enenmy position (see above)"""

        actions = ['mine', 'tavern', 'fight']

        decisions = {'mine': [("Mine", 30), ('Fight', 10), ('Tavern', 5)],
                    'tavern': [("Mine", 10), ('Fight', 10), ('Tavern', 50)],
                    'fight': [("Mine", 15), ('Fight', 30), ('Tavern', 10)]}

        path_to_goal = []
        dirs = ["North", "East", "South", "West", "Stay"]

        first_cell = self.game.hero.pos
        path_to_goal.append(first_cell)

        map = MapConverter.convertMap(self.game)
        padded_map = self.pad_map(map)
        dirWeights = self.net.calculateDecisions(padded_map)
        decision = [
            ("North", UI_FORMATTING_STRING % dirWeights[0]),
            ("East", UI_FORMATTING_STRING % dirWeights[1]),
            ("South", UI_FORMATTING_STRING % dirWeights[2]),
            ("West", UI_FORMATTING_STRING % dirWeights[3]),
            ("Stay", UI_FORMATTING_STRING % dirWeights[4])
        ]
        hero_move = dirs[dirWeights.argmax(0)]

        action = random.choice(actions)

        nearest_enemy_pos = (0, 0)   # random.choice(self.game.heroes).pos
        nearest_mine_pos = (0, 0)    # random.choice(self.game.mines_locs)
        nearest_tavern_pos = (0, 0)  # random.choice(self.game.mines_locs)

        return (path_to_goal,
                action,
                decision,
                hero_move,
                nearest_enemy_pos,
                nearest_mine_pos,
                nearest_tavern_pos)


if __name__ == "__main__":
    pass
