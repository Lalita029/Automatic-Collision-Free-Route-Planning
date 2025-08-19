import unittest
import numpy as np
import cv2
from src.computer_vision import ComputerVision
from config.config import Config

class TestComputerVision(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.computer_vision = ComputerVision(self.config)
        self.obstacle_map = np.zeros(self.config.MAP_SIZE, dtype=np.uint8)

    def test_detect_obstacles(self):
        # Create a test image with a white rectangle (obstacle) on black background
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(image, (40, 40), (60, 60), (255, 255, 255), -1)

        obstacles = self.computer_vision.detect_obstacles(image, self.obstacle_map)
        self.assertEqual(len(obstacles), 1)
        self.assertEqual(obstacles[0], (50, 50))

if __name__ == '__main__':
    unittest.main()
