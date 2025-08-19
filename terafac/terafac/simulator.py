#!/usr/bin/env python3
"""
Simple Robot Simulator with Web UI
Provides HTTP endpoints for robot control and a web interface to visualize the robot.
"""

from flask import Flask, jsonify, request, render_template_string
import json
import threading
import time
import math

app = Flask(__name__)

# Robot state
robot_state = {
    "x": 400,
    "y": 300,
    "orientation": 0,
    "moving": False
}

# Navigation state
navigation_state = {
    "start_point": None,
    "end_point": None,
    "is_navigating": False,
    "path": []
}

# Map and obstacles - redesigned with better spacing for robot navigation
MAP_SIZE = (800, 600)
obstacles = [
    # Top row - with gaps
    {"x": 100, "y": 80, "width": 50, "height": 60},
    {"x": 200, "y": 80, "width": 50, "height": 60},
    {"x": 300, "y": 80, "width": 50, "height": 60},
    {"x": 450, "y": 80, "width": 50, "height": 60},
    {"x": 550, "y": 80, "width": 50, "height": 60},
    {"x": 650, "y": 80, "width": 50, "height": 60},

    # Middle-left section
    {"x": 80, "y": 200, "width": 60, "height": 50},
    {"x": 80, "y": 300, "width": 60, "height": 50},

    # Center obstacles - creating corridors
    {"x": 250, "y": 220, "width": 50, "height": 80},
    {"x": 350, "y": 180, "width": 50, "height": 60},
    {"x": 450, "y": 220, "width": 50, "height": 80},
    {"x": 550, "y": 180, "width": 50, "height": 60},

    # Middle-right section
    {"x": 660, "y": 200, "width": 60, "height": 50},
    {"x": 660, "y": 300, "width": 60, "height": 50},

    # Bottom row - with gaps
    {"x": 100, "y": 460, "width": 50, "height": 60},
    {"x": 200, "y": 460, "width": 50, "height": 60},
    {"x": 350, "y": 460, "width": 50, "height": 60},
    {"x": 450, "y": 460, "width": 50, "height": 60},
    {"x": 600, "y": 460, "width": 50, "height": 60},

    # Additional strategic obstacles
    {"x": 180, "y": 320, "width": 40, "height": 50},
    {"x": 520, "y": 320, "width": 40, "height": 50},
]

# Movement history for trail
movement_history = []
max_history = 100

def generate_camera_image():
    """Generate a simulated camera image with obstacles."""
    # For now, return a simple response indicating camera is working
    # This can be enhanced later with actual image processing
    return b"Camera image placeholder"

def check_point_collision(x, y):
    """Check if a point collides with any obstacle"""
    robot_size = 8  # Robot radius (reduced for smaller robot)
    for obstacle in obstacles:
        if (x - robot_size < obstacle["x"] + obstacle["width"] and
            x + robot_size > obstacle["x"] and
            y - robot_size < obstacle["y"] + obstacle["height"] and
            y + robot_size > obstacle["y"]):
            return True
    return False

def calculate_path(start, end):
    """Calculate a simple path from start to end avoiding obstacles"""
    path = []
    current_x, current_y = start["x"], start["y"]
    target_x, target_y = end["x"], end["y"]

    step_size = 20
    max_steps = 100

    for _ in range(max_steps):
        # Calculate direction to target
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < step_size:
            # Close enough to target
            path.append({"x": target_x, "y": target_y})
            break

        # Normalize direction
        dx = dx / distance * step_size
        dy = dy / distance * step_size

        # Try direct path first
        next_x = current_x + dx
        next_y = current_y + dy

        if not check_point_collision(next_x, next_y):
            # Direct path is clear
            current_x, current_y = next_x, next_y
            path.append({"x": current_x, "y": current_y})
        else:
            # Try to go around obstacle
            # Try perpendicular directions
            for angle_offset in [90, -90, 45, -45, 135, -135]:
                angle = math.atan2(dy, dx) + math.radians(angle_offset)
                test_x = current_x + step_size * math.cos(angle)
                test_y = current_y + step_size * math.sin(angle)

                if (test_x > 20 and test_x < MAP_SIZE[0] - 20 and
                    test_y > 20 and test_y < MAP_SIZE[1] - 20 and
                    not check_point_collision(test_x, test_y)):
                    current_x, current_y = test_x, test_y
                    path.append({"x": current_x, "y": current_y})
                    break
            else:
                # If no direction works, try smaller step
                for smaller_step in [10, 5]:
                    test_x = current_x + dx * smaller_step / step_size
                    test_y = current_y + dy * smaller_step / step_size
                    if not check_point_collision(test_x, test_y):
                        current_x, current_y = test_x, test_y
                        path.append({"x": current_x, "y": current_y})
                        break

    return path

def navigate_to_target():
    """Navigate robot along the calculated path"""
    if not navigation_state["path"]:
        return

    for point in navigation_state["path"]:
        if not navigation_state["is_navigating"]:
            break

        # Move robot to next point
        target_x, target_y = point["x"], point["y"]
        current_x, current_y = robot_state["x"], robot_state["y"]

        # Calculate movement
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 5:  # Only move if not already close
            # Limit movement speed
            max_move = 25
            if distance > max_move:
                dx = dx / distance * max_move
                dy = dy / distance * max_move

            # Update robot position
            new_x = current_x + dx
            new_y = current_y + dy

            # Keep within bounds and check collision
            new_x = max(20, min(MAP_SIZE[0] - 20, new_x))
            new_y = max(20, min(MAP_SIZE[1] - 20, new_y))

            if not check_point_collision(new_x, new_y):
                robot_state["x"] = new_x
                robot_state["y"] = new_y
                robot_state["moving"] = True

                # Calculate orientation
                if abs(dx) > 0.1 or abs(dy) > 0.1:
                    robot_state["orientation"] = int(math.degrees(math.atan2(dy, dx)))

                # Add to movement history
                movement_history.append((new_x, new_y))
                if len(movement_history) > max_history:
                    movement_history.pop(0)

        time.sleep(0.1)  # Control movement speed

    # Navigation complete
    robot_state["moving"] = False
    navigation_state["is_navigating"] = False

@app.route('/')
def index():
    """Serve the main UI page."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Robot Simulator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .container { display: flex; gap: 20px; }
            .map-container { border: 2px solid #333; position: relative; background: #b8b8b8; }
            .info-panel { min-width: 300px; }
            .robot {
                position: absolute;
                width: 12px;
                height: 12px;
                background: #cc3333;
                border: 1px solid #aa2222;
                transform: translate(-50%, -50%);
                z-index: 10;
                cursor: pointer;
            }
            .robot::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 4px;
                height: 4px;
                background: #ffffff;
                border-radius: 50%;
                transform: translate(-50%, -50%);
            }
            .obstacle {
                position: absolute;
                background: #66cc66;
                border: 1px solid #55bb55;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .goal { position: absolute; width: 30px; height: 30px; background: #0066cc; border-radius: 50%; transform: translate(-50%, -50%); }
            .start-point { position: absolute; width: 25px; height: 25px; background: #00cc00; border: 2px solid #009900; border-radius: 50%; transform: translate(-50%, -50%); z-index: 5; }
            .end-point { position: absolute; width: 25px; height: 25px; background: #ff6600; border: 2px solid #cc4400; border-radius: 50%; transform: translate(-50%, -50%); z-index: 5; }
            .trail { position: absolute; width: 2px; height: 2px; background: rgba(204, 51, 51, 0.4); transform: translate(-50%, -50%); }
            .path-point { position: absolute; width: 4px; height: 4px; background: rgba(0, 102, 204, 0.6); border-radius: 50%; transform: translate(-50%, -50%); z-index: 3; }
            .status { background: #ffffff; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Robot Navigation Simulator</h1>
        <div class="container">
            <div class="map-container" style="width: 800px; height: 600px; cursor: crosshair;" onclick="handleMapClick(event)">
                <div id="robot" class="robot"></div>
                <div id="goal" class="goal" style="display: none;"></div>
                <div id="start-point" class="start-point" style="display: none;"></div>
                <div id="end-point" class="end-point" style="display: none;"></div>
                <div id="trail-container"></div>
                <div id="path-container"></div>
                <!-- Green rectangular obstacles with better spacing for navigation -->
                <!-- Top row -->
                <div class="obstacle" style="left: 100px; top: 80px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 200px; top: 80px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 300px; top: 80px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 450px; top: 80px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 550px; top: 80px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 650px; top: 80px; width: 50px; height: 60px;"></div>

                <!-- Middle-left section -->
                <div class="obstacle" style="left: 80px; top: 200px; width: 60px; height: 50px;"></div>
                <div class="obstacle" style="left: 80px; top: 300px; width: 60px; height: 50px;"></div>

                <!-- Center obstacles - creating corridors -->
                <div class="obstacle" style="left: 250px; top: 220px; width: 50px; height: 80px;"></div>
                <div class="obstacle" style="left: 350px; top: 180px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 450px; top: 220px; width: 50px; height: 80px;"></div>
                <div class="obstacle" style="left: 550px; top: 180px; width: 50px; height: 60px;"></div>

                <!-- Middle-right section -->
                <div class="obstacle" style="left: 660px; top: 200px; width: 60px; height: 50px;"></div>
                <div class="obstacle" style="left: 660px; top: 300px; width: 60px; height: 50px;"></div>

                <!-- Bottom row -->
                <div class="obstacle" style="left: 100px; top: 460px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 200px; top: 460px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 350px; top: 460px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 450px; top: 460px; width: 50px; height: 60px;"></div>
                <div class="obstacle" style="left: 600px; top: 460px; width: 50px; height: 60px;"></div>

                <!-- Additional strategic obstacles -->
                <div class="obstacle" style="left: 180px; top: 320px; width: 40px; height: 50px;"></div>
                <div class="obstacle" style="left: 520px; top: 320px; width: 40px; height: 50px;"></div>
            </div>
            <div class="info-panel">
                <div class="status">
                    <h3>Robot Status</h3>
                    <p><strong>Position:</strong> <span id="position">Loading...</span></p>
                    <p><strong>Orientation:</strong> <span id="orientation">Loading...</span>°</p>
                    <p><strong>Status:</strong> <span id="status">Idle</span></p>
                </div>
                <div class="status">
                    <h3>Navigation Controls</h3>
                    <p><strong>Mode:</strong> <span id="mode">Click to set start point</span></p>
                    <button onclick="startNavigation()">Start Navigation</button>
                    <button onclick="stopNavigation()">Stop Navigation</button>
                    <button onclick="clearPoints()">Clear Points</button>
                    <button onclick="resetRobot()">Reset Robot</button>
                    <button onclick="clearTrail()">Clear Trail</button>
                </div>
                <div class="status">
                    <h3>Instructions</h3>
                    <p>1. <strong>Click</strong> on the map to set start point (green)</p>
                    <p>2. <strong>Click</strong> again to set end point (orange)</p>
                    <p>3. <strong>Click "Start Navigation"</strong> to begin</p>
                    <p>4. Watch the robot navigate from start to end!</p>
                    <p><em>The robot will avoid green obstacles automatically.</em></p>
                </div>
            </div>
        </div>

        <script>
            let goalVisible = false;
            let navigationMode = 'start'; // 'start', 'end', 'ready'
            let startPoint = null;
            let endPoint = null;
            let isNavigating = false;
            
            function updateRobotPosition() {
                fetch('/position')
                    .then(response => response.json())
                    .then(data => {
                        const robot = document.getElementById('robot');
                        robot.style.left = data.x + 'px';
                        robot.style.top = data.y + 'px';
                        robot.style.transform = `translate(-50%, -50%) rotate(${data.orientation}deg)`;
                        
                        document.getElementById('position').textContent = `(${data.x}, ${data.y})`;
                        document.getElementById('orientation').textContent = data.orientation;
                        document.getElementById('status').textContent = data.moving ? 'Moving' : 'Idle';
                        
                        // Add to trail
                        addTrailPoint(data.x, data.y);
                    })
                    .catch(error => console.error('Error:', error));
            }
            
            function addTrailPoint(x, y) {
                const trailContainer = document.getElementById('trail-container');
                const trailPoint = document.createElement('div');
                trailPoint.className = 'trail';
                trailPoint.style.left = x + 'px';
                trailPoint.style.top = y + 'px';
                trailContainer.appendChild(trailPoint);
                
                // Limit trail length for better visibility
                const trails = trailContainer.children;
                if (trails.length > 100) {
                    trailContainer.removeChild(trails[0]);
                }
            }
            
            function resetRobot() {
                fetch('/reset', { method: 'POST' })
                    .then(() => updateRobotPosition());
            }
            
            function clearTrail() {
                document.getElementById('trail-container').innerHTML = '';
            }

            function handleMapClick(event) {
                if (isNavigating) return; // Don't allow clicks during navigation

                const rect = event.currentTarget.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                if (navigationMode === 'start') {
                    setStartPoint(x, y);
                } else if (navigationMode === 'end') {
                    setEndPoint(x, y);
                }
            }

            function setStartPoint(x, y) {
                startPoint = {x: x, y: y};
                const startElement = document.getElementById('start-point');
                startElement.style.left = x + 'px';
                startElement.style.top = y + 'px';
                startElement.style.display = 'block';

                navigationMode = 'end';
                document.getElementById('mode').textContent = 'Click to set end point';
            }

            function setEndPoint(x, y) {
                endPoint = {x: x, y: y};
                const endElement = document.getElementById('end-point');
                endElement.style.left = x + 'px';
                endElement.style.top = y + 'px';
                endElement.style.display = 'block';

                navigationMode = 'ready';
                document.getElementById('mode').textContent = 'Ready to navigate! Click Start Navigation';
            }

            function clearPoints() {
                startPoint = null;
                endPoint = null;
                navigationMode = 'start';
                document.getElementById('start-point').style.display = 'none';
                document.getElementById('end-point').style.display = 'none';
                document.getElementById('path-container').innerHTML = '';
                document.getElementById('mode').textContent = 'Click to set start point';
                stopNavigation();
            }

            function startNavigation() {
                if (!startPoint || !endPoint) {
                    alert('Please set both start and end points first!');
                    return;
                }

                isNavigating = true;
                document.getElementById('mode').textContent = 'Navigating...';

                // Move robot to start point first
                fetch('/set_position', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({x: startPoint.x, y: startPoint.y})
                }).then(() => {
                    // Start navigation to end point
                    fetch('/start_navigation', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            start: startPoint,
                            end: endPoint
                        })
                    });
                });
            }

            function stopNavigation() {
                isNavigating = false;
                fetch('/stop_navigation', {method: 'POST'});
                if (navigationMode === 'ready' || startPoint && endPoint) {
                    document.getElementById('mode').textContent = 'Ready to navigate! Click Start Navigation';
                } else {
                    document.getElementById('mode').textContent = 'Click to set start point';
                }
            }
            
            function toggleGoal() {
                const goal = document.getElementById('goal');
                goalVisible = !goalVisible;
                goal.style.display = goalVisible ? 'block' : 'none';
                if (goalVisible) {
                    // Set goal to a corner
                    goal.style.left = '100px';
                    goal.style.top = '100px';
                }
            }
            
            // Update robot position every 50ms for faster tracking
            setInterval(updateRobotPosition, 50);
            
            // Initial update
            updateRobotPosition();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/position')
def get_position():
    """Get current robot position and orientation."""
    return jsonify(robot_state)

@app.route('/capture')
def capture_image():
    """Capture a simulated camera image."""
    image_data = generate_camera_image()
    return image_data, 200, {'Content-Type': 'text/plain'}

@app.route('/move_rel', methods=['POST'])
def move_relative():
    """Move robot by relative distances."""
    try:
        data = request.get_json()
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        
        # Update robot position
        new_x = robot_state["x"] + dx
        new_y = robot_state["y"] + dy
        
        # Keep robot within bounds
        new_x = max(20, min(MAP_SIZE[0] - 20, new_x))
        new_y = max(20, min(MAP_SIZE[1] - 20, new_y))
        
        # Check for collisions with obstacles
        collision = False
        robot_size = 8  # Robot radius (reduced for smaller robot)
        for obstacle in obstacles:
            # Check if robot overlaps with rectangular obstacle
            if (new_x - robot_size < obstacle["x"] + obstacle["width"] and
                new_x + robot_size > obstacle["x"] and
                new_y - robot_size < obstacle["y"] + obstacle["height"] and
                new_y + robot_size > obstacle["y"]):
                collision = True
                break
        
        if not collision:
            robot_state["x"] = new_x
            robot_state["y"] = new_y
            robot_state["moving"] = True
            
            # Add to movement history
            movement_history.append((new_x, new_y))
            if len(movement_history) > max_history:
                movement_history.pop(0)
            
            # Calculate orientation based on movement
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                robot_state["orientation"] = int(math.degrees(math.atan2(dy, dx)))
            
            # Stop moving after a short delay
            def stop_moving():
                time.sleep(0.05)  # Reduced delay for faster response
                robot_state["moving"] = False
            
            threading.Thread(target=stop_moving).start()
            
            return jsonify({"success": True, "position": robot_state})
        else:
            return jsonify({"success": False, "error": "Collision detected"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/set_position', methods=['POST'])
def set_position():
    """Set robot to specific position."""
    try:
        data = request.get_json()
        x = data.get('x', 400)
        y = data.get('y', 300)

        # Keep robot within bounds
        x = max(20, min(MAP_SIZE[0] - 20, x))
        y = max(20, min(MAP_SIZE[1] - 20, y))

        robot_state["x"] = x
        robot_state["y"] = y
        robot_state["orientation"] = 0
        robot_state["moving"] = False

        return jsonify({"success": True, "position": robot_state})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/start_navigation', methods=['POST'])
def start_navigation():
    """Start navigation from start to end point."""
    try:
        data = request.get_json()
        start = data.get('start')
        end = data.get('end')

        navigation_state["start_point"] = start
        navigation_state["end_point"] = end
        navigation_state["is_navigating"] = True

        # Calculate simple path (A* algorithm would be better, but this is a simple implementation)
        path = calculate_path(start, end)
        navigation_state["path"] = path

        # Start navigation in a separate thread
        import threading
        threading.Thread(target=navigate_to_target, daemon=True).start()

        return jsonify({"success": True, "path": path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/stop_navigation', methods=['POST'])
def stop_navigation():
    """Stop current navigation."""
    navigation_state["is_navigating"] = False
    navigation_state["path"] = []
    robot_state["moving"] = False
    return jsonify({"success": True})

@app.route('/reset', methods=['POST'])
def reset_robot():
    """Reset robot to center position."""
    robot_state["x"] = 400
    robot_state["y"] = 300
    robot_state["orientation"] = 0
    robot_state["moving"] = False
    movement_history.clear()
    navigation_state["is_navigating"] = False
    navigation_state["path"] = []
    return jsonify({"success": True})

if __name__ == '__main__':
    print("🤖 Robot Simulator Starting...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🎯 Then run: python src/autonomous_robot.py")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
