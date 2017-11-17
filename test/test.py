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

            obj, rel = am.get_rel(3, 7)
            _, own = am.get_abs(3, 7)
            self.assertEqual(obj, ArrayMap.MINE)
            self.assertEqual(rel, ArrayMap.OWNED)
            self.assertEqual(own, int(g.hero.bot_id))

            obj, rel = am.get_rel(5, 6)
            _, own = am.get_abs(5, 6)
            self.assertEqual(obj, ArrayMap.HERO)
            self.assertEqual(rel, ArrayMap.MASTER)
            self.assertEqual(own, 1)

            obj, rel = am.get_rel(12, 11)
            _, own = am.get_abs(12, 11)
            self.assertEqual(obj, ArrayMap.HERO)
            self.assertEqual(rel, ArrayMap.ENEMY)
            self.assertEqual(own, 3)



if __name__ == '__main__':
    unittest.main()
