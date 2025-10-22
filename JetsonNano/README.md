# JetsonNano

Scripts que corren en la Jetson Nano para actuar como **gateway de borde** entre las pasarelas **ESP32** (BLE→MQTT) y el PC con **FlexSim**.  
El script principal es **`jetson_gateway.py`**.

---

## 📜 `jetson_gateway.py` (qué hace)

- **Escucha** en el broker MQTT **local de la Jetson** los tópicos publicados por las ESP32:
  - `sensor/#` → típicamente `sensor/STA1`, `sensor/STA2`, `sensor/STA3`
- **Valida** y **depura** los mensajes JSON recibidos.
- Aplica una **lógica de armado** por estación para registrar solo el **primer `IN`** hasta un `OUT` (evita rebotes).
- **Enriquece** con `timestamp_jetson` (ms) y **republica** al broker del **PC**:
  - `datos/paciente`
- Maneja errores de publicación sin detener el servicio.

**Formato que publica al PC:**
```json
{
  "loc": "STA1",
  "status": "IN|OUT",
  "timestamp_esp32": "YYYY-MM-DD HH:MM:SS.mmm",
  "timestamp_jetson": "YYYY-MM-DDTHH:MM:SS.mmm"
}
