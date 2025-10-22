#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <time.h>
#include <sys/time.h>  // Para obtener milisegundos

// 🛜 Configuración WiFi
const char* ssid = "RED_B201";
const char* password = "InformaticaSabana";

// 🛰️ Configuración del broker MQTT (Jetson Nano)
const char* mqtt_server = "172.23.0.41";
const int mqtt_port = 1883;

// 📡 Cliente WiFi y MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// 🔍 Variables BLE
BLEScan* pBLEScan;
BLEClient* pClient;
bool connected = false;
std::string serviceUUID = "1234";
std::string characteristicUUID = "5678";

// 🛠 Buffer JSON BLE
String jsonBuffer = "";

// 🌐 Conexión WiFi
void connectToWiFi() {
  Serial.print("🔌 Conectando a WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi conectado. IP: " + WiFi.localIP().toString());
}

// 📡 Conexión MQTT
void connectToMQTT() {
  while (!client.connected()) {
    Serial.print("🔄 Conectando a MQTT...");
    if (client.connect("ESP32_STA3")) {
      Serial.println("✅ Conectado a MQTT");
    } else {
      Serial.print("❌ rc=");
      Serial.print(client.state());
      Serial.println(" Reintentando en 5s");
      delay(5000);
    }
  }
}

// 🔔 Notificación BLE con timestamp de milisegundos
void notifyCallback(
  BLERemoteCharacteristic* pRemoteCharacteristic,
  uint8_t* data,
  size_t length,
  bool isNotify
) {
  String receivedData = "";
  for (size_t i = 0; i < length; i++) {
    receivedData += (char)data[i];
  }
  receivedData.trim();
  jsonBuffer += receivedData;

  int startIdx = jsonBuffer.indexOf("{");
  int endIdx = jsonBuffer.lastIndexOf("}");
  if (startIdx != -1 && endIdx != -1 && endIdx > startIdx) {
    String completeJSON = jsonBuffer.substring(startIdx, endIdx + 1);

    StaticJsonDocument<512> jsonDoc;
    DeserializationError error = deserializeJson(jsonDoc, completeJSON);
    if (!error) {
      // 🕒 Agregar timestamp_esp32 con milisegundos
      struct timeval tv;
      gettimeofday(&tv, nullptr);
      struct tm* timeinfo = localtime(&tv.tv_sec);
      char timestamp[30];
      snprintf(timestamp, sizeof(timestamp), "%04d-%02d-%02d %02d:%02d:%02d.%03ld",
               timeinfo->tm_year + 1900,
               timeinfo->tm_mon + 1,
               timeinfo->tm_mday,
               timeinfo->tm_hour,
               timeinfo->tm_min,
               timeinfo->tm_sec,
               tv.tv_usec / 1000);  // milisegundos

      jsonDoc["timestamp_esp32"] = timestamp;

      // Mostrar en Serial
      serializeJsonPretty(jsonDoc, Serial);
      Serial.println();

      // Enviar por MQTT al topic de STA3
      String jsonOut;
      serializeJson(jsonDoc, jsonOut);
      if (client.publish("sensor/STA3", jsonOut.c_str())) {
        Serial.println("📤 Publicado a MQTT");
      } else {
        Serial.println("❌ Fallo al publicar en MQTT");
      }
    } else {
      Serial.println("❌ Error al parsear JSON");
    }

    jsonBuffer = jsonBuffer.substring(endIdx + 1);
  }
}

// 🔍 Conectar a STA3 BLE
void connectToSTA3() {
  Serial.println("🔍 Escaneando STA3...");
  pBLEScan->start(5, false);
  BLEScanResults results = *pBLEScan->getResults();
  for (int i = 0; i < results.getCount(); i++) {
    BLEAdvertisedDevice dev = results.getDevice(i);
    if (dev.getName() == "STA3_BLE") {
      Serial.println("✅ STA3_BLE encontrado, conectando...");
      pClient = BLEDevice::createClient();
      pClient->connect(&dev);
      BLERemoteService* svc = pClient->getService(BLEUUID(serviceUUID.c_str()));
      if (svc) {
        BLERemoteCharacteristic* ch = svc->getCharacteristic(BLEUUID(characteristicUUID.c_str()));
        if (ch) {
          ch->registerForNotify(notifyCallback);
          Serial.println("✅ Conectado y suscrito a STA3_BLE");
          connected = true;
          return;
        }
      }
      Serial.println("❌ Error en conexión BLE");
    }
  }
  Serial.println("❌ STA3_BLE no encontrado, reintentando...");
}

// 🔁 SETUP
void setup() {
  Serial.begin(115200);
  delay(100);

  connectToWiFi();

  // 🕒 Sincronización con PC como servidor NTP
  configTime(-5 * 3600, 0, "172.23.0.42");
  Serial.print("⏳ Sincronizando hora con NTP (PC)");
  while (time(nullptr) < 100000) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n🕒 Hora sincronizada con éxito");

  client.setServer(mqtt_server, mqtt_port);
  connectToMQTT();

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  connectToSTA3();
}

// 🔁 LOOP
void loop() {
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop();

  if (!connected) {
    connectToSTA3();
  }
}

