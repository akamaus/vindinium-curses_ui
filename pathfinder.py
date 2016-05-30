import random
import Queue
from mapConverter import *

class Node:
    def __init__(self, coordinates, parent):
        self.parent = parent
        self.coordinates = coordinates
        self.children = []

    def __str__(self):
        return "%i,%i" % self.coordinates

    def __repr__(self):
        return self.__str__()

    def neighbours(self):
        directions = [(-1,0), (0,-1), (1,0), (0,1) ]
        neighs = []
        for d in directions:
            a = (self.coordinates[0]+d[0], self.coordinates[1]+d[1])
            neighs.append(a)
        return neighs

    def has_child(self, target):
        result = False
        if self.coordinates == target:
            return True
        for child in self.children:
            result = result or child.has_child(target)
        return result


class Pathfinder:
    def __init__(self, fullmap=None):
        self._gamemap = fullmap

    def find_route(self, start, end):
        gamemap = self._gamemap[:, :, OBJECTS_LAYER]
        map_size = gamemap.shape

        if gamemap[start] in IMPASSABLE_TERRAIN or gamemap[end] == TERRAIN:
            return []

        start = Node(start, None)
        queue = Queue.Queue()
        queue.put_nowait(start)

        endNode = None
        while (not queue.empty()) and (endNode is None):
            n = queue.get_nowait()

            if not gamemap[(n.coordinates[0], n.coordinates[1])] in IMPASSABLE_TERRAIN:
                neigh = n.neighbours()
                proper_neigh = [nod
                                for nod in neigh
                                if 0 <= nod[0] < map_size[0]
                                and 0 <= nod[1] < map_size[1]]
                unvisited_neigh = [Node(nod, n)
                                   for nod in proper_neigh
                                   if not start.has_child(nod)]
                n.children = unvisited_neigh

                if(end in [ch.coordinates for ch in n.children]):
                    endNode = next((endNode for endNode in n.children if endNode.coordinates == end), None)
                else:
                    for nod in n.children:
                        if not start.has_child(nod):
                            queue.put_nowait(nod)
            # print "From %s,%s to %s" % n.coordinates, " ".join(n.children)
        result_path = []
        while endNode is not None:
            result_path.insert(0, endNode)
            endNode = endNode.parent

        return result_path

if __name__ == '__main__':
    node = Node((3,5),None)
    print node.__str__()
    print(node.neighbours())

    map = numpy.zeros((28,28,2))

    for i in range(20):
        map[random.randint(0,27), random.randint(0,27), OBJECTS_LAYER] = TERRAIN

    p = Pathfinder(map)
    path = p.find_route((random.randint(0,27),random.randint(0,27)), (random.randint(0,27),random.randint(0,27)))
    print (path)
