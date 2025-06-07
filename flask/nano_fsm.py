import time
import requests
from enum import Enum, auto

FLASK_SERVER = 'http://<flask-server-ip>:8000'  # Replace with your HP server's address
DRONE_NAME = 'Drone1'  # Change as needed
IMAGE_TYPE = 'rgb'
REQUEST_HZ = 5  # 5 Hz

class State(Enum):
    INIT = auto()
    REQUEST_IMAGE = auto()
    REQUEST_STATUS = auto()
    PROCESS = auto()
    IDLE = auto()

class NanoFSM:
    def __init__(self):
        self.state = State.INIT
        self.last_image = None
        self.last_status = None
        self.cycle_time = 1.0 / REQUEST_HZ

    def run(self):
        while True:
            start = time.time()
            if self.state == State.INIT:
                print('[FSM] Initializing...')
                self.state = State.REQUEST_IMAGE

            elif self.state == State.REQUEST_IMAGE:
                print('[FSM] Requesting image...')
                try:
                    resp = requests.get(f"{FLASK_SERVER}/image", params={"drone": DRONE_NAME, "type": IMAGE_TYPE}, timeout=2)
                    if resp.status_code == 200:
                        self.last_image = resp.content
                        print(f"[FSM] Received image ({len(self.last_image)} bytes)")
                    else:
                        print(f"[FSM] Image error: {resp.status_code}")
                except Exception as e:
                    print(f"[FSM] Image request failed: {e}")
                self.state = State.REQUEST_STATUS

            elif self.state == State.REQUEST_STATUS:
                print('[FSM] Requesting status...')
                try:
                    resp = requests.get(f"{FLASK_SERVER}/status", params={"drone": DRONE_NAME}, timeout=2)
                    if resp.status_code == 200:
                        self.last_status = resp.json()
                        print(f"[FSM] Received status: {self.last_status}")
                    else:
                        print(f"[FSM] Status error: {resp.status_code}")
                except Exception as e:
                    print(f"[FSM] Status request failed: {e}")
                self.state = State.PROCESS

            elif self.state == State.PROCESS:
                # Here you could add logic to process the image/status, make decisions, etc.
                print('[FSM] Processing data...')
                # For now, just print and go idle
                self.state = State.IDLE

            elif self.state == State.IDLE:
                # Wait for the next cycle
                elapsed = time.time() - start
                sleep_time = max(0, self.cycle_time - elapsed)
                time.sleep(sleep_time)
                self.state = State.REQUEST_IMAGE

if __name__ == '__main__':
    fsm = NanoFSM()
    fsm.run() 