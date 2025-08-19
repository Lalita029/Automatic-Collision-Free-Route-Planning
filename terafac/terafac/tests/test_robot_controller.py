import unittest
from unittest.mock import patch, MagicMock
from src.robot_controller import RobotController
from config.config import Config

class TestRobotController(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.robot_controller = RobotController(self.config.SIMULATOR_URL)

    @patch('requests.get')
    def test_capture_image(self, mock_get):
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\xff\xd9'
        mock_get.return_value = mock_response

        image = self.robot_controller.capture_image()
        self.assertIsNotNone(image)

    @patch('requests.get')
    def test_get_robot_position(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'x': 100, 'y': 200, 'orientation': 90}
        mock_get.return_value = mock_response

        position = self.robot_controller.get_robot_position()
        self.assertEqual(position, (100, 200, 90))

    @patch('requests.post')
    @patch('requests.get')
    def test_move_robot_relative(self, mock_get, mock_post):
        # Mock the position update
        mock_get.return_value = MagicMock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'x': 110, 'y': 210, 'orientation': 90}

        # Mock the move request
        mock_post.return_value = MagicMock()
        mock_post.return_value.status_code = 200

        result = self.robot_controller.move_robot_relative(10, 10)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
