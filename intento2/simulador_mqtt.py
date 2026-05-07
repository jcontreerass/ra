import time
import random
import paho.mqtt.client as mqtt

# --- CONFIGURACIÓN ---
BROKER = "127.0.0.1"
PORT = 1883
SENSORES = ["salon", "habitacion1"]

def main():
    # Inicializamos el cliente MQTT
    # (Usamos protocol=mqtt.MQTTv311 para máxima compatibilidad)
    client = mqtt.Client(client_id="simulador_python", protocol=mqtt.MQTTv311)
    
    try:
        print(f"Conectando al broker en {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f"❌ Error al conectar con el broker: {e}")
        return

    # Iniciamos el bucle de red en segundo plano para manejar la conexión
    client.loop_start()
    
    print("✅ Conectado. Iniciando simulador MQTT...")
    print("Pulsa Ctrl+C para detenerlo.")
    print("-" * 55)

    try:
        while True:
            for sensor in SENSORES:
                # Generamos valores aleatorios realistas
                temp = round(random.uniform(20.0, 28.0), 1)  # Temperatura entre 20.0 y 28.0
                hum = round(random.uniform(40.0, 65.0), 1)   # Humedad entre 40.0 y 65.0
                co2 = int(random.uniform(400, 800))          # CO2 entre 400 y 800
                voc = int(random.uniform(50, 200))           # VOC entre 50 y 200

                # Publicamos los mensajes en sus respectivos topics
                # retain=False significa que el broker no guardará el último mensaje
                client.publish(f"sensors/{sensor}/temperature", str(temp), retain=False)
                client.publish(f"sensors/{sensor}/humidity", str(hum), retain=False)
                client.publish(f"sensors/{sensor}/co2", str(co2), retain=False)
                client.publish(f"sensors/{sensor}/voc", str(voc), retain=False)

                # Imprimimos por consola lo que estamos enviando
                hora_actual = time.strftime('%H:%M:%S')
                print(f"[{hora_actual}] Publicado en {sensor} -> T: {temp} | H: {hum} | CO2: {co2} | VOC: {voc}")
            
            # Esperamos 5 segundos antes de la siguiente ráfaga
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido por el usuario.")
    finally:
        # Cerramos la conexión de forma limpia al salir
        client.loop_stop()
        client.disconnect()
        print("Desconectado del broker MQTT.")

if __name__ == "__main__":
    main()
