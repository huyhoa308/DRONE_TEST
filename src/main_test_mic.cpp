#include <Arduino.h>
#include <driver/i2s.h>

#define MIC_I2S_SCK 5
#define MIC_I2S_WS 4
#define MIC_I2S_SD 6

void setup() {
    Serial.begin(115200);
    delay(2000); // Cho Serial on dinh
    Serial.println("\n\n--- INMP441 MIC TEST MINIMAL ---");

    i2s_config_t i2s_mic_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT, // INMP441 thuong mac dinh chan L/R xuong GND
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = 0,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_mic_config;
    memset(&pin_mic_config, 0xFF, sizeof(pin_mic_config));
    pin_mic_config.bck_io_num = MIC_I2S_SCK;
    pin_mic_config.ws_io_num = MIC_I2S_WS;
    pin_mic_config.data_out_num = I2S_PIN_NO_CHANGE;
    pin_mic_config.data_in_num = MIC_I2S_SD;
    
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_mic_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("Failed installing I2S driver: %d\n", err);
        while(1);
    }
    
    err = i2s_set_pin(I2S_NUM_0, &pin_mic_config);
    if (err != ESP_OK) {
        Serial.printf("Failed setting I2S pins: %d\n", err);
        while(1);
    }
    
    Serial.println("I2S initialized! Start reading...");
}

void loop() {
    int32_t samples[256];
    size_t bytes_read = 0;
    
    esp_err_t result = i2s_read(I2S_NUM_0, &samples, sizeof(samples), &bytes_read, portMAX_DELAY);
    
    if (result == ESP_OK && bytes_read > 0) {
        int num_samples = bytes_read / sizeof(int32_t);
        int64_t sum_sq = 0;
        int32_t max_val = 0;
        
        for (int i = 0; i < num_samples; i++) {
            // INMP441 tra ve 24 bit data tren khung 32 bit, nen dich phai de giam do lon 
            // (hoac bo 8 bit rac neu co)
            int32_t val = samples[i] >> 8; 
            sum_sq += (int64_t)val * val;
            if (abs(val) > max_val) max_val = abs(val);
        }
        
        uint32_t rms = sqrt(sum_sq / num_samples);
        Serial.printf("[MIC TEST] RMS: %8u | MAX: %8d | Read Bytes: %d\n", rms, max_val, bytes_read);
        
        // Print gia tri raw cua 2 sample dau tien de debug tin hieu co bi float (toan 0 hoac toan 1) khong
        if (num_samples >= 2) {
            Serial.printf("           Raw[0]=0x%08X, Raw[1]=0x%08X\n", samples[0], samples[1]);
        }
    }
    delay(100);
}
