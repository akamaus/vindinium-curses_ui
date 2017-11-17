import json
import unittest
from unittest import TestCase, TestSuite, TestLoader

from array_map import ArrayMap
from game import Game


class TestDataStructures(TestCase):
    ex_f = open('test/exampleMap.json', 'r')
    ex_state = json.load(ex_f)
    ex_game = Game(ex_state)
    ex_amap = ArrayMap(ex_game)

    def test_arraymap_conversion(self):
        am = self.ex_amap

        p0 = (3, 7)
        obj, rel = am.get_rel(p0)
        _, own = am.get_abs(p0)
        self.assertEqual(obj, ArrayMap.MINE)
        self.assertEqual(rel, ArrayMap.OWNED)
        self.assertEqual(own, int(self.ex_game.hero.bot_id))

        p1 = (5, 6)
        obj, rel = am.get_rel(p1)
        _, own = am.get_abs(p1)
        self.assertEqual(obj, ArrayMap.HERO)
        self.assertEqual(rel, ArrayMap.MASTER)
        self.assertEqual(own, 1)

        p2 = (12, 11)
        obj, rel = am.get_rel(p2)
        _, own = am.get_abs(p2)
        self.assertEqual(obj, ArrayMap.HERO)
        self.assertEqual(rel, ArrayMap.ENEMY)
        self.assertEqual(own, 3)

    def test_floodfill(self):
        from algo.floodfill import FloodFiller

        h1 = self.ex_game.heroes[0]
        self.assertEqual(h1.bot_id, 1)

        ff = FloodFiller(self.ex_amap)
        ff.fill_from(self.ex_game.hero.pos)
        r1 = ff.get(h1.pos)
        self.assertEqual(r1, 9)

        path = ff.path_to(h1.pos)
        self.assertEqual(path, [(5, 8), (6, 8), (6, 7), (7, 7), (7, 6), (7, 5), (6, 5), (5, 5), (5, 6)])


if __name__ == '__main__':
    unittest.main()
