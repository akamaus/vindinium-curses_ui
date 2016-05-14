
import json
import sys
from game import Game

NEUTRAL = 0
OWNED = 1
ENEMY = 2
MASTER = 3
SERVANT = 4

EMPTY = 0
TAVERN = 1
HERO = 2
SPAWNPOINT = 3
MINE = 4
TERRAIN = 5

class MapConverter:

    def convertMap(self, gameState):
        if not issubclass(gameState, Game):
            raise Exception("wrong object")

if __name__ == "__main__":
    with open('exampleMap.json') as data_file:
        data = json.load(data_file)

    gameobj = Game(data)

    d3 = [[[0 for col in range(gameobj.board_size)] for row in range(gameobj.board_size)] for x in range(2)]

    # Mark Mines
    for pos, owner in gameobj.mines.iteritems():
        if owner == "-":
            owner = NEUTRAL
        owner = int(owner)
        d3[0][pos[0]][pos[1]] = MINE
        d3[1][pos[0]][pos[1]] = owner
    # Mark Spawn Points
    for pos, owner in gameobj.spawn_points_locs.iteritems():
        d3[0][pos[0]][pos[1]] = SPAWNPOINT
        d3[1][pos[0]][pos[1]] = owner
    # Mark Terrain
    for pos in gameobj.walls_locs:
        d3[0][pos[0]][pos[1]] = TERRAIN
        d3[1][pos[0]][pos[1]] = NEUTRAL
    # Mark Taverns
    for pos in gameobj.taverns_locs:
        d3[0][pos[0]][pos[1]] = TAVERN
        d3[1][pos[0]][pos[1]] = NEUTRAL
    # Mark Heroes
    for i in range(len(gameobj.heroes)):
        pos = gameobj.heroes[i].pos
        owner = gameobj.heroes[i].bot_id
        d3[0][pos[0]][pos[1]] = HERO
        d3[1][pos[0]][pos[1]] = i

    for layer in range(len(d3)):
        print("Layer ", layer)
        for row in range(len(d3[layer])):
            print d3[layer][row]

    print("Bye")

