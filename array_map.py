import numpy as np
from game import Game

class ArrayMap:
    """ More convenient map representation based on 3d numpy array """

    OBJECTS_LAYER, OWNING_LAYER = np.arange(2)
    NEUTRAL, OWNED, ENEMY, MASTER, SERVANT = np.arange(5)
    EMPTY, TAVERN, HERO, SPAWNPOINT, MINE, WALL = np.arange(6)
    IMPASSABLE_TERRAIN = [TAVERN, MINE, WALL]

    def __init__(self, gameobj):
        if not isinstance(gameobj, Game):
            raise TypeError("wrong object")

        self.state = np.zeros((gameobj.board_size, gameobj.board_size, 2), dtype=np.uint8)

        me = gameobj.hero
        self.ownersDict = {0: self.NEUTRAL}
        for h in gameobj.heroes:
            if h.name == me.name:
                bot_id = h.bot_id
                if bot_id < me.bot_id:
                    self.ownersDict[bot_id] = self.MASTER
                elif bot_id > me.bot_id:
                    self.ownersDict[bot_id] = self.SERVANT
                else:
                    self.ownersDict[bot_id] = self.OWNED
            else:
                self.ownersDict[h.bot_id] = self.ENEMY

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
            self.state[pos[0], pos[1], self.OWNING_LAYER] = self.ownersDict[owner]

        # Mark Spawn Points
        for pos, owner in gameobj.spawn_points_locs.items():
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.SPAWNPOINT
            self.state[pos[0], pos[1], self.OWNING_LAYER] = self.ownersDict[owner]

        # Mark Terrain
        for pos in gameobj.walls_locs:
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.WALL
            self.state[pos[0], pos[1], self.OWNING_LAYER] = self.NEUTRAL

        # Mark Taverns
        for pos in gameobj.taverns_locs:
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.TAVERN
            self.state[pos[0], pos[1], self.OWNING_LAYER] = self.NEUTRAL

        # Mark Heroes
        for i in range(len(gameobj.heroes)):
            pos = gameobj.heroes[i].pos
            owner = gameobj.heroes[i].bot_id
            self.state[pos[0], pos[1], self.OBJECTS_LAYER] = self.HERO
            self.state[pos[0], pos[1], self.OWNING_LAYER] = self.ownersDict[owner]

    def get_obj(self, y, x):
        return self.state[y, x, ArrayMap.OBJECTS_LAYER]

    def get(self, y, x):
        return self.state[y, x, ArrayMap.OBJECTS_LAYER], self.state[y, x, ArrayMap.OWNING_LAYER]
