# pc_coil_mapper.py
import time
import json
from datetime import datetime
from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt

# =========================================
# CONFIGURACIÓN DE MQTT Y MODBUS
# =========================================
MQTT_BROKER   = "localhost"          # si Mosquitto corre en este PC
TOPIC         = "datos/paciente"
MODBUS_HOST   = "127.0.0.1"
MODBUS_PORT   = 502
SLAVE_ID      = 1
PULSE_SECONDS = 0.2

# Guardas: sólo 1er OUT tras IN por estación
waiting = {"STA1": False, "STA2": False, "STA3": False}

# =========================================
# Función para timestamp con milisegundos
# =========================================
def t_ms():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# =========================================
# Activa un coil con pulso
# =========================================
def activar_coil(coil):
    mb = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    if mb.connect():
        mb.write_coil(coil, True, slave=SLAVE_ID)
        time.sleep(PULSE_SECONDS)
        mb.write_coil(coil, False, slave=SLAVE_ID)
        mb.close()

# =========================================
# Callback MQTT
# =========================================
def on_message(_c, _u, msg):
    try:
        d = json.loads(msg.payload.decode())
    except:
        return

    loc       = (d.get("loc") or "").strip().upper()
    status    = (d.get("status") or "").strip().upper()
    ts_esp32  = d.get("timestamp_esp32") or d.get("timestamp")
    ts_jetson = d.get("timestamp_jetson")

    if not (loc and status and ts_esp32 and ts_jetson):
        return
    if loc not in ("STA1", "STA2", "STA3") or status not in ("IN", "OUT"):
        return

    # Normalizamos formato Jetson y ESP32
    try:
        ts_esp32 = datetime.strptime(ts_esp32, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    except:
        pass
    try:
        ts_jetson = datetime.strptime(ts_jetson.replace("T", " "), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    except:
        pass

    # Habilitar ventanas por IN
    if status == "IN":
        waiting[loc] = True
        if loc == "STA1":
            coil = 0
        else:
            return
    else:  # OUT
        if not waiting[loc]:
            return
        waiting[loc] = False
        coil = {"STA1": 1, "STA2": 2, "STA3": 3}[loc]

    ts_pc_rx = t_ms()
    activar_coil(coil)
    ts_pc_resp = t_ms()

    # Impresión uniforme
    esp_idx = {"STA1": 0, "STA2": 1, "STA3": 2}[loc]
    texto = f"{status} ESP32_{esp_idx} en {loc}"
    print(f"""{texto}
timestamp_esp32: {ts_esp32}
timestamp_jetson: {ts_jetson}
timestamp_pc: {ts_pc_rx}
timestamp_flexsim: {ts_pc_resp}
""")

# =========================================
# MQTT listener principal
# =========================================
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER)
mqtt_client.subscribe(TOPIC)
print("🟢 PC esperando mensaje de Jetson...")
mqtt_client.loop_forever()
