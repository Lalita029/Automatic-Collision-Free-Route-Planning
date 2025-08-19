import time
import random
import numpy as np
import math
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.robot_controller import RobotController
from src.computer_vision import ComputerVision
from src.path_planning import PathPlanner
from config.config import Config

class AutonomousRobot:
    def __init__(self):
        self.config = Config()
        self.robot_controller = RobotController(self.config.SIMULATOR_URL)
        self.computer_vision = ComputerVision(self.config)
        self.path_planner = PathPlanner(self.config)
        self.obstacle_map = np.zeros(self.config.MAP_SIZE, dtype=np.uint8)
        self.goal_position = None

    def set_goal_position(self):
        """Set the goal position dynamically near one of the corners."""
        margin = self.config.GOAL_MARGIN
        corners = [
            (margin, margin),  # Top-left
            (self.config.MAP_SIZE[0] - margin, margin),  # Top-right
            (margin, self.config.MAP_SIZE[1] - margin),  # Bottom-left
            (self.config.MAP_SIZE[0] - margin, self.config.MAP_SIZE[1] - margin)  # Bottom-right
        ]

        # Choose a random corner
        self.goal_position = random.choice(corners)
        print(f"Goal position set to: {self.goal_position}")

    def navigate_to_goal(self):
        """Navigate the robot to the goal position while avoiding obstacles."""
        print("Starting navigation...")
        self.robot_controller.get_robot_position()  # Initialize the current position
        print(f"Initial position: {self.robot_controller.current_position}")
        self.set_goal_position()  # Set the goal position

        # Check if position was retrieved successfully
        if self.robot_controller.current_position is None:
            print("Failed to get initial robot position!")
            return

        # Main navigation loop
        step_count = 0
        while np.linalg.norm(np.array(self.robot_controller.current_position) - np.array(self.goal_position)) > 10:
            step_count += 1
            print(f"Step {step_count}: Current position: {self.robot_controller.current_position}, Goal: {self.goal_position}")

            # Capture an image
            image = self.robot_controller.capture_image()
            if image is None:
                print("Failed to capture image. Retrying...")
                time.sleep(1)
                continue

            # Detect obstacles and update the obstacle map
            obstacles = self.computer_vision.detect_obstacles(image, self.obstacle_map)
            print(f"Detected {len(obstacles)} obstacles")

            # Plan a path using A*
            path = self.path_planner.plan_path_astar(
                self.robot_controller.current_position,
                self.goal_position,
                self.obstacle_map
            )

            if not path or len(path) < 2:
                print("No path found. Trying to move randomly...")
                # Try to move in a random direction with larger steps
                angle = random.uniform(0, 360)
                dx = 30 * math.cos(math.radians(angle))
                dy = 30 * math.sin(math.radians(angle))
                self.robot_controller.move_robot_relative(dx, dy)
                continue

            # Move to the next waypoint in the path
            next_waypoint = path[1]

            # Calculate the direction and distance to the next waypoint
            dx = next_waypoint[0] - self.robot_controller.current_position[0]
            dy = next_waypoint[1] - self.robot_controller.current_position[1]
            distance = np.sqrt(dx**2 + dy**2)

            # Normalize and scale the movement
            if distance > 0:
                dx = dx / distance * min(distance, self.config.STEP_SIZE)
                dy = dy / distance * min(distance, self.config.STEP_SIZE)

                # Move towards the waypoint
                print(f"Moving by dx={dx:.2f}, dy={dy:.2f}")
                if not self.robot_controller.move_robot_relative(dx, dy):
                    print("Move failed, trying random direction")
                    # If the move failed, try to move in a different direction with larger steps
                    angle = random.uniform(0, 360)
                    dx = 30 * math.cos(math.radians(angle))
                    dy = 30 * math.sin(math.radians(angle))
                    self.robot_controller.move_robot_relative(dx, dy)
                else:
                    print(f"Move successful, new position: {self.robot_controller.current_position}")

            # Small delay to prevent overwhelming the server (reduced for faster movement)
            time.sleep(0.05)

        print(f"Reached the goal! Collisions: {self.robot_controller.collision_count}")

def main():
    robot = AutonomousRobot()
    robot.navigate_to_goal()

if __name__ == "__main__":
    main()
