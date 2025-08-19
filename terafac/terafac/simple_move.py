#!/usr/bin/env python3
import requests
import time
import sys

def move_robot():
    try:
        print("Starting robot movement test...")
        
        # Move right
        print("Moving right...")
        response = requests.post("http://localhost:5000/move_rel", json={"dx": 30, "dy": 0}, timeout=5)
        print(f"Right move: {response.status_code}")
        time.sleep(1)
        
        # Move down
        print("Moving down...")
        response = requests.post("http://localhost:5000/move_rel", json={"dx": 0, "dy": 30}, timeout=5)
        print(f"Down move: {response.status_code}")
        time.sleep(1)
        
        # Move left
        print("Moving left...")
        response = requests.post("http://localhost:5000/move_rel", json={"dx": -30, "dy": 0}, timeout=5)
        print(f"Left move: {response.status_code}")
        time.sleep(1)
        
        # Move up
        print("Moving up...")
        response = requests.post("http://localhost:5000/move_rel", json={"dx": 0, "dy": -30}, timeout=5)
        print(f"Up move: {response.status_code}")
        
        print("Movement test completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    move_robot()
