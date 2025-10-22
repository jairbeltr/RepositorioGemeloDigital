#include <SPI.h>
#include <DW1000Ng.hpp>
#include <DW1000NgUtils.hpp>
#include <DW1000NgRanging.hpp>
#include <bluefruit.h>

// Pines UWB
const uint8_t PIN_SS = SS; // Pin SPI Select
const uint8_t PIN_RST = WB_IO6;
const uint8_t PIN_IRQ = WB_IO5;

// Configuración por defecto UWB
device_configuration_t DEFAULT_CONFIG = {
    false, true, true, true, false,
    SFDMode::STANDARD_SFD,
    Channel::CHANNEL_5,
    DataRate::RATE_850KBPS,
    PulseFrequency::FREQ_16MHZ,
    PreambleLength::LEN_256,
    PreambleCode::CODE_3
};

// BLE
BLEService customService = BLEService(0x1234); // UUID del servicio BLE
BLECharacteristic customCharacteristic = BLECharacteristic(0x5678); // UUID de la característica BLE

// Variables
float RSSI_THRESHOLD_CLOSE = -65.0; // Umbral RSSI cercano
float RSSI_THRESHOLD_FAR = -80.0;   // Umbral RSSI lejano

void setup() {
  // Inicializar Serial solo si está disponible
  Serial.begin(115200);
  delay(100); // Pequeño retraso para evitar errores de arranque
  Serial.println("Inicializando STA1...");

  // Inicializar UWB
  DW1000Ng::initialize(PIN_SS, PIN_IRQ, PIN_RST);
  DW1000Ng::applyConfiguration(DEFAULT_CONFIG);
  DW1000Ng::setDeviceAddress(1); // Dirección única para STA1
  DW1000Ng::setNetworkId(10);
  DW1000Ng::setAntennaDelay(16436);

  // Inicializar BLE
  Bluefruit.begin();
  Bluefruit.setTxPower(4); // Potencia de transmisión BLE
  Bluefruit.setName("STA1_BLE");
  customService.begin();
  customCharacteristic.setProperties(CHR_PROPS_READ | CHR_PROPS_NOTIFY);
  customCharacteristic.setFixedLen(128); // Tamaño máximo del mensaje JSON
  customCharacteristic.begin();
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addName();
  Bluefruit.Advertising.addService(customService);
  Bluefruit.Advertising.start();
  Serial.println("BLE configurado.");
}

void loop() {
  // Inicia la recepción UWB
  DW1000Ng::startReceive();
  while (!DW1000Ng::isReceiveDone()) {
    delay(10);
  }
  DW1000Ng::clearReceiveStatus();

  // Leer el RSSI
  float rssi = DW1000Ng::getReceivePower();
  const char* status = (rssi > RSSI_THRESHOLD_CLOSE) ? "IN" : "OUT";

  // Crear mensaje JSON sin marca de tiempo
  char jsonMessage[128];
  snprintf(jsonMessage, sizeof(jsonMessage),
           "{\"loc\":\"STA1\",\"status\":\"%s\",\"rssi\":%.1f}",
           status, rssi);

  // Transmitir mensaje BLE
  customCharacteristic.notify((uint8_t*)jsonMessage, strlen(jsonMessage));

  // Mostrar datos en el monitor serial (solo si está conectado)
  if (Serial) {
    Serial.println(jsonMessage);
  }

  delay(1000); // Intervalo entre transmisiones
}

