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

        first_cell = self.game.hero.pos
        path_to_goal.append(first_cell)

        action = actions[0]

        for j in range(0, 5, 1):
            next[j] = self.score(self.game.hero.pos, dirs[j])

        hero_move = dirs[next.index(max(next))]

        now = self.game.hero.pos
        enemy_mines = tuple(list(set(self.game.mines_locs) - set(self.game.hero.mines)))
        goTo = self.getClosest(now, enemy_mines)
        map = MapConverter.convertMap(self.game)
        p = Pathfinder(map)
        path = p.find_route(self.game.hero.pos, goTo)
        path_to_goal = path
        if (self.game.hero.bot_last_move is not None) :
            if (((hero_move == "North") & ("South" == self.game.hero.bot_last_move)) |
                    ((hero_move == "South") & ("North" == self.game.hero.bot_last_move)) |
                    ((hero_move == "East") & ("West" == self.game.hero.bot_last_move)) |
                    ((hero_move == "West") & ("East" == self.game.hero.bot_last_move))):
                action = actions[1]

        decision = decisions[action]

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
        if location_list:
            for l in location_list:
                if (math.fabs(l[0]-loc[0]) + math.fabs(l[1]-loc[1])) < min_local:
                    min_local = math.fabs(l[0] - loc[0]) + math.fabs(l[1] - loc[1])
                    min_local_pos = l
            return min_local_pos
        else:
            return min_local

    def getDistance(self, loc, l):
        if l == self.game.board_size * self.game.board_size:
            return l
        else:
            min_local = math.sqrt(math.pow(l[0] - loc[0], 2) + math.pow(l[1] - loc[1], 2))
            return min_local

    def getManhatanDistance(self, loc, l):
        if l == self.game.board_size * self.game.board_size:
            return l
        else:
            min_local = math.fabs(l[0] - loc[0]) + math.fabs(l[1] - loc[1])
            return min_local

    def score(self, now, next_move):
        sc = 0

        if next_move == "North":
            next_f = [now[0] - 1, now[1]]
        elif next_move == "East":
            next_f = [now[0], now[1] + 1]
        elif next_move == "South":
            next_f = [now[0] + 1, now[1]]
        elif next_move == "West":
            next_f = [now[0], now[1] - 1]
        else:
            next_f = now

        t = tuple(next_f)
        if ((t not in self.game.walls_locs) & (next_f[0] >= 0) &(next_f[0] < self.game.board_size) & (next_f[1] >= 0) &(next_f[1] < self.game.board_size)):
            enemy_mines = tuple(list(set(self.game.mines_locs) - set(self.game.hero.mines)))

            #reward and punishment for geting away from closest mine
            if (self.game.hero.life > 30) & (self.getDistance(now, self.getClosest(now, enemy_mines)) > \
                    self.getDistance(next_f, self.getClosest(next_f, enemy_mines))):
                sc += 50
            elif (self.game.hero.life > 30) & (self.getDistance(now, self.getClosest(now, enemy_mines)) < \
                    self.getDistance(next_f, self.getClosest(next_f, enemy_mines))):
                sc -= 50


            #reward for life restoring
            if (self.game.hero.life < 30) & (self.getDistance(now, self.getClosest(now, self.game.taverns_locs)) > self.getDistance(next_f, self.getClosest(next_f, self.game.taverns_locs))):
                sc += 50
            if (self.game.hero.life < 30) & (self.getDistance(now, self.getClosest(now, self.game.taverns_locs)) < self.getDistance(next_f, self.getClosest(next_f, self.game.taverns_locs))):
                sc -= 50

            #punishment for running into not penetrable
            if (((self.game.hero.life > 70) & (t in self.game.taverns_locs)) | (t in self.game.hero.mines)):
                sc = -1000

            # reward distances between heroes
            enemies = list()
            for e in self.game.heroes:
                if e.bot_id is not self.game.hero.bot_id:
                    enemies.append(e)

            if (((self.game.hero.life > enemies[0].life) & (t == enemies[0].pos)) | ((self.game.hero.life > enemies[1].life) & (t == enemies[1].pos)) | ((self.game.hero.life > enemies[2].life) & (t == enemies[2].pos))):
                sc += 100
            elif (((self.game.hero.life <= enemies[0].life) & (t == enemies[0].pos)) | ((self.game.hero.life <= enemies[1].life) & (t == enemies[1].pos)) | ((self.game.hero.life <= enemies[2].life) & (t == enemies[2].pos))):
                sc -= 100

            #punish staying in place
            if next_move == "Stay":
                sc -= 200
        else:
            sc = -1000
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
