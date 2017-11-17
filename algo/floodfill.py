import numpy as np

from array_map import ArrayMap

class FloodFiller:
    EMPTY = -1
    def __init__(self, amap):
        self.sy, self.sx, _ = amap.state.shape
        self.field = np.ones((self.sy, self.sx), dtype=np.int) * self.EMPTY
        self.amap = amap

    def clear(self):
        self.field[...] = FloodFiller.EMPTY

    def fill_from(self, pos):  # pos = (y,x)
        """ Runs a wave from pos until whole map in visited """
        self.set(pos, 0)
        front = list(self._neighs(pos))
        dist = 1


        while len(front) > 0:
            next_front = []
            while len(front) > 0:
                p = front.pop()
                self.set(p, dist)
                if self.amap.is_passable(p):
                    next_front += filter(lambda npos: self.get(npos) == self.EMPTY, self._neighs(p))
            front = next_front
            dist += 1

    def path_to(self, pos):
        v = self.get(pos)
        if v == self.EMPTY:
            return None

        path = [pos]
        while v > 1:
            v -= 1
            pos = next(filter(lambda p: self.get(p) == v and self.amap.is_passable(p), self._neighs(pos)))
            path.append(pos)

        path.reverse()
        return path

    def get(self, pos):
        return self.field[pos[0],pos[1]]

    def set(self, pos, v):
        self.field[pos[0],pos[1]] = v

    def print(self):
        for y in range(self.sy):
            for x in range(self.sx):
                print("%2d " % self.get((y, x)), end='')
            print("")

    def _neighs(self, pos):

        neighs = [(pos[0]-1, pos[1]), (pos[0]+1, pos[1]), (pos[0], pos[1]-1), (pos[0], pos[1]+1)]
        return filter(lambda p: 0 <= p[0] < self.sy and 0 <= p[1] < self.sx, neighs)

