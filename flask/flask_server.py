import os
from flask import Flask, request, jsonify, send_file, Response
import requests
from io import BytesIO

app = Flask(__name__)

# === CONFIGURATION ===
# Map drone names to their controller REST API base URLs (using Tailscale hostnames)
DRONE_CONTROLLERS = {
    'Drone1': 'http://drone1-hostname:5001',  # Replace with actual Tailscale hostname/port
    'Drone2': 'http://drone2-hostname:5002',  # Replace with actual Tailscale hostname/port
    # Add more drones as needed
}

# === ENDPOINTS ===

@app.route('/command', methods=['POST'])
def command():
    """
    Forward a command to the specified drone controller.
    Expects JSON: {"drone": "Drone1", ...command_payload...}
    """
    data = request.get_json()
    drone = data.get('drone')
    if not drone or drone not in DRONE_CONTROLLERS:
        return jsonify({'error': 'Invalid or missing drone name'}), 400
    try:
        controller_url = f"{DRONE_CONTROLLERS[drone]}/command"
        resp = requests.post(controller_url, json=data, timeout=2)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({'error': f'Controller unreachable: {e}'}), 502

@app.route('/image', methods=['GET'])
def image():
    """
    Fetch the latest image from the specified drone controller.
    Query params: drone=Drone1&type=rgb (type is optional)
    """
    drone = request.args.get('drone')
    img_type = request.args.get('type', 'rgb')
    if not drone or drone not in DRONE_CONTROLLERS:
        return jsonify({'error': 'Invalid or missing drone name'}), 400
    try:
        controller_url = f"{DRONE_CONTROLLERS[drone]}/image?type={img_type}"
        resp = requests.get(controller_url, timeout=2)
        if resp.status_code == 200:
            # Stream the image file back
            return Response(resp.content, mimetype=resp.headers.get('Content-Type', 'image/png'))
        else:
            return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({'error': f'Controller unreachable: {e}'}), 502

@app.route('/status', methods=['GET'])
def status():
    """
    Fetch status/telemetry from the specified drone controller.
    Query params: drone=Drone1
    """
    drone = request.args.get('drone')
    if not drone or drone not in DRONE_CONTROLLERS:
        return jsonify({'error': 'Invalid or missing drone name'}), 400
    try:
        controller_url = f"{DRONE_CONTROLLERS[drone]}/status"
        resp = requests.get(controller_url, timeout=2)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({'error': f'Controller unreachable: {e}'}), 502

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, threaded=True) 