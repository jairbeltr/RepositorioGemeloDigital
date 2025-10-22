# PC_FlexSim

Scripts que habilitan la **comunicación bidireccional** entre el Gemelo Digital en **FlexSim Healthcare** y el sistema físico.

- **Entrada PC ← Jetson (MQTT):** recibe eventos desde la Jetson (`datos/paciente`) y **activa coils Modbus** hacia FlexSim según reglas de negocio.
- **Salida PC → Operador (UI):** monitoriza en tiempo real **coils de FlexSim** y muestra notificaciones (registro→triage→evaluación) con verificación de la meta ≤ 2 h.

---

## 📁 Archivos

| Script | Rol |
|---|---|
| **pc_coil_mapper.py** | Listener MQTT → **mapea** eventos (`IN/OUT` de STA1–STA3) a **coils Modbus** de FlexSim, con pulso `True`/`False`. |
| **modbus_patient_monitor.py** | **Lee** tres coils Modbus (Registro, Triage, Evaluación) y muestra **notificaciones** en Windows; calcula tiempos y la meta ≤ 2 h. |

---

## 🔧 Dependencias (PC)

- Python 3.8+
- Paquetes:
  ```bash
  pip install paho-mqtt pymodbus win10toast

