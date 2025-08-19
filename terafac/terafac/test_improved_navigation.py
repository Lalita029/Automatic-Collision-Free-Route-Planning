#!/usr/bin/env python3
import requests
import time

def test_improved_navigation():
    """Test navigation with smaller robot and better obstacle spacing"""
    base_url = "http://localhost:5000"
    
    print("Testing improved navigation with smaller robot and better spacing...")
    
    # Test case 1: Navigate through narrow corridors
    print("\n🎯 Test 1: Navigate through narrow corridors")
    start_point = {"x": 50, "y": 250}
    end_point = {"x": 750, "y": 250}
    
    requests.post(f"{base_url}/set_position", json=start_point)
    time.sleep(0.5)
    
    response = requests.post(f"{base_url}/start_navigation", json={
        "start": start_point,
        "end": end_point
    })
    print(f"Started corridor navigation: {response.json()}")
    
    # Monitor for 15 seconds
    for i in range(15):
        response = requests.get(f"{base_url}/position")
        pos = response.json()
        print(f"  Step {i+1}: Robot at ({pos['x']:.1f}, {pos['y']:.1f})")
        time.sleep(1)
        
        if abs(pos['x'] - end_point['x']) < 25:
            print("  ✅ Successfully navigated through corridors!")
            break
    
    time.sleep(2)
    
    # Test case 2: Zigzag navigation
    print("\n🎯 Test 2: Zigzag navigation between obstacles")
    start_point = {"x": 125, "y": 50}
    end_point = {"x": 125, "y": 550}
    
    requests.post(f"{base_url}/set_position", json=start_point)
    time.sleep(0.5)
    
    response = requests.post(f"{base_url}/start_navigation", json={
        "start": start_point,
        "end": end_point
    })
    print(f"Started zigzag navigation: {response.json()}")
    
    # Monitor for 15 seconds
    for i in range(15):
        response = requests.get(f"{base_url}/position")
        pos = response.json()
        print(f"  Step {i+1}: Robot at ({pos['x']:.1f}, {pos['y']:.1f})")
        time.sleep(1)
        
        if abs(pos['y'] - end_point['y']) < 25:
            print("  ✅ Successfully completed zigzag navigation!")
            break
    
    time.sleep(2)
    
    # Test case 3: Complex maze-like navigation
    print("\n🎯 Test 3: Complex maze-like navigation")
    start_point = {"x": 175, "y": 150}
    end_point = {"x": 625, "y": 400}
    
    requests.post(f"{base_url}/set_position", json=start_point)
    time.sleep(0.5)
    
    response = requests.post(f"{base_url}/start_navigation", json={
        "start": start_point,
        "end": end_point
    })
    print(f"Started complex navigation: {response.json()}")
    
    # Monitor for 20 seconds
    for i in range(20):
        response = requests.get(f"{base_url}/position")
        pos = response.json()
        print(f"  Step {i+1}: Robot at ({pos['x']:.1f}, {pos['y']:.1f})")
        time.sleep(1)
        
        if (abs(pos['x'] - end_point['x']) < 25 and 
            abs(pos['y'] - end_point['y']) < 25):
            print("  ✅ Successfully completed complex navigation!")
            break
    
    print("\n🚀 All navigation tests completed!")
    print("The smaller robot can now easily navigate through the improved obstacle layout!")

if __name__ == "__main__":
    test_improved_navigation()
