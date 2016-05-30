from game import Game
from pathfinder import *
import math

class ReflexAI:
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
        next = [0, 0, 0, 0, 0]

        #goTo = (random.choice(self.game.mines_locs))

        if self.game.hero.life > 30:
            first_cell = self.game.hero.pos
            path_to_goal.append(first_cell)

            action = random.choice(actions)
            decision = decisions[action]
        else:
            first_cell = self.game.hero.pos
            path_to_goal.append(first_cell)

            #goTo = self.getClosest(self.game.hero.pos, self.game.taverns_locs)

            action = actions[2]
            decision = decisions[action]

        #map = MapConverter.convertMap(self.game)
        #p = Pathfinder(map)
        #path = p.find_route(self.game.hero.pos, goTo)

        for j in range(0, 4, 1):
            next[j] = self.score(self.game.hero.pos, dirs[j])

        hero_move = dirs[next.index(min(next))]

        #path_to_goal = path

        nearest_enemy_pos = random.choice(self.game.heroes).pos
        nearest_mine_pos = self.getClosest(self.game.hero.pos, self.game.mines_locs)
        nearest_tavern_pos = self.getClosest(self.game.hero.pos, self.game.taverns_locs)

        return (path_to_goal,
                action,
                decision,
                hero_move,
                nearest_enemy_pos,
                nearest_mine_pos,
                nearest_tavern_pos)

    def getClosest(self, loc, location_list):
        min_local = self.game.board_size * self.game.board_size
        for l in location_list:
            if (math.fabs(l[0]-loc[0]) + math.fabs(l[1]-loc[1])) < min_local:
                min_local = math.fabs(l[0] - loc[0]) + math.fabs(l[1] - loc[1])
                min_local_pos = l
        return min_local_pos

    def getDistance(self, loc, l):
        min_local = math.fabs(l[0] - loc[0]) + math.fabs(l[1] - loc[1])
        return min_local

    def score(self, now, next_move):
        sc = 0

        if next_move == "North":
            next_f = [now[0] + 1, now[1]]
        elif next_move == "East":
            next_f = [now[0], now[1] + 1]
        elif next_move == "South":
            next_f = [now[0] - 1, now[1]]
        elif next_move == "West":
            next_f = [now[0], now[1] - 1]
        else:
            next_f = now

        #punishment for runing into wall
        

        #little reward for being healthy
        if self.game.hero.life > 30:
            sc += 1

        #reward and punishment for geting away from closest mine
        if self.getDistance(now, self.getClosest(now, self.game.mines_locs)) > \
                self.getDistance(next_f, self.getClosest(next_f, self.game.mines_locs)):
            sc -= 10
        elif self.getDistance(now, self.getClosest(now, self.game.mines_locs)) < \
                self.getDistance(next_f, self.getClosest(next_f, self.game.mines_locs)):
            sc += 10

        #reward distances between heroes

        #reward for life restoring
        if (self.game.hero.life < 30) & (self.getDistance(now, self.getClosest(now, self.game.taverns_locs)) < self.getDistance(next_f, self.getClosest(next_f, self.game.taverns_locs))):
            sc += 20
        if (self.game.hero.life < 30) & (self.getDistance(now, self.getClosest(now, self.game.taverns_locs)) > self.getDistance(next_f, self.getClosest(next_f, self.game.taverns_locs))):
            sc -= 20
        return sc

    def post_process(self):
        pass

if __name__ == "__main__":
    with open('exampleMap.json') as data_file:
        data = json.load(data_file)
    gameobj = Game(data)

    ai = ReflexAI()
    for i in range(1):
        ai.process(gameobj)
        ai.decide()
        ai.post_process()
        print("%d ---" % i)
