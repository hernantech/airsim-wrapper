# Flask Proxy Server for Drone Controller Integration

## Overview

This Flask server acts as a proxy between Jetson Nano clients and already-running drone controllers (which expose their own REST APIs) on your HP server. It is designed to:

- Receive requests from Jetson Nanos (or other clients)
- Forward those requests to the appropriate drone controller using its Tailscale hostname and REST API
- Return the controller's response (images, telemetry, etc.) to the client

This setup allows you to centralize access to multiple drones/controllers behind a single, easy-to-use API.

---

## Configuration

At the top of `flask_server.py`, configure the mapping of drone names to their controller REST API base URLs (using Tailscale hostnames):

```python
DRONE_CONTROLLERS = {
    'Drone1': 'http://drone1-hostname:5001',  # Replace with actual Tailscale hostname/port
    'Drone2': 'http://drone2-hostname:5002',  # Replace with actual Tailscale hostname/port
    # Add more drones as needed
}
```

- **Drone names** (e.g., 'Drone1', 'Drone2') are used in API requests.
- **Hostnames/ports** should match the Tailscale addresses and REST API ports of your running controllers.

---

## Endpoints

### 1. `/command` (POST)
- **Purpose:** Forward a command or telemetry request to a specific drone controller.
- **Request:**
  - Method: `POST`
  - Content-Type: `application/json`
  - Body: `{ "drone": "Drone1", ...other_command_fields... }`
- **Response:**
  - Forwards the controller's response (JSON or other data)
  - Returns 400 if the drone name is missing/invalid
  - Returns 502 if the controller is unreachable

**Example:**
```bash
curl -X POST http://<flask-server>:8000/command \
     -H 'Content-Type: application/json' \
     -d '{"drone": "Drone1", "action": "takeoff"}'
```

---

### 2. `/image` (GET)
- **Purpose:** Fetch the latest image from a drone controller.
- **Request:**
  - Method: `GET`
  - Query params:
    - `drone` (required): e.g., `Drone1`
    - `type` (optional): e.g., `rgb` (default), `ir`, etc.
- **Response:**
  - Streams the image file (PNG/JPEG)
  - Returns 400 if the drone name is missing/invalid
  - Returns 502 if the controller is unreachable

**Example:**
```bash
curl "http://<flask-server>:8000/image?drone=Drone1&type=rgb" --output latest.png
```

---

### 3. `/status` (GET)
- **Purpose:** Fetch status/telemetry from a drone controller.
- **Request:**
  - Method: `GET`
  - Query params:
    - `drone` (required): e.g., `Drone1`
- **Response:**
  - Forwards the controller's JSON response
  - Returns 400 if the drone name is missing/invalid
  - Returns 502 if the controller is unreachable

**Example:**
```bash
curl "http://<flask-server>:8000/status?drone=Drone1"
```

---

## Running the Server

1. Install dependencies:
   ```bash
   pip install flask requests
   ```
2. Edit `flask_server.py` to set the correct Tailscale hostnames/ports for your controllers.
3. Start the server:
   ```bash
   python flask_server.py
   ```
   By default, it listens on port 8000 on all interfaces (`0.0.0.0`).

---

## Notes
- The Flask server does **not** launch or manage the drone controllers; it only proxies requests.
- Each controller must expose compatible REST endpoints (`/command`, `/image`, `/status`).
- Error handling is included for unreachable controllers or invalid requests.
- You can add more drones by extending the `DRONE_CONTROLLERS` dictionary.

---

## Example Use Case

A Jetson Nano can send requests to this Flask server to:
- Command a drone to move or perform an action
- Retrieve the latest camera image for ML inference
- Get telemetry/status updates

This architecture allows you to keep the drone control logic and hardware-specific code on your HP server, while the Jetson Nanos interact with a simple, unified API. 