import random


class RandomAI:
    def __init__(self):
        pass

    def process(self, game):
        """Do whatever you need with the Game object game"""
        self.game = game

    def decide(self):

        actions = ['mine', 'tavern', 'fight']

        decisions = {'mine': [("Mine", 30), ('Fight', 10), ('Tavern', 5)],
                     'tavern': [("Mine", 10), ('Fight', 10), ('Tavern', 50)],
                     'fight': [("Mine", 15), ('Fight', 30), ('Tavern', 10)]}

        path_to_goal = []
        dirs = ["North", "East", "South", "West", "Stay"]

        first_cell = self.game.hero.pos
        path_to_goal.append(first_cell)

        action = random.choice(actions)
        decision = decisions[action]

        hero_move = random.choice(dirs)
        nearest_enemy_pos = random.choice(self.game.heroes).pos
        nearest_mine_pos = random.choice(self.game.mines_locs)
        nearest_tavern_pos = random.choice(self.game.mines_locs)

        return (path_to_goal,
                action,
                decision,
                hero_move,
                nearest_enemy_pos,
                nearest_mine_pos,
                nearest_tavern_pos)


    def post_process(self):
        pass