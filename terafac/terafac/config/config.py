import os

class Config:
    # Simulator settings
    SIMULATOR_URL = os.getenv("SIMULATOR_URL", "http://localhost:5000")

    # Map settings
    MAP_SIZE = (800, 600)  # (width, height)

    # Robot settings
    GOAL_MARGIN = 100  # Distance from the corner when setting the goal

    # Movement settings
    STEP_SIZE = 40  # Maximum step size in pixels (increased for faster movement)

    # Computer vision settings
    OBSTACLE_THRESHOLD = 200  # Threshold for obstacle detection
    MIN_CONTOUR_AREA = 100  # Minimum contour area to be considered an obstacle

    # Path planning settings
    DIAGONAL_MOVEMENT = True  # Allow diagonal movement in A*
