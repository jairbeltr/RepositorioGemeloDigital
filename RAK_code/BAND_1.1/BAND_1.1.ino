#include <SPI.h>
#include <DW1000Ng.hpp>

// Pines de comunicación
const uint8_t PIN_SS = SS;        // SPI Select
const uint8_t PIN_RST = WB_IO6;   // Reset Pin
const uint8_t PIN_IRQ = WB_IO5;   // Interrupt Pin

// Configuración básica del dispositivo
device_configuration_t DEFAULT_CONFIG = {
    false,
    true,
    true,
    true,
    false,
    SFDMode::STANDARD_SFD,
    Channel::CHANNEL_5,
    DataRate::RATE_850KBPS,
    PulseFrequency::FREQ_16MHZ,
    PreambleLength::LEN_256,
    PreambleCode::CODE_3
};

void setup() {
  // Inicializar Serial (solo si está disponible)
  Serial.begin(115200);
  delay(100); // Pequeño delay para estabilidad
  Serial.println("🔹 Inicializando BAND...");

  // Inicializar el módulo DW1000
  DW1000Ng::initialize(PIN_SS, PIN_RST, PIN_IRQ);
  Serial.println("✅ DW1000Ng inicializado correctamente.");

  // Aplicar configuración
  DW1000Ng::applyConfiguration(DEFAULT_CONFIG);
  DW1000Ng::setDeviceAddress(1);    // Dirección del dispositivo
  DW1000Ng::setNetworkId(10);       // ID de la red
  DW1000Ng::setAntennaDelay(16436); // Calibrar la antena
  Serial.println("✅ Configuración aplicada.");
}

void loop() {
  // Crear mensaje simple
  const char mensaje[] = "BAND activo";
  
  // Configurar y enviar mensaje
  DW1000Ng::setTransmitData((byte*)mensaje, sizeof(mensaje));
  DW1000Ng::startTransmit(TransmitMode::IMMEDIATE);

  // Esperar confirmación de transmisión sin bloquear el loop
  unsigned long transmitStart = millis();
  while (!DW1000Ng::isTransmitDone()) {
    delay(1);
    // Si tarda más de 2 segundos en transmitir, salir del loop para evitar bloqueos
    if (millis() - transmitStart > 2000) {
      Serial.println("⚠️ Error en transmisión, reintentando...");
      DW1000Ng::clearTransmitStatus();
      return;
    }
  }
  
  // Limpiar el estado de transmisión
  DW1000Ng::clearTransmitStatus();
  
  // Mostrar en el monitor serial (solo si está conectado)
  Serial.println(mensaje);

  delay(1000); // Intervalo de 1 segundo entre transmisiones
}
