import math
import numpy as np
from queue import PriorityQueue

class PathPlanner:
    def __init__(self, config):
        self.config = config

    def heuristic(self, a, b):
        """Calculate the heuristic (Euclidean distance) between two points."""
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def get_neighbors(self, pos, obstacle_map):
        """Get the valid neighbors of a position."""
        x, y = pos
        neighbors = []

        # Check all 8 possible directions if diagonal movement is allowed
        if self.config.DIAGONAL_MOVEMENT:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        else:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if the neighbor is within the map bounds
            if 0 <= nx < self.config.MAP_SIZE[0] and 0 <= ny < self.config.MAP_SIZE[1]:
                # Check if the neighbor is not an obstacle
                if obstacle_map[nx, ny] == 0:
                    neighbors.append((nx, ny))

        return neighbors

    def plan_path_astar(self, start, goal, obstacle_map):
        """Plan a path from the current position to the goal using the A* algorithm."""
        # Initialize the open and closed sets
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        open_set_hash = {start}

        while not open_set.empty():
            current = open_set.get()[1]
            open_set_hash.remove(current)

            # If we've reached the goal, reconstruct the path
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            # Check all neighbors
            for neighbor in self.get_neighbors(current, obstacle_map):
                # Calculate the tentative g score
                tentative_g_score = g_score[current] + self.heuristic(current, neighbor)

                # If this path to the neighbor is better than any previous one
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

                    if neighbor not in open_set_hash:
                        open_set.put((f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

        # If we get here, no path was found
        print("No path found using A*")
        return []
