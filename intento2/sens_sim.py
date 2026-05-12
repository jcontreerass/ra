import requests
import json
import time
import random

# Configuration
HAPROXY_URL = "http://localhost:8080" 
SEDES = ["sede1", "sede2", "sede3"]
VARIABLES = ["temperature", "humidity", "co2", "voc"]

def generate_sensor_data(variable):
    if variable == "temperature":
        return round(random.uniform(18.0, 35.0), 2)
    elif variable == "humidity":
        return round(random.uniform(30.0, 60.0), 2)
    elif variable == "co2":
        return random.randint(400, 1200)
    elif variable == "voc":
        return random.randint(0, 500)
    return 0

def send_data():
    while True:
        for sede in SEDES:
            for var in VARIABLES:
                # Construct URL based on middleware path logic
                url = f"{MIDDLEWARE_URL}/sensors/{sede}/{var}"
                
                payload = {
                    "value": generate_sensor_data(var),
                    "timestamp": time.time(),
                    "unit": "metric"
                }

                try:
                    response = requests.post(
                        url, 
                        data=json.dumps(payload),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        print(f"[OK] {sede} - {var}: {payload['value']}")
                    elif response.status_code == 429:
                        print(f"[LIMIT] Traffic shaping active (429)")
                    elif response.status_code == 403:
                        print(f"[BLOCKED] IP Blacklisted (403)")
                    else:
                        print(f"[ERROR] Status {response.status_code}: {response.text}")

                except Exception as e:
                    print(f"[CONNECTION ERROR] {e}")

                # Sleep slightly to avoid exhausting the token bucket immediately
                # The middleware refills 1 token/sec
                time.sleep(0.5) 

        # Simulate sleep period of the sensor cycle
        print("Sensors entering sleep mode...")
        time.sleep(5)

if __name__ == "__main__":
    send_data()
