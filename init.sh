#!/bin/bash

# --- CONFIGURACIÓN ---
SERVER1_PATH="./server1/app.js"
SERVER2_PATH="./server2/app.js"
HAPROXY_CONFIG="./haproxy.cfg"
PID_FILE="./haproxy.pid"

# --- FUNCIÓN DE LIMPIEZA ---
function cleanup {
    echo -e "\n[!] Deteniendo servicios..."
    
    # Matar Node servers usando sus PIDs guardados
    if [ ! -z "$PID_NODE1" ]; then kill $PID_NODE1 2>/dev/null; fi
    if [ ! -z "$PID_NODE2" ]; then kill $PID_NODE2 2>/dev/null; fi
    
    # Matar HAProxy usando el PID del archivo
    if [ -f "$PID_FILE" ]; then
        H_PID=$(cat $PID_FILE)
        kill $H_PID 2>/dev/null
        rm $PID_FILE
    fi

    echo "[✓] Todo limpio. Saliendo."
    exit 0
}

# Registrar el trap para capturar Ctrl+C (SIGINT)
trap cleanup SIGINT

# --- INICIO DE SERVICIOS ---

# 1. Limpiar puertos por si acaso antes de empezar
echo "[*] Liberando puertos..."
fuser -k 3000/tcp 3001/tcp 2>/dev/null

# 2. Levantar servidores Node
echo "[*] Iniciando servidores Node..."
node $SERVER1_PATH &
PID_NODE1=$!

node $SERVER2_PATH &
PID_NODE2=$!

# 3. Levantar HAProxy (usando -p para guardar el PID localmente)
echo "[*] Iniciando HAProxy..."
haproxy -f $HAPROXY_CONFIG -D -p $PID_FILE

echo "------------------------------------------------"
echo " Servidores y Proxy ejecutándose..."
echo " Node 1 (PID: $PID_NODE1) en puerto 3000"
echo " Node 2 (PID: $PID_NODE2) en puerto 3001"
echo " HAProxy (PID: $(cat $PID_FILE)) listo."
echo " Presiona Ctrl + C para detenerlo todo."
echo "------------------------------------------------"



# --- FUNCIÓN DE LIMPIEZA (Ctrl+C) ---
function cleanup {
    echo -e "\n[!] Deteniendo servicios (requiere permisos)..."
    sudo systemctl stop mosquitto telegraf
    echo "[✓] Mosquitto y Telegraf detenidos correctamente."
    exit 0
}

# Registrar el trap para capturar Ctrl+C (SIGINT)
trap cleanup SIGINT

# --- INICIO DE SERVICIOS ---
echo "[*] Iniciando Mosquitto y Telegraf (requiere permisos)..."
sudo systemctl start mosquitto telegraf

# Comprobar si se iniciaron correctamente
if systemctl is-active --quiet mosquitto && systemctl is-active --quiet telegraf; then
    echo "================================================"
    echo " 🚀 PUENTE MQTT ACTIVO 🚀"
    echo "================================================"
    echo " ✓ Mosquitto (Broker MQTT) ejecutándose."
    echo " ✓ Telegraf  (Agente de métricas) ejecutándose."
    echo "================================================"
    echo " Presiona Ctrl + C para detener los servicios."
    echo "================================================"
else
    echo "[X] Hubo un problema al iniciar los servicios. Revisa los logs con: journalctl -xe"
    exit 1
fi

# 4. Mantener el script vivo para que el trap pueda actuar
wait
