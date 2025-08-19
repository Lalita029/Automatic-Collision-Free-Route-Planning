#!/usr/bin/env python3
import requests
import time
import math

def fast_robot_demo():
    """Demonstrate fast robot movement in various patterns"""
    base_url = "http://localhost:5000"
    
    print("Starting fast robot demonstration...")
    
    # Reset robot to center
    requests.post(f"{base_url}/reset")
    time.sleep(0.1)
    
    # Pattern 1: Fast square movement
    print("Pattern 1: Fast square movement")
    moves = [
        (50, 0),   # Right
        (0, 50),   # Down  
        (-50, 0),  # Left
        (0, -50)   # Up
    ]
    
    for dx, dy in moves * 2:  # Do it twice
        requests.post(f"{base_url}/move_rel", json={"dx": dx, "dy": dy})
        time.sleep(0.1)
    
    time.sleep(0.5)
    
    # Pattern 2: Circular movement
    print("Pattern 2: Circular movement")
    for i in range(16):
        angle = i * (2 * math.pi / 16)
        dx = 25 * math.cos(angle)
        dy = 25 * math.sin(angle)
        requests.post(f"{base_url}/move_rel", json={"dx": dx, "dy": dy})
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    # Pattern 3: Zigzag movement
    print("Pattern 3: Zigzag movement")
    for i in range(8):
        dx = 30 if i % 2 == 0 else -30
        dy = 20
        requests.post(f"{base_url}/move_rel", json={"dx": dx, "dy": dy})
        time.sleep(0.1)
    
    print("Fast demonstration completed!")

if __name__ == "__main__":
    fast_robot_demo()
