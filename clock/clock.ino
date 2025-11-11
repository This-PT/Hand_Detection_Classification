#include <vector>
using namespace std;
#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>

const char* ssid = ".";
const char* password = ".";
uint32_t a = 32;
uint32_t b = 33;
uint32_t c = 25;
uint32_t d = 26;
uint32_t e = 27;
uint32_t f = 23;
uint32_t g = 22;
const char* mqtt_server = "mqtt-dashboard.com";
const char* mqtt_topic  = "group99/u2";

WiFiClient espClient;
PubSubClient client(espClient);
int idx = 0;
int last_idx = -1;  // Track last idx for printing only when changed
unsigned long currt = 0; // Track last minute

vector<vector<uint32_t>> v = {
  {a,b,c,d,e,f},       // 0
  {b,c},               // 1
  {a,b,d,e,g},         // 2
  {a,b,c,d,g},         // 3
  {b,c,g,f},           // 4
  {a,c,d,g,f},         // 5
  {a,c,d,e,f,g},       // 6
  {a,b,c,f},           // 7
  {a,b,c,d,e,f,g},     // 8
  {a,b,c,d,g,f}        // 9
};

void setup_wifi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT broker...");
    String clientId = "ESP32_Client_" + String(random(0xffff), HEX); // Unique client ID
    if (client.connect(clientId.c_str())) {
      Serial.println(" connected ✅");
      client.subscribe(mqtt_topic);
      Serial.print("Subscribed to topic: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print(" failed, rc=");
      Serial.print(client.state());
      Serial.println(" — retrying in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
    String msg = "";
    for (unsigned int i = 0; i < length; i++) {
        msg += (char)payload[i];
    }
    msg.trim();

    String cleanMsg = "";
    bool negative = false;
    for (unsigned int i = 0; i < msg.length(); i++) {
        char c = msg[i];
        if (c == '-' && i == 0) negative = true;
        else if (isDigit(c)) cleanMsg += c;
    }

    if (cleanMsg.length() > 0) {
        idx = cleanMsg.toInt();
        if (negative) idx = -idx;
    } else {
        idx = 0;
    }

    if (idx != last_idx) {
        Serial.print("Received idx: ");
        Serial.println(idx);
        last_idx = idx;
    }
}

void setup() {
    pinMode(a,OUTPUT); pinMode(b,OUTPUT); pinMode(c,OUTPUT);
    pinMode(d,OUTPUT); pinMode(e,OUTPUT); pinMode(f,OUTPUT); pinMode(g,OUTPUT);
    pinMode(17,OUTPUT); // Alarm/target pin
    pinMode(12, INPUT_PULLUP); // Button input

    Serial.begin(115200);
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
}

unsigned long mwant = 0;
unsigned long hwant = 4;

void loop() {
    if (!client.connected()) reconnect();
    client.loop();

    unsigned long ms = millis();
    unsigned long seconds = ms / 1000;
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;

    // Clear all segments first, then light up current minute
    uint32_t allPins[] = {a,b,c,d,e,f,g};
    for (uint32_t pin : allPins) digitalWrite(pin, LOW);

    if (minutes < 10) {
        for (uint32_t pin : v[minutes]) digitalWrite(pin, HIGH);
    }

    // Button logic to set target time
    if(digitalRead(12) == 0){
        seconds = seconds % 60;
        minutes = minutes % 60;

        Serial.println("now");
        Serial.print(hours); Serial.print(" : ");
        Serial.print(minutes); Serial.print(" : ");
        Serial.println(seconds);

        if(idx == 0) mwant += 10;
        if(idx == 1) mwant += 15;

        Serial.println("set_time_to");
        Serial.print(hwant); Serial.print(" : ");
        Serial.println(mwant);

        delay(1000);
    }

    // Track last minute for segment clearing
    if(minutes > currt) currt = minutes;

    // Alarm logic
    if(hours > hwant || (hours == hwant && minutes >= mwant)){
        digitalWrite(17,HIGH);
    } else {
        digitalWrite(17,LOW);
    }
}
