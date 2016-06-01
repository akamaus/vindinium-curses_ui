from pathfinder import *
import math

class ExpectiMaxAI:
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
        next_m = [0, 0, 0, 0, 0]
        next = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        prob = [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]]


        # goTo = (random.choice(self.game.mines_locs))

        first_cell = self.game.hero.pos
        path_to_goal.append(first_cell)

        action = actions[0]
        hero_index = self.game.hero.bot_id

        enemies_list = self.game.heroes

        enemies = list()
        for e in self.game.heroes:
            if e.bot_id is not hero_index:
                enemies.append(e)


        foes_score = 0
        for en in enemies_list:
            foes = 0
            for j in range(0, 5, 1):
                fc = enemies_list.index(en) - 1
                next[fc][j] = self.score(en, dirs[j])
            prob[fc] = self.proportional_probability(next[fc])


        for j in range(0, 5, 1):
            foes_score = 0
            for en in enemies_list:
                foes = 0
                ran = random.random()
                for k in range(0, 5, 1):
                    foes += prob[fc][k]
                    if (ran < foes) & (ran >= foes - prob[fc][k]):
                        foes_score += prob[fc][k] * next[fc][k]
            next_m[j] = self.score(self.game.hero, dirs[j]) - foes_score

        hero_move = dirs[next_m.index(max(next_m))]

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

    def score(self, now, next_move):
        sc = 2000

        if next_move == "North":
            next_f = [now.pos[0] - 1, now.pos[1]]
        elif next_move == "East":
            next_f = [now.pos[0], now.pos[1] + 1]
        elif next_move == "South":
            next_f = [now.pos[0] + 1, now.pos[1]]
        elif next_move == "West":
            next_f = [now.pos[0], now.pos[1] - 1]
        else:
            next_f = now.pos

        t = tuple(next_f)
        if ((t not in self.game.walls_locs) & (next_f[0] >= 0) & (next_f[0] < self.game.board_size) &
                (next_f[1] >= 0) & (next_f[1] < self.game.board_size)):
            enemy_mines = tuple(list(set(self.game.mines_locs) - set(self.game.hero.mines)))

            # reward and punishment for geting away from closest mine
            if (now.life > 30) & (self.getDistance(now.pos, self.getClosest(now.pos, enemy_mines)) >
                                                 self.getDistance(next_f, self.getClosest(next_f, enemy_mines))):
                sc += 50
            elif (now.life > 30) & (self.getDistance(now.pos, self.getClosest(now.pos, enemy_mines)) <
                                                   self.getDistance(next_f, self.getClosest(next_f, enemy_mines))):
                sc -= 50

            # reward for life restoring
            if (now.life < 30) & (
                self.getDistance(now.pos, self.getClosest(now.pos, self.game.taverns_locs)) >
                        self.getDistance(next_f, self.getClosest(next_f, self.game.taverns_locs))):
                sc += 50
            if (now.life < 30) & (
                self.getDistance(now.pos, self.getClosest(now.pos, self.game.taverns_locs)) <
                        self.getDistance(next_f, self.getClosest(next_f, self.game.taverns_locs))):
                sc -= 50

            # punishment for running into not penetrable
            if (((now.life > 70) & (t in self.game.taverns_locs)) | (t in now.mines)):
                sc -= 1000

            # reward distances between heroes
            enemies = list()
            for e in self.game.heroes:
                if e.bot_id is not now.bot_id:
                    enemies.append(e)

            if (((now.life > enemies[0].life) & (t == enemies[0].pos)) |
                    ((now.life > enemies[1].life) & (t == enemies[1].pos)) |
                    ((now.life > enemies[2].life) & (t == enemies[2].pos))):
                sc += 100
            elif (((now.life <= enemies[0].life) & (t == enemies[0].pos)) |
                      ((now.life <= enemies[1].life) & (t == enemies[1].pos)) |
                      ((now.life <= enemies[2].life) & (t == enemies[2].pos))):
                sc -= 100

            # punish staying in place
            if next_move == "Stay":
                sc -= 200
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

    ai = ExpectiMaxAI()
    for i in range(1):
        ai.process(gameobj)
        ai.decide()
        ai.post_process()
        print("%d ---" % i)