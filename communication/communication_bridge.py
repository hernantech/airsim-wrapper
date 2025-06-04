import os
import multiprocessing
import time
import json

class CommunicationBridge:
    """
    Mock LoRa communication bridge using multiprocessing pipes.
    This simulates packet-based communication between drones.
    """
    
    def __init__(self, drone_names, log_messages=True):
        self.drone_names = drone_names
        self.log_messages = log_messages
        self.pipes = {}
        self.processes = {}
        
        # Create bidirectional pipes for each drone
        for name in drone_names:
            parent_conn, child_conn = multiprocessing.Pipe()
            self.pipes[name] = {
                "parent": parent_conn,
                "child": child_conn
            }
    
    def get_drone_pipe(self, drone_name):
        """Get the pipe endpoint for a specific drone."""
        return self.pipes[drone_name]["child"]
    
    def start_bridge(self):
        """Start the communication bridge process."""
        self.bridge_process = multiprocessing.Process(
            target=self._bridge_loop,
            args=(self.pipes, self.log_messages)
        )
        self.bridge_process.start()
    
    @staticmethod
    def _bridge_loop(pipes, log_messages):
        """Main bridge loop that routes messages between drones."""
        message_log = []
        
        while True:
            try:
                # Check each drone's pipe for messages
                for sender_name, pipe_set in pipes.items():
                    parent_conn = pipe_set["parent"]
                    
                    if parent_conn.poll(timeout=0.01):
                        # Receive message
                        message = parent_conn.recv()
                        msg_data = json.loads(message)
                        
                        if log_messages:
                            print(f"[COMM] {msg_data['sender']} -> {msg_data['recipient']}: "
                                  f"{msg_data['payload'].get('type', 'unknown')}")
                            message_log.append(msg_data)
                        
                        # Route to recipient
                        recipient = msg_data["recipient"]
                        if recipient in pipes:
                            pipes[recipient]["parent"].send(message)
                        
                        # Simulate LoRa delay (optional)
                        time.sleep(0.01)
                        
            except Exception as e:
                print(f"Bridge error: {e}")
                continue
    
    def stop_bridge(self):
        """Stop the communication bridge."""
        if hasattr(self, 'bridge_process'):
            self.bridge_process.terminate()
            self.bridge_process.join()


class MockLoRaTransceiver:
    """
    Mock LoRa transceiver interface for each drone.
    This would be replaced with actual serial communication on Jetson Nano.
    """
    
    def __init__(self, drone_name, pipe_connection):
        self.drone_name = drone_name
        self.pipe = pipe_connection
        self.rssi = -50  # Mock signal strength
        self.snr = 10    # Mock signal-to-noise ratio
    
    def send(self, message):
        """Send message through the pipe (simulating LoRa transmission)."""
        self.pipe.send(message)
    
    def receive(self, timeout=0.1):
        """Receive message from pipe (simulating LoRa reception)."""
        if self.pipe.poll(timeout=timeout):
            return self.pipe.recv()
        return None
    
    def get_rssi(self):
        """Get mock RSSI value."""
        # Simulate varying signal strength
        import random
        self.rssi = -50 + random.randint(-10, 10)
        return self.rssi
    
    def get_snr(self):
        """Get mock SNR value."""
        import random
        self.snr = 10 + random.randint(-2, 2)
        return self.snr