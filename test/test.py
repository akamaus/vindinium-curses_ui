import json
import unittest
from unittest import TestCase, TestSuite, TestLoader

from array_map import ArrayMap
from game import Game


class TestDataStructures(TestCase):
    def test_arraymap_conversion(self):
        with open('test/exampleMap.json', 'r') as f:
            state = json.load(f)
            g = Game(state)
            am = ArrayMap(g)

            p0 = (3, 7)
            obj, rel = am.get_rel(p0)
            _, own = am.get_abs(p0)
            self.assertEqual(obj, ArrayMap.MINE)
            self.assertEqual(rel, ArrayMap.OWNED)
            self.assertEqual(own, int(g.hero.bot_id))

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



if __name__ == '__main__':
    unittest.main()
