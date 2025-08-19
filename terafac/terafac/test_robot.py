#!/usr/bin/env python3
import requests
import time

def test_robot():
    base_url = "http://localhost:5000"
    
    # Test getting position
    print("Testing position endpoint...")
    response = requests.get(f"{base_url}/position")
    print(f"Position response: {response.json()}")
    
    # Test moving robot
    print("Testing movement...")
    for i in range(5):
        print(f"Move {i+1}: Moving right by 10 pixels")
        response = requests.post(f"{base_url}/move_rel", json={"dx": 10, "dy": 0})
        if response.status_code == 200:
            print(f"Move successful: {response.json()}")
        else:
            print(f"Move failed: {response.status_code}")
        
        # Get new position
        response = requests.get(f"{base_url}/position")
        print(f"New position: {response.json()}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    test_robot()
