#!/usr/bin/env python3
import requests
import time

def test_point_to_point_navigation():
    """Test the point-to-point navigation functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing point-to-point navigation...")
    
    # Test case 1: Simple navigation
    print("\nTest 1: Simple navigation from top-left to bottom-right")
    start_point = {"x": 100, "y": 100}
    end_point = {"x": 700, "y": 500}
    
    # Set robot to start position
    response = requests.post(f"{base_url}/set_position", json=start_point)
    print(f"Set start position: {response.json()}")
    time.sleep(1)
    
    # Start navigation
    response = requests.post(f"{base_url}/start_navigation", json={
        "start": start_point,
        "end": end_point
    })
    print(f"Started navigation: {response.json()}")
    
    # Monitor progress
    for i in range(20):
        response = requests.get(f"{base_url}/position")
        pos = response.json()
        print(f"Step {i+1}: Robot at ({pos['x']:.1f}, {pos['y']:.1f})")
        time.sleep(1)
        
        # Check if reached destination
        if abs(pos['x'] - end_point['x']) < 30 and abs(pos['y'] - end_point['y']) < 30:
            print("✅ Reached destination!")
            break
    
    time.sleep(2)
    
    # Test case 2: Navigation around obstacles
    print("\nTest 2: Navigation around obstacles")
    start_point = {"x": 50, "y": 200}
    end_point = {"x": 750, "y": 200}
    
    # Set robot to start position
    requests.post(f"{base_url}/set_position", json=start_point)
    time.sleep(1)
    
    # Start navigation
    response = requests.post(f"{base_url}/start_navigation", json={
        "start": start_point,
        "end": end_point
    })
    print(f"Started obstacle avoidance navigation: {response.json()}")
    
    # Monitor progress
    for i in range(25):
        response = requests.get(f"{base_url}/position")
        pos = response.json()
        print(f"Step {i+1}: Robot at ({pos['x']:.1f}, {pos['y']:.1f})")
        time.sleep(1)
        
        # Check if reached destination
        if abs(pos['x'] - end_point['x']) < 30 and abs(pos['y'] - end_point['y']) < 30:
            print("✅ Successfully navigated around obstacles!")
            break
    
    print("\nNavigation test completed!")

if __name__ == "__main__":
    test_point_to_point_navigation()
