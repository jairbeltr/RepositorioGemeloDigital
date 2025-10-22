# ESP32_gateway

Pasarelas **ESP32** que reciben por **BLE** los mensajes JSON enviados por las estaciones **RAK (STA1–STA3)** y los publican en el broker **MQTT** (Jetson Nano).  
Cada gateway añade un **timestamp con milisegundos (timestamp_esp32)** sincronizado por **NTP**.

---

## 📁 Estructura

| Archivo / Carpeta | Descripción |
|---|---|
| **ESP32_STA1.ino** | Escanea y se conecta a `STA1_BLE`, se suscribe a su característica y publica en el tópico MQTT `sensor/STA1`. |
| **ESP32_STA2.ino** | Igual que el anterior pero para `STA2_BLE` → `sensor/STA2`. |
| **ESP32_STA3.ino** | Igual que el anterior pero para `STA3_BLE` → `sensor/STA3`. |

> Cada sketch usa los mismos UUIDs BLE del servicio/característica expuestos por las STA: **Service 0x1234**, **Characteristic 0x5678**.

---

## 🔌 Dependencias (Arduino IDE)

- **Board:** ESP32 (ESP32 by Espressif Systems)
- **Librerías:**
  - `PubSubClient` (MQTT)
  - `ArduinoJson`
  - `ESP32 BLE Arduino`
  
Instálalas desde **Herramientas → Administrar bibliotecas…**.

---

## ⚙️ Parámetros a configurar

Edita las constantes al inicio de cada sketch:

```cpp
// WiFi
const char* ssid = "TU_RED_WIFI";
const char* password = "TU_PASSWORD";

// Broker MQTT (Jetson Nano)
const char* mqtt_server = "IP_DE_TU_JETSON";
const int   mqtt_port   = 1883;

// NTP (PC/servidor horario). Ej.: PC: 172.23.0.42, o pool.ntp.org
configTime(-5 * 3600, 0, "172.23.0.42"); // GMT-5 ejemplo
