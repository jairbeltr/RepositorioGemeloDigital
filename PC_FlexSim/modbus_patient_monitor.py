# ============================================================
#  modbus_patient_monitor.py
#  ------------------------------------------------------------
#  Descripción:
#     Monitor en tiempo real del flujo de atención de un paciente
#     en Servicios de Urgencias (Registro → Triage → Evaluación).
#     Escucha el estado de tres coils Modbus activados desde FlexSim
#     y muestra notificaciones tipo "toast" en Windows.
#
#  Secuencia monitoreada:
#     1️⃣ Registro          (Coil 4 TRUE)
#     2️⃣ Llegada a Triage  (Coil 5 TRUE)
#     3️⃣ Tiempo Registro → Triage
#     4️⃣ Evaluación Médica (Coil 6 TRUE)
#     5️⃣ Verifica cumplimiento de atención ≤ 2h
# ============================================================

import time
from datetime import datetime, timedelta
from pymodbus.client import ModbusTcpClient
from win10toast import ToastNotifier

try:
    import winsound
except Exception:
    winsound = None

# ------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 502
UNIT_ID = 1

# Coils Modbus asignados a cada etapa
COIL_REG  = 4   # Registro
COIL_TRI  = 5   # Triage
COIL_EVAL = 6   # Evaluación médica

# Parámetros de monitoreo
POLL_SEC  = 0.5
UMBRAL_2H = timedelta(hours=2)

# Estados del autómata de monitoreo
WAIT_REG   = 0
WAIT_TRI   = 1
WAIT_EVAL  = 2
HARD_RESET = 3  # Espera que los tres coils vuelvan a False

# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------
def leer_coil(cli, addr):
    """Lee el estado de un coil Modbus (True/False)."""
    r = cli.read_coils(address=addr, count=1, slave=UNIT_ID)
    if r.isError():
        return None
    return bool(r.bits[0])

def fmt_hms(dt: datetime) -> str:
    return dt.strftime('%H:%M:%S')

def fmt_td(td: timedelta) -> str:
    """Convierte un timedelta en HH:MM:SS."""
    s = int(td.total_seconds())
    hh, rem = divmod(s, 3600)
    mm, ss = divmod(rem, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

def beep(ok=True):
    """Emite un beep según el resultado (solo Windows)."""
    if not winsound:
        return
    try:
        winsound.MessageBeep(
            winsound.MB_ICONASTERISK if ok else winsound.MB_ICONHAND
        )
    except Exception:
        pass

# ------------------------------------------------------------
# BUCLE PRINCIPAL
# ------------------------------------------------------------
def main():
    toaster = ToastNotifier()
    cli = ModbusTcpClient(HOST, port=PORT)

    if not cli.connect():
        toaster.show_toast("Monitor ED", "❌ No hay conexión Modbus", duration=5, threaded=False)
        return

    toaster.show_toast("Monitor ED", "✅ Conectado y escuchando", duration=3, threaded=False)

    estado = WAIT_REG
    reg_ts = None
    tri_ts = None

    prev_reg = prev_tri = prev_eval = False

    try:
        while True:
            s_reg  = leer_coil(cli, COIL_REG)
            s_tri  = leer_coil(cli, COIL_TRI)
            s_eval = leer_coil(cli, COIL_EVAL)

            if s_reg is None or s_tri is None or s_eval is None:
                time.sleep(POLL_SEC)
                continue

            # Detectar flancos (False → True)
            rising_reg  = (not prev_reg)  and s_reg
            rising_tri  = (not prev_tri)  and s_tri
            rising_eval = (not prev_eval) and s_eval

            ahora = datetime.now()

            # 1️⃣ Registro
            if estado == WAIT_REG and rising_reg:
                reg_ts = ahora
                toaster.show_toast("Registro",
                                   f"Hora: {fmt_hms(reg_ts)}",
                                   duration=5, threaded=False)
                beep(True)
                estado = WAIT_TRI

            # 2️⃣ Llegada a Triage + 3️⃣ Tiempo Registro→Triage
            elif estado == WAIT_TRI and rising_tri and reg_ts is not None:
                tri_ts = ahora
                toaster.show_toast("Llegada a Triage",
                                   f"Hora: {fmt_hms(tri_ts)}",
                                   duration=5, threaded=False)
                beep(True)

                delta_rt = tri_ts - reg_ts
                time.sleep(0.3)
                toaster.show_toast("Tiempo Registro→Triage",
                                   f"{fmt_td(delta_rt)}",
                                   duration=6, threaded=False)
                beep(True)
                estado = WAIT_EVAL

            # 4️⃣ Evaluación Médica + 5️⃣ Atención ≤ 2h
            elif estado == WAIT_EVAL and rising_eval and tri_ts is not None:
                eval_ts = ahora
                toaster.show_toast("Evaluación Médica",
                                   f"Hora: {fmt_hms(eval_ts)}",
                                   duration=5, threaded=False)
                beep(True)

                delta_te = eval_ts - tri_ts
                cumple = delta_te <= UMBRAL_2H
                time.sleep(0.3)
                toaster.show_toast("Atención en ≤ 2h",
                                   f"{'✅ Cumplido' if cumple else '⛔ No cumplido'}\n"
                                   f"Tiempo Total: {fmt_td(delta_te)}",
                                   duration=8, threaded=False)
                beep(cumple)

                # Reset hasta que los tres coils vuelvan a False
                reg_ts = tri_ts = None
                estado = HARD_RESET

            # Esperar reinicio (todos los coils deben volver a False)
            elif estado == HARD_RESET and not s_reg and not s_tri and not s_eval:
                estado = WAIT_REG

            # Actualizar estados previos
            prev_reg, prev_tri, prev_eval = s_reg, s_tri, s_eval
            time.sleep(POLL_SEC)

    except KeyboardInterrupt:
        toaster.show_toast("Monitor ED", "🔌 Monitoreo detenido", duration=3, threaded=False)
    finally:
        try:
            cli.close()
        except:
            pass

# ------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
