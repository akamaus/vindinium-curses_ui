from pathfinder import *
import math

class ConvNetTeacherAI:
    def __init__(self):
        self.p = None


    def process(self, game):
        """Do whatever you need with the Game object game"""
        self.game = game
        if self.p is None:
            map = MapConverter.convertMap(self.game)
            self.p = Pathfinder(map)

    def decide(self):
        actions = ['mine', 'tavern', 'fight']

        decision = []

        path_to_goal = []
        dirs = ["North", "East", "South", "West", "Stay"]

        next = [0, 0, 0, 0, 0]

        enemy_mines = list(set(self.game.mines_locs) - set(self.game.hero.mines))
        closest_enemy_mine = self.getClosest(self.game.hero.pos, enemy_mines)
        nearest_mine_pos = self.getClosest(self.game.hero.pos, self.game.mines_locs)
        nearest_tavern_pos = self.getClosest(self.game.hero.pos, self.game.taverns_locs)

        if (self.game.hero.life >= 30):
            path = self.p.find_route(self.game.hero.pos, closest_enemy_mine)
        else:
            path = self.p.find_route(self.game.hero.pos, self.getClosest(self.game.hero.pos, self.game.taverns_locs))

        # goTo = (random.choice(self.game.mines_locs))

        first_cell = self.game.hero.pos
        path_to_goal = path

        action = actions[0]

        for j in range(0, 5, 1):
            next[j] = self.score(self.game.hero, dirs[j], path)
            decision.append((dirs[j], next[j]))

        hero_move = dirs[next.index(max(next))]

        action = random.choice(actions)

        nearest_enemy_pos = random.choice(self.game.heroes).pos

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
                if (math.fabs(l[0] - loc[0]) + math.fabs(l[1] - loc[1])) < min_local:
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

    def score(self, now, next_dir, path):
        sc = 0

        if next_dir == "North":
            next_f = (now.pos[0] - 1, now.pos[1])
        elif next_dir == "East":
            next_f = (now.pos[0], now.pos[1] + 1)
        elif next_dir == "South":
            next_f = (now.pos[0] + 1, now.pos[1])
        elif next_dir == "West":
            next_f = (now.pos[0], now.pos[1] - 1)
        else:
            next_f = now.pos

        t = next_f
        if ((t not in self.game.walls_locs) & (next_f[0] >= 0) & (next_f[0] < self.game.board_size) &
                (next_f[1] >= 0) & (next_f[1] < self.game.board_size)):
            # reward and punishment for geting away from closest mine

            next_move = path[1]

            if (next_f == next_move.coordinates):
                sc += 1000

                enemies = list()
                for e in self.game.heroes:
                    if e.bot_id is not now.bot_id:
                        enemies.append(e)

                if ((((now.life + 20) > enemies[0].life) & (next_f == enemies[0].pos)) |
                        ((now.life > enemies[1].life) & (next_f == enemies[1].pos)) |
                        ((now.life > enemies[2].life) & (next_f == enemies[2].pos))):
                    sc += 1000
                elif (((now.life <= enemies[0].life) & (next_move == enemies[0].pos)) |
                          ((now.life <= enemies[1].life) & (next_f == enemies[1].pos)) |
                          ((now.life <= enemies[2].life) & (next_f == enemies[2].pos))):
                    sc -= 2000

            # punish staying in place
            if next_dir == "Stay":
                sc -= 2000
        else:
            sc -= 2000
        return sc

    def proportional_probability(self, score):
        sum = 0
        for s in score:
            sum += s
        prob = [float(score[0])/float(sum), float(score[1])/float(sum), float(score[2])/float(sum), float(score[3])/float(sum), float(score[4])/float(sum)]

        return prob

    def post_process(self):
        pass


if __name__ == "__main__":
    with open('exampleMap.json') as data_file:
        data = json.load(data_file)
    gameobj = Game(data)

    ai = ConvNetTeacherAI()
    for i in range(1):
        ai.process(gameobj)
        ai.decide()
        ai.post_process()
        print("%d ---" % i)