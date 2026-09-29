#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <VL53L0X.h>
#include <ESP32Servo.h>
#include <driver/i2s.h>

// OLED config
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// MPU6050 config
Adafruit_MPU6050 mpu;

// VL53L0X config
VL53L0X sensorToF;

// Servos config
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

// I2S config for INMP441
#define I2S_PORT I2S_NUM_0

void setup_i2s() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 64,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = MIC_I2S_SCK,
        .ws_io_num = MIC_I2S_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = MIC_I2S_SD
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);
    i2s_start(I2S_PORT);
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    Serial.println("ESP32-S3 Robot Base System Starting...");

    // I2C Setup
    Wire.begin(I2C_SDA, I2C_SCL);
    
    // Setup OLED
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("SSD1306 allocation failed");
    } else {
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);
        display.setCursor(0, 0);
        display.println("OLED Init OK!");
        display.display();
    }

    // Setup MPU6050
    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050 chip");
    } else {
        Serial.println("MPU6050 Found!");
        mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
        mpu.setGyroRange(MPU6050_RANGE_500_DEG);
        mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    }

    // Setup VL53L0X
    sensorToF.setTimeout(500);
    if (!sensorToF.init()) {
        Serial.println("Failed to detect and initialize VL53L0X!");
    } else {
        Serial.println("VL53L0X Found!");
    }

    // Setup Servos
    // Allow allocation of all timers
    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);
    
    servo1.setPeriodHertz(50);
    servo2.setPeriodHertz(50);
    servo3.setPeriodHertz(50);
    servo4.setPeriodHertz(50);

    servo1.attach(SERVO_PIN_1, 500, 2400);
    servo2.attach(SERVO_PIN_2, 500, 2400);
    servo3.attach(SERVO_PIN_3, 500, 2400);
    servo4.attach(SERVO_PIN_4, 500, 2400);

    // Setup Touch
    pinMode(TOUCH_PIN, INPUT);

    // Setup Battery ADC
    analogReadResolution(12);
    pinMode(BATTERY_ADC_PIN, INPUT);

    // Setup INMP441
    setup_i2s();
    
    Serial.println("All Systems Initialized!");
}

void loop() {
    // 1. Read Touch
    int touchVal = digitalRead(TOUCH_PIN);

    // 2. Read Battery
    int battVal = analogRead(BATTERY_ADC_PIN);
    float voltage = (battVal / 4095.0) * 3.3 * 2; // Assuming 1/2 voltage divider for 2S

    // 3. Read ToF
    uint16_t dist = 0;
    if (sensorToF.init()) dist = sensorToF.readRangeSingleMillimeters();

    // 4. Update OLED
    display.clearDisplay();
    display.setCursor(0, 0);
    display.printf("Touch: %d\n", touchVal);
    display.printf("Batt: %.2fV\n", voltage);
    display.printf("ToF: %d mm\n", dist);
    display.display();

    // 5. Minimal servo movement
    static int pos = 0;
    static int dir = 1;
    servo1.write(pos);
    pos += (dir * 5);
    if (pos >= 180 || pos <= 0) dir = -dir;

    delay(100);
}
