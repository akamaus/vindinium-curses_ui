import numpy as np
from game import Game

class ArrayMap:
    """ More convenient map representation based on 3d numpy array """

    # layers for objects, owner bot-id's, owner relations to player
    NUM_LAYERS = 3
    OBJECTS_LAYER, OWNING_LAYER, RELATION_LAYER = np.arange(NUM_LAYERS)
    NEUTRAL, OWNED, ENEMY, MASTER, SERVANT = np.arange(5)
    EMPTY, TAVERN, HERO, SPAWNPOINT, MINE, WALL = np.arange(6)
    IMPASSABLE_TERRAIN = [TAVERN, MINE, WALL]

    def __init__(self, gameobj):
        if not isinstance(gameobj, Game):
            raise TypeError("wrong object")

        self.state = np.zeros((gameobj.board_size, gameobj.board_size, self.NUM_LAYERS), dtype=np.uint8)

        me = gameobj.hero
        self.relOwnersDict = {0: self.NEUTRAL}
        for h in gameobj.heroes:
            if h.name == me.name:
                bot_id = h.bot_id
                if bot_id < me.bot_id:
                    self.relOwnersDict[bot_id] = self.MASTER
                elif bot_id > me.bot_id:
                    self.relOwnersDict[bot_id] = self.SERVANT
                else:
                    self.relOwnersDict[bot_id] = self.OWNED
            else:
                self.relOwnersDict[h.bot_id] = self.ENEMY

        self.convertMap(gameobj)

    def convertMap(self, gameobj):
        if not isinstance(gameobj, Game):
            raise TypeError("wrong object")

        self.state[...] = 0

        # Mark Mines
        for pos, owner in gameobj.mines.items():
            if owner == '-':
                owner = self.NEUTRAL
            owner = int(owner)
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.MINE
            self.state[pos[0], pos[1], self.OWNING_LAYER] = owner
            self.state[pos[0], pos[1], self.RELATION_LAYER] = self.relOwnersDict[owner]

        # Mark Spawn Points
        for pos, owner in gameobj.spawn_points_locs.items():
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.SPAWNPOINT
            self.state[pos[0], pos[1], self.OWNING_LAYER] = int(owner)
            self.state[pos[0], pos[1], self.RELATION_LAYER] = self.relOwnersDict[owner]

        # Mark Terrain
        for pos in gameobj.walls_locs:
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.WALL
            self.state[pos[0], pos[1], self.RELATION_LAYER] = self.NEUTRAL

        # Mark Taverns
        for pos in gameobj.taverns_locs:
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.TAVERN
            self.state[pos[0], pos[1], self.RELATION_LAYER] = self.NEUTRAL

        # Mark Heroes
        for i in range(len(gameobj.heroes)):
            pos = gameobj.heroes[i].pos
            owner = gameobj.heroes[i].bot_id
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.HERO
            self.state[pos[0], pos[1], self.OWNING_LAYER] = int(owner)
            self.state[pos[0], pos[1], self.RELATION_LAYER] = self.relOwnersDict[owner]

    def get(self, p):
        return self.state[p[0], p[1], ArrayMap.OBJECTS_LAYER]

    def get_rel(self, p):
        return self.state[p[0], p[1], ArrayMap.OBJECTS_LAYER], self.state[p[0], p[1], ArrayMap.RELATION_LAYER]

    def get_abs(self, p):
        return self.state[p[0], p[1], ArrayMap.OBJECTS_LAYER], self.state[p[0], p[1], ArrayMap.OWNING_LAYER]
