#!/bin/bash

# --- CONFIGURACIÓN ---
BROKER="127.0.0.1"
PORT="1883"

# Nombres de los sensores que sustituirán al comodín '+'
SENSORES=("salon" "hab1" "hab2" "hab3" "hab4")

echo "Iniciando simulador MQTT publicando cada 5 segundos..."
echo "Pulsa Ctrl+C para detenerlo."
echo "------------------------------------------------------"

while true; do
    for SENSOR in "${SENSORES[@]}"; do
        
        # Generamos los 4 valores aleatorios de golpe usando awk.
        # Le pasamos la variable $RANDOM de bash como semilla para que varíen siempre.
        VALORES=$(awk -v seed=$RANDOM 'BEGIN{
            srand(seed);
            temp = 20 + rand() * 8;      # Temperatura entre 20.0 y 28.0 °C
            hum = 40 + rand() * 25;      # Humedad entre 40.0 y 65.0 %
            co2 = 400 + rand() * 400;    # CO2 entre 400 y 800 ppm (entero)
            voc = 50 + rand() * 150;     # VOC entre 50 y 200 ppb (entero)
            
            # Formateamos los decimales
            printf "%.1f %.1f %d %d", temp, hum, co2, voc;
        }')
        
        # Extraemos los valores a variables de bash
        read TEMP HUM CO2 VOC <<< "$VALORES"

        # --- PUBLICACIÓN CON MOSQUITTO_PUB ---
        mosquitto_pub -h "$BROKER" -p "$PORT" -t "sensors/$SENSOR/temperature" -m "$TEMP"
        mosquitto_pub -h "$BROKER" -p "$PORT" -t "sensors/$SENSOR/humidity" -m "$HUM"
        mosquitto_pub -h "$BROKER" -p "$PORT" -t "sensors/$SENSOR/co2" -m "$CO2"
        mosquitto_pub -h "$BROKER" -p "$PORT" -t "sensors/$SENSOR/voc" -m "$VOC"

        # Mostramos por pantalla lo que acabamos de enviar
        echo "[$(date +'%H:%M:%S')] Publicado en $SENSOR -> T: $TEMP | H: $HUM | CO2: $CO2 | VOC: $VOC"
        
    done
    
    # Pausa de 5 segundos antes de la siguiente ráfaga
    sleep 5
done
