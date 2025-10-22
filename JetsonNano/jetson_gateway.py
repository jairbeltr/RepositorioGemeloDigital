# jetson_gateway.py
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# MQTT
BROKER_LOCAL   = "localhost"       # broker en Jetson
BROKER_PC      = "172.23.0.42"     # broker en PC
TOPIC_SENSOR   = "sensor/#"        # ESP32 -> Jetson
TOPIC_SALIDA   = "datos/paciente"  # Jetson -> PC

# Estado: solo 1er IN hasta OUT por estación
armed = {"STA1": False, "STA2": False, "STA3": False}

def t_ms():
    return datetime.now().isoformat(timespec='milliseconds')

def enviar_pc(loc, status, ts_esp32):
    payload = {
        "loc": loc,
        "status": status,                # "IN" o "OUT"
        "timestamp_esp32": ts_esp32,
        "timestamp_jetson": t_ms()
    }
    try:
        publish.single(TOPIC_SALIDA, json.dumps(payload), hostname=BROKER_PC, qos=1)
    except Exception as e:
        # No tumbar el proceso si el broker del PC rechaza
        print(f"⚠️ No se pudo publicar al PC: {e}")

def on_message(_c, _u, msg):
    try:
        d = json.loads(msg.payload.decode(errors="ignore"))
    except:
        return

    loc = (d.get("loc") or "").strip().upper()           # STA1/STA2/STA3
    status = (d.get("status") or "").strip().upper()     # IN/OUT
    ts = d.get("timestamp_esp32") or d.get("timestamp")
    if not (loc and status and ts):
        return
    if loc not in ("STA1","STA2","STA3") or status not in ("IN","OUT"):
        return

    # Map para impresión con índice visible
    esp_idx = {"STA1": 0, "STA2": 1, "STA3": 2}[loc]

    if status == "IN":
        # Solo el PRIMER IN por estación
        if not armed[loc]:
            armed[loc] = True
            print(f"IN ESP32_{esp_idx} en {loc}: {ts}")
            # Enviar al PC solo los que disparan coil:
            if loc == "STA1":  # ("STA1","IN") -> coil 0
                enviar_pc(loc, "IN", ts)
        return

    # status == "OUT"
    if armed[loc]:
        armed[loc] = False
        print(f"OUT ESP32_{esp_idx} en {loc}: {ts}")
        # Enviar al PC solo OUTs que disparan coil:
        # ("STA1","OUT")->1, ("STA2","OUT")->2, ("STA3","OUT")->3
        enviar_pc(loc, "OUT", ts)
    # Si no estaba armado, OUT suelto se ignora (no imprime, no envía)

# Cliente MQTT (simple)
cliente = mqtt.Client()
cliente.on_message = on_message
cliente.connect(BROKER_LOCAL)
cliente.subscribe(TOPIC_SENSOR)
print("📡 Jetson escuchando mensajes de ESP32...")
cliente.loop_forever()
