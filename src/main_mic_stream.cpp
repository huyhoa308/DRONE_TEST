#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "config_ai.h" // Chứa WIFI_SSID, WIFI_PASS, WS_SERVER_IP

#define MIC_I2S_SCK 5
#define MIC_I2S_WS 4
#define MIC_I2S_SD 6

#define UDP_PORT 12345
WiFiUDP udp;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n--- BẮT ĐẦU KẾT NỐI WIFI ---");
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected! IP: " + WiFi.localIP().toString());

    // Cấu hình I2S
    i2s_config_t i2s_mic_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = 0,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_mic_config = {
        .bck_io_num = MIC_I2S_SCK,
        .ws_io_num = MIC_I2S_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = MIC_I2S_SD
    };
    
    i2s_driver_install(I2S_NUM_0, &i2s_mic_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_mic_config);
    Serial.println("I2S initialized! Sẵn sàng stream...");
}

void loop() {
    int32_t samples[256];
    size_t bytes_read = 0;
    
    esp_err_t result = i2s_read(I2S_NUM_0, &samples, sizeof(samples), &bytes_read, portMAX_DELAY);
    
    if (result == ESP_OK && bytes_read > 0) {
        int num_samples = bytes_read / sizeof(int32_t);
        int16_t pcm16[256];
        
        for (int i = 0; i < num_samples; i++) {
            // Dịch 16 bit để lấy 16 bit data thực sự (vứt 8 bit rác ở dưới và 8 bit cao không cần thiết)
            pcm16[i] = samples[i] >> 14; // Có thể cần chỉnh số bit dịch tuỳ độ nhạy (14-16)
        }
        
        udp.beginPacket(WS_SERVER_IP, UDP_PORT);
        udp.write((uint8_t*)pcm16, num_samples * sizeof(int16_t));
        udp.endPacket();
    }
}
