import requests
import numpy as np
# import cv2  # Temporarily disabled

class RobotController:
    def __init__(self, simulator_url):
        self.simulator_url = simulator_url
        self.current_position = None
        self.current_orientation = None
        self.collision_count = 0

    def capture_image(self):
        """Capture an image from the robot's camera using the /capture endpoint."""
        try:
            response = requests.get(f"{self.simulator_url}/capture", timeout=5)
            if response.status_code == 200:
                # For now, return a dummy image since we simplified the camera
                # Create a simple 480x640x3 image
                dummy_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
                return dummy_image
            else:
                print(f"Error capturing image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception capturing image: {str(e)}")
            return None

    def get_robot_position(self):
        """Get the current position and orientation of the robot."""
        try:
            response = requests.get(f"{self.simulator_url}/position", timeout=5)
            if response.status_code == 200:
                position_data = response.json()
                self.current_position = (position_data['x'], position_data['y'])
                self.current_orientation = position_data['orientation']
                return self.current_position + (self.current_orientation,)
            else:
                print(f"Error getting robot position: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception getting robot position: {str(e)}")
            return None

    def move_robot_relative(self, dx, dy):
        """Move the robot by the specified relative distances."""
        try:
            response = requests.post(
                f"{self.simulator_url}/move_rel",
                json={"dx": dx, "dy": dy},
                timeout=5
            )

            if response.status_code == 200:
                self.get_robot_position()  # Update the current position
                return True
            else:
                print(f"Error moving robot: {response.status_code}")
                self.collision_count += 1
                return False
        except Exception as e:
            print(f"Exception moving robot: {str(e)}")
            self.collision_count += 1
            return False
