import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import paho.mqtt.client as mqtt

class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        payload = self.rfile.read(content_length)
        
        try:
            client = mqtt.Client()
            client.connect(self.server.broker_address, 1883)
            client.publish("sensors/data", payload)
            client.disconnect()
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            self.send_response(500)
            self.end_headers()

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--broker", type=str, default="localhost")
    args = parser.parse_args()

    server = HTTPServer(('0.0.0.0', args.port), BridgeHandler)
    server.broker_address = args.broker
    server.serve_forever()

if __name__ == "__main__":
    run()
