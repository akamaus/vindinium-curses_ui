
import json
import numpy
import time
from game import Game


NEUTRAL, OWNED, ENEMY, MASTER, SERVANT = numpy.arange(5) / 5

EMPTY, TAVERN, HERO, SPAWNPOINT, MINE, TERRAIN = numpy.arange(6) / 6

class MapConverter:
    @staticmethod
    def convertMap(gameobj):
        if not isinstance(gameobj, Game):
            raise Exception("wrong object")

        me = gameobj.hero
        ownersDict = {0 : NEUTRAL}
        for h in gameobj.heroes:
            if h.name == me.name:
                bot_id = h.bot_id
                if bot_id < me.bot_id:
                    ownersDict[bot_id] = MASTER
                elif bot_id > me.bot_id:
                    ownersDict[bot_id] = SERVANT
                else:
                    ownersDict[bot_id] = OWNED
            else:
                ownersDict[h.bot_id] = ENEMY

        state = numpy.zeros((gameobj.board_size, gameobj.board_size, 2))

        # Mark Mines
        for pos, owner in gameobj.mines.iteritems():
            if owner == "-":
                owner = NEUTRAL
            owner = int(owner)
            state[pos[0]][pos[1]][0] = MINE
            state[pos[0]][pos[1]][1] = ownersDict[owner]

        # Mark Spawn Points
        for pos, owner in gameobj.spawn_points_locs.iteritems():
            state[pos[0]][pos[1]][0] = SPAWNPOINT
            state[pos[0]][pos[1]][1] = ownersDict[owner]

        # Mark Terrain
        for pos in gameobj.walls_locs:
            state[pos[0]][pos[1]][0] = TERRAIN
            state[pos[0]][pos[1]][1] = NEUTRAL

        # Mark Taverns
        for pos in gameobj.taverns_locs:
            state[pos[0]][pos[1]][0] = TAVERN
            state[pos[0]][pos[1]][1] = NEUTRAL

        # Mark Heroes
        for i in range(len(gameobj.heroes)):
            pos = gameobj.heroes[i].pos
            owner = gameobj.heroes[i].bot_id
            state[pos[0]][pos[1]][0] = HERO
            state[pos[0]][pos[1]][1] = ownersDict[owner]

        return state

if __name__ == "__main__":
    for i in range(60):
        start_time = time.time()

        with open('exampleMap.json') as data_file:
            data = json.load(data_file)

        gameobj = Game(data)
        d3 = MapConverter.convertMap(gameobj)
        # for layer in range(len(d3)):
        #     print("Layer ", layer)
        #     for row in range(len(d3[layer])):
        #         print d3[layer][row]
        print("%d --- %s seconds ---" % (i, time.time() - start_time))

