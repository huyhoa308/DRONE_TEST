#include "XiaozhiClient.h"
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <driver/i2s.h>
#include "config_ai.h"
#include "Audio/Audio.h"

static WebSocketsClient webSocket;
static bool isConnected = false;
static bool isRecording = false;

extern void Audio_PlayStream(const uint8_t* data, size_t len);

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("[WS] Disconnected!");
            isConnected = false;
            break;
        case WStype_CONNECTED:
            Serial.printf("[WS] Connected to url: %s\n", payload);
            isConnected = true;
            break;
        case WStype_TEXT:
            Serial.printf("[WS] Text: %s\n", payload);
            break;
        case WStype_BIN:
            // Nhận được audio từ server -> phát ra loa
            Audio_PlayStream(payload, length);
            break;
        default:
            break;
    }
}

void Xiaozhi_Init() {
    Serial.print("[WIFI] Connecting to ");
    Serial.println(WIFI_SSID);
    
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    
    // Khong block loop, chi bat dau ket noi
    // WS se tu dong retry neu chua connect WiFi
    webSocket.begin(WS_SERVER_IP, WS_SERVER_PORT, "/");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
}

void Xiaozhi_Update() {
    webSocket.loop();
    
    static uint32_t lastWifiMs = 0;
    if (millis() - lastWifiMs > 2000) {
        lastWifiMs = millis();
        if (WiFi.status() == WL_CONNECTED) {
            // Serial.println("[WIFI] Connected.");
        } else {
            Serial.println("[WIFI] Reconnecting...");
        }
    }
}

void Xiaozhi_SendAudio(const uint8_t* payload, size_t length) {
    if (isConnected) {
        webSocket.sendBIN(payload, length);
    }
}

bool Xiaozhi_IsConnected() {
    return isConnected;
}
