# RAK_code

Este directorio contiene los programas fuente de las **estaciones UWB RAK4631 + RAK13801** y del **dispositivo portátil BAND**, componentes fundamentales del sistema físico del **Gemelo Digital**.  
Cada módulo opera sobre la plataforma **WisBlock** de RAKwireless, combinando comunicación **Ultra-Wideband (UWB)** para detección de presencia y **Bluetooth Low Energy (BLE)** para transmisión de datos hacia las pasarelas **ESP32**.

---

## 📁 Estructura de carpetas

| Carpeta | Descripción |
|----------|-------------|
| **BAND_1.1/** | Código de la unidad portátil que lleva el paciente. Transmite señales UWB periódicas que permiten a las estaciones fijas detectar su presencia. |
| **Stage_1.2/** | Código de la Estación 1 (STA1). Recibe señales UWB de la BAND, calcula la potencia recibida (RSSI) y envía por BLE un mensaje JSON con el estado `IN/OUT`. |
| **Stage_2.2/** | Código de la Estación 2 (STA2). Misma lógica que STA1, con dirección y nombre BLE propios. |
| **Stage_3.2/** | Código de la Estación 3 (STA3). Última etapa del recorrido del paciente, con su propia dirección y nombre BLE. |

---

## ⚙️ Funcionamiento general

Cada **estación RAK (STA1–STA3)** cumple las siguientes funciones:

1. **Recepción UWB:** Detecta las señales transmitidas por el módulo **BAND**.  
2. **Cálculo de RSSI:** Evalúa la potencia de la señal recibida.  
3. **Clasificación:** Determina el estado del paciente:  
   - `IN` → cuando el RSSI supera el umbral de cercanía.  
   - `OUT` → cuando el RSSI está por debajo del umbral.  
4. **Transmisión BLE:** Envía un mensaje JSON mediante BLE, por ejemplo:  
   ```json
   {"loc":"STA1","status":"IN","rssi":-64.8}

