from(bucket: "waterdrop")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "value") 
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "sensores")


from(bucket: "waterdrop")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  // Eliminamos el filtro de ["_field"] == "value" si tus variables 
  // (temperatura, co2, etc.) ya vienen como nombres de campos distintos.
  |> group(columns: ["_field"]) 
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "sensores_combinados")


import "strings"

from(bucket: "waterdrop")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "value")
  |> map(fn: (r) => ({
      r with 
      sensor_type: strings.split(v: r.topic, t: "/")[2]
    }))
  |> group(columns: ["sensor_type"])
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "promedio_global")
