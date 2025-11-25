#include <Ethernet.h>
#include <ArduinoJson.h>

// Настройки сети – ЗАМЕНИ НА СВОИ!
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);
IPAddress server(192, 168, 0, 57); // IP твоего компьютера
int serverPort = 8080;

const String DEVICE_ID = "MCU_001";
EthernetClient client;

void setup() {
  Serial.begin(9600);
  
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Using static IP");
    Ethernet.begin(mac, ip);
  }
  
  delay(1000);
  Serial.println("Ethernet ready!");
  Serial.print("My IP: ");
  Serial.println(Ethernet.localIP());
}

void loop() {
  float temperature = random(200, 300) / 10.0;
  float humidity = random(400, 800) / 10.0;
  int analogValue = analogRead(A0);
  
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["analog_value"] = analogValue;
  doc["timestamp"] = millis();
  
  if (sendData(doc)) {
    Serial.println("Data sent successfully!");
  } else {
    Serial.println("Failed to send data");
  }
  
  delay(5000);
}

// ⚠️ ИСПРАВЛЕННАЯ ФУНКЦИЯ - убрали & перед doc
bool sendData(StaticJsonDocument<200> doc) {
  if (client.connect(server, serverPort)) {
    client.println("POST /data HTTP/1.1");
    client.println("Host: 192.168.1.100:8080");
    client.println("Content-Type: application/json");
    client.println("Connection: close");
    
    String jsonData;
    serializeJson(doc, jsonData);
    
    client.print("Content-Length: ");
    client.println(jsonData.length());
    client.println();
    client.println(jsonData);
    
    client.stop();
    return true;
  }
  return false;
}