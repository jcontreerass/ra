from fastapi import FastAPI, HTTPException
from influxdb_client import InfluxDBClient

# Inicializamos la aplicación FastAPI
app = FastAPI(title="Servicio de Datos de Sensores (SOA)")

# --- CONFIGURACIÓN DE INFLUXDB ---
INFLUX_URL = "http://127.0.0.1:8086"
INFLUX_TOKEN = "jg8jrARJ8gTVn6UrpSHDS5XL0us8NBmWqaoz6nN1fvXBqRBDICFxQNXZKvhEdAF18uW19J79OmVJGSo3V6AQUA=="
INFLUX_ORG = "etsisi"
INFLUX_BUCKET = "waterdrop"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

@app.get("/api/sensores/actual")
def obtener_datos_actuales():

    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "mqtt_consumer")
      |> last()
    '''
    
    try:
        tablas = query_api.query(query, org=INFLUX_ORG)
        
        resultados = {}
        for tabla in tablas:
            for registro in tabla.records:
                campo = registro.get_field()   
                valor = registro.get_value()   
                resultados[campo] = valor
                
        if not resultados:
            return {"status": "ok", "mensaje": "No se encontraron datos en la última hora."}
            
        return {"status": "ok", "datos": resultados}
        
    except Exception as e:
        # Si falla, error
        raise HTTPException(status_code=500, detail=f"Error consultando la base de datos: {str(e)}")
