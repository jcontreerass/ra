import argparse
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import paho.mqtt.client as mqtt

# --- REQUISITOS DE SEGURIDAD ---
# Lista Negra de IPs
BLACKLIST_IPS = ["192.168.1.100", "10.0.0.5"]

# Token Bucket (Máx 10 peticiones, recupera 1 por segundo)
MAX_TOKENS = 10
TOKENS = 10
REFILL_RATE = 1.0 
LAST_CHECK = time.time()

def consume_token():
    global TOKENS, LAST_CHECK
    now = time.time()
    TOKENS += (now - LAST_CHECK) * REFILL_RATE
    if TOKENS > MAX_TOKENS:
        TOKENS = MAX_TOKENS
    LAST_CHECK = now
    
    if TOKENS >= 1:
        TOKENS -= 1
        return True
    return False

class BridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/wadl':
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            wadl = """<?xml version="1.0" encoding="UTF-8"?>
            <application xmlns="http://wadl.dev.java.net/2009/02">
                <resources base="http://localhost:8080/">
                    <resource path="sensors/{sede}/{variable}">
                        <method name="POST">
                            <request><representation mediaType="application/json"/></request>
                            <response><representation mediaType="text/plain"/></response>
                        </method>
                    </resource>
                </resources>
            </application>"""
            self.wfile.write(wadl.encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Service Running. Check /wadl for details.")

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # Comprobar Lista Negra
        client_ip = self.client_address[0]
        if client_ip in BLACKLIST_IPS:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden: IP Blocked")
            return

        # Comprobar Token Bucket
        if not consume_token():
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b"Too Many Requests: Traffic Shaping active")
            return

        content_length = int(self.headers['Content-Length'])
        payload = self.rfile.read(content_length)
        
        # Analizar el path para extraer sede y variable
        path_parts = self.path.strip('/').split('/')
        if len(path_parts) != 3 or path_parts[0] != 'sensors':
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request. Use format: /sensors/<sede>/<variable>")
            return
        
        # Reconstruir topic dinámico para que coincida con telegraf.conf
        topic = f"sensors/{path_parts[1]}/{path_parts[2]}"
        
        try:
            client = mqtt.Client()
            client.connect(self.server.broker_address, 1883)
            client.publish(topic, payload)
            client.disconnect()
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--broker", type=str, default="localhost")
    args = parser.parse_args()

    server = HTTPServer(('0.0.0.0', args.port), BridgeHandler)
    server.broker_address = args.broker
    print(f"Middleware listening on port {args.port}...")
    server.serve_forever()

if __name__ == "__main__":
    run()
