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

           obj, own = am.get(3, 7)
           self.assertEqual(obj, ArrayMap.MINE)
           self.assertEqual(own, ArrayMap.OWNED)

           obj, own = am.get(5, 6)
           self.assertEqual(obj, ArrayMap.HERO)
           self.assertEqual(own, ArrayMap.MASTER)

           obj, own = am.get(12, 11)
           self.assertEqual(obj, ArrayMap.HERO)
           self.assertEqual(own, ArrayMap.ENEMY)



if __name__ == '__main__':
    unittest.main()
