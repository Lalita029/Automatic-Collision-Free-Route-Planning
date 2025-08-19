import unittest
import numpy as np
from src.path_planning import PathPlanner
from config.config import Config

class TestPathPlanner(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.path_planner = PathPlanner(self.config)
        self.obstacle_map = np.zeros(self.config.MAP_SIZE, dtype=np.uint8)

    def test_heuristic(self):
        a = (0, 0)
        b = (3, 4)
        expected = 5.0
        result = self.path_planner.heuristic(a, b)
        self.assertAlmostEqual(result, expected, places=5)

    def test_get_neighbors(self):
        pos = (500, 500)
        neighbors = self.path_planner.get_neighbors(pos, self.obstacle_map)
        self.assertEqual(len(neighbors), 8)  # All 8 neighbors should be valid

    def test_plan_path_astar(self):
        start = (0, 0)
        goal = (10, 10)
        path = self.path_planner.plan_path_astar(start, goal, self.obstacle_map)
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

if __name__ == '__main__':
    unittest.main()
