/**
 * main_xiaozhi.cpp
 * Xiaozhi AI Voice Assistant & Desktop Robot
 * Board: ESP32-S3 WeAct N16R8 (16MB Flash, 8MB PSRAM OPI)
 * Display: GMT147SPI (ST7789V3 172x320 IPS)
 * Env: esp32s3_xiaozhi
 *
 * Hardware Pinout Map:
 *   [GMT147SPI Display - SPI3/HSPI]
 *     SCL  -> GPIO40 (SCLK)
 *     SDA  -> GPIO41 (MOSI)
 *     CS   -> GPIO39
 *     DC   -> GPIO38
 *     RES  -> GPIO47
 *     BL   -> 3.3V
 *   [INMP441 MEMS Microphone - I2S0]
 *     SCK  -> GPIO15
 *     WS   -> GPIO16
 *     SD   -> GPIO17
 *     L/R  -> GND (Left channel)
 *   [MAX98357A I2S DAC / Speaker - I2S1]
 *     BCLK -> GPIO12
 *     LRC  -> GPIO13
 *     DIN  -> GPIO14
 *     GAIN -> GND (12dB)
 *   [VL53L0X / VL53L1X ToF Distance Sensor - I2C]
 *     SDA  -> GPIO8
 *     SCL  -> GPIO9
 *     XSHUT-> GPIO21
 *   [4x Servos (180 deg) - LEDC PWM]
 *     SERVO1 -> GPIO4
 *     SERVO2 -> GPIO5
 *     SERVO3 -> GPIO6
 *     SERVO4 -> GPIO7
 *   [Status & Controls]
 *     RGB LED -> GPIO48 (WS2812 onboard)
 *     BUTTON  -> GPIO1  (Wake / Push-to-talk)
 */

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <math.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <VL53L0X.h>
#include <ESP32Servo.h>
#include <driver/i2s.h>
#include "Logo/Logo.h"

// --- Hardware Globals ---
static Adafruit_MPU6050 mpu;
static VL53L0X tof;
static Servo servos[4];
static const int servoPins[4] = {SERVO_PIN_1, SERVO_PIN_2, SERVO_PIN_3, SERVO_PIN_4};
static int servoTargets[4] = {90, 90, 90, 90};
static float servoCurrents[4] = {90.0, 90.0, 90.0, 90.0};
static const float servoMaxSlew = 2.0; // max degrees per frame
static uint32_t lastServoUpdate = 0;
static float filteredBattVoltage = 4.0;

static Adafruit_SSD1306 oled(128, 64, &Wire, -1);
static bool oledReady = false;


static TFT_eSPI tft = TFT_eSPI();

// Sprite 1bpp cho logo: 240x190
static constexpr int SPRITE_W = 240;
static constexpr int SPRITE_H = 190;
static constexpr int SPRITE_Y = 28;
static TFT_eSprite logoSprite = TFT_eSprite(&tft);

// Sprite 1bpp cho dong chu chay (marquee ticker): 240x20
static constexpr int MARQUEE_W   = 240;
static constexpr int MARQUEE_H   = 20;
static constexpr int MARQUEE_Y   = 292;
static TFT_eSprite marqueeSprite = TFT_eSprite(&tft);

// Bang mau ReShape Lab & Cyberpunk
static const uint16_t COLOR_RESHAPE_ORANGE = tft.color565(217, 119, 87); // #D97757 chinh hang
static const uint16_t COLOR_CYBER_CYAN     = tft.color565(0, 240, 255);
static const uint16_t COLOR_ELECTRIC_BLUE  = tft.color565(70, 160, 255);
static const uint16_t COLOR_NEON_GREEN     = tft.color565(40, 255, 160);
static const uint16_t COLOR_PURE_WHITE     = TFT_WHITE;
static const uint16_t COLOR_BG             = TFT_BLACK;

static const uint16_t THEME_COLORS[] = {
    COLOR_RESHAPE_ORANGE,
    COLOR_CYBER_CYAN,
    COLOR_ELECTRIC_BLUE,
    COLOR_PURE_WHITE,
    COLOR_NEON_GREEN};
static constexpr size_t NUM_THEMES = sizeof(THEME_COLORS) / sizeof(THEME_COLORS[0]);

// Chuoi chay marquee o day man hinh
static const char kMarqueeText[] = "  ✦ RESHAPE LAB ✦ CINQ ✦ TRIAD UAV ECOSYSTEM ✦ ESP32-S3 N16R8 ✦ AUTOMATION & ROBOTICS ✦";
static int gMarqueeOffset        = 0;
static int gMarqueeTextW         = 0;

// Render 1 khung logo voi ty le 'scale' vao sprite (chong giat tuyet doi)
static void renderLogoFrame(float scale, uint16_t fgColor, int maxVisibleY = SPRITE_H)
{
    logoSprite.fillSprite(0);
    logoSprite.setBitmapColor(fgColor, COLOR_BG);

    constexpr int kRowBytes = (kLogoTftW + 7) / 8;
    const float cx          = (SPRITE_W - 1) / 2.0f;
    const float cy          = (SPRITE_H - 1) / 2.0f;
    const float logo_cx     = (kLogoTftW - 1) / 2.0f;
    const float logo_cy     = (kLogoTftH - 1) / 2.0f;

    int srcCol[SPRITE_W];
    int srcRow[SPRITE_H];

    for (int x = 0; x < SPRITE_W; ++x) {
        const int sx = static_cast<int>(lroundf((x - cx) / scale + logo_cx));
        srcCol[x]    = (sx >= 0 && sx < kLogoTftW) ? sx : -1;
    }
    for (int y = 0; y < SPRITE_H; ++y) {
        const int sy = static_cast<int>(lroundf((y - cy) / scale + logo_cy));
        srcRow[y]    = (sy >= 0 && sy < kLogoTftH) ? sy : -1;
    }

    const int limitY = min(SPRITE_H, maxVisibleY);
    for (int y = 0; y < limitY; ++y) {
        if (srcRow[y] < 0) continue;
        const uint8_t *row = kLogoTft + srcRow[y] * kRowBytes;
        for (int x = 0; x < SPRITE_W; ++x) {
            const int sx = srcCol[x];
            if (sx < 0) continue;
            if (pgm_read_byte(row + (sx >> 3)) & (0x80 >> (sx & 7))) {
                logoSprite.drawPixel(x, y, 1);
            }
        }
    }

    logoSprite.pushSprite(0, SPRITE_Y);
}

// Phase 1: Laser Scanline Wipe Reveal (Tu tren xuong, lay cam hung tu OLED runIntro)
static void runLaserWipeIntro(uint32_t durationMs)
{
    Serial.println("[ANIM] Phase 1: Laser Wipe Reveal starting...");
    const uint32_t start        = millis();
    constexpr float kFixedScale = 0.82f;
    constexpr int kLogoX = (128 - kLogoOledBigW) / 2;

    while (millis() - start < durationMs) {
        const uint32_t elapsed = millis() - start;
        const int scanY        = static_cast<int>((elapsed * (SPRITE_H + 10)) / durationMs);

        renderLogoFrame(kFixedScale, COLOR_RESHAPE_ORANGE, scanY);

        // Ve tia laser quet ngang o vi tri scanY
        if (scanY < SPRITE_H) {
            tft.drawFastHLine(0, SPRITE_Y + scanY, SPRITE_W, TFT_WHITE);
            if (scanY > 0) tft.drawFastHLine(4, SPRITE_Y + scanY - 1, SPRITE_W - 8, COLOR_CYBER_CYAN);
        }

        // OLED Wipe (reveal from top)
        if (oledReady) {
            oled.clearDisplay();
            const int oledShown = static_cast<int>((elapsed * kLogoOledBigH) / durationMs);
            oled.drawBitmap(kLogoX, 4, kLogoOledBig, kLogoOledBigW, kLogoOledBigH, SSD1306_WHITE);
            oled.fillRect(kLogoX, 4 + oledShown, kLogoOledBigW, kLogoOledBigH - oledShown, SSD1306_BLACK);
            oled.display();
        }

        delay(8);
    }

    // Xoa vet tia laser khung cuoi
    renderLogoFrame(kFixedScale, COLOR_RESHAPE_ORANGE, SPRITE_H);
    if (oledReady) {
        oled.clearDisplay();
        oled.drawBitmap(kLogoX, 4, kLogoOledBig, kLogoOledBigW, kLogoOledBigH, SSD1306_WHITE);
        oled.setTextSize(1);
        oled.setTextColor(SSD1306_WHITE);
        oled.setCursor(30, 48);
        oled.print("RESHAPE LAB");
        oled.display();
    }
}

// Phase 2: Breathing & Pulsing (To -> Nho -> To nhu Display_BootLogo cua js-controler)
static void runBreathingIntro(uint32_t durationMs)
{
    Serial.println("[ANIM] Phase 2: Breathing Zoom starting...");
    constexpr float kMinScale = 0.58f;
    constexpr float kMaxScale = 0.88f;
    constexpr float kCycles   = 2.0f; // 2 nhip tho

    const uint32_t start = millis();
    while (millis() - start < durationMs) {
        const uint32_t elapsed = millis() - start;
        const float phase      = 2.0f * PI * kCycles * (static_cast<float>(elapsed) / durationMs);
        const float scale      = kMinScale + (kMaxScale - kMinScale) * (0.5f + 0.5f * (1.0f - cosf(phase)));

        // Mau chuyen nhe tu ReShape Orange sang Cyan theo nhip
        const uint16_t color = (cosf(phase) > 0) ? COLOR_RESHAPE_ORANGE : COLOR_CYBER_CYAN;
        renderLogoFrame(scale, color);
        delay(12);
    }
}

// Ve khung tinh giao dien (HUD Top Bar + Brand Text + Separator)
static void drawStaticUI()
{
    tft.setTextDatum(MC_DATUM);

    // --- Top Bar HUD ---
    tft.fillRect(0, 0, 240, 24, tft.color565(12, 16, 24));
    tft.drawFastHLine(0, 24, 240, COLOR_RESHAPE_ORANGE);
    tft.setTextColor(TFT_WHITE, tft.color565(12, 16, 24));
    tft.drawString("TRIAD // RESHAPE", 120, 12, 2);

    // --- Brand Text ---
    // RESHAPE LAB (Font 4)
    tft.setTextColor(COLOR_PURE_WHITE, COLOR_BG);
    tft.drawString("RESHAPE LAB", 120, 236, 4);

    // Subtitle (Font 2)
    tft.setTextColor(COLOR_CYBER_CYAN, COLOR_BG);
    tft.drawString("AUTONOMOUS SYSTEMS", 120, 260, 2);

    tft.setTextColor(tft.color565(120, 140, 160), COLOR_BG);
    tft.drawString("WEACT S3 // ILI9341", 120, 276, 1);

    // --- Bottom Separator ---
    tft.drawFastHLine(10, 288, 220, tft.color565(40, 50, 70));
}

// Cap nhat dong Marquee Ticker chay muot o chan man hinh
static void updateMarquee(uint16_t color)
{
    if (gMarqueeTextW == 0) {
        gMarqueeTextW = tft.textWidth(kMarqueeText, 2);
        if (gMarqueeTextW == 0) gMarqueeTextW = 1;
    }

    marqueeSprite.fillSprite(0);
    marqueeSprite.setBitmapColor(color, COLOR_BG);
    marqueeSprite.setTextDatum(TL_DATUM);

    // Ve text 2 lan de lap vo tan lien tuc
    marqueeSprite.drawString(kMarqueeText, gMarqueeOffset, 2, 2);
    marqueeSprite.drawString(kMarqueeText, gMarqueeOffset + gMarqueeTextW, 2, 2);

    marqueeSprite.pushSprite(0, MARQUEE_Y);

    gMarqueeOffset -= 2;
    if (gMarqueeOffset <= -gMarqueeTextW) {
        gMarqueeOffset = 0;
    }
}

// Cap nhat Uptime & Heap tren Top Bar
static void updateHudStats()
{
    static uint32_t lastHudMs = 0;
    const uint32_t now        = millis();
    if (now - lastHudMs < 500) return;
    lastHudMs = now;

    const uint32_t s = now / 1000;
    char buf[24];
    snprintf(buf, sizeof(buf), "UP %02lu:%02lu", static_cast<unsigned long>((s / 60) % 60),
             static_cast<unsigned long>(s % 60));

    tft.setTextDatum(TR_DATUM);
    tft.setTextColor(COLOR_CYBER_CYAN, tft.color565(12, 16, 24));
    tft.drawString(buf, 236, 6, 1);

    tft.setTextDatum(TL_DATUM);
    tft.setTextColor(COLOR_RESHAPE_ORANGE, tft.color565(12, 16, 24));
    tft.drawString("ILI9341", 4, 6, 1);
}

// --- OLED ANIMATIONS ---
static void renderOledKawaiiFace(uint32_t elapsedMs) {
    if (!oledReady) return;
    oled.clearDisplay();
    // Blink every 3 seconds
    bool blink = (elapsedMs % 3000) < 150; 
    int cx = 128 / 2;
    int cy = 64 / 2;
    
    if (blink) {
        oled.drawFastHLine(cx - 30, cy - 5, 20, SSD1306_WHITE);
        oled.drawFastHLine(cx + 10, cy - 5, 20, SSD1306_WHITE);
    } else {
        oled.fillCircle(cx - 20, cy - 5, 12, SSD1306_WHITE);
        oled.fillCircle(cx + 20, cy - 5, 12, SSD1306_WHITE);
        // Kawaii reflection
        oled.fillCircle(cx - 15, cy - 9, 3, SSD1306_BLACK);
        oled.fillCircle(cx + 25, cy - 9, 3, SSD1306_BLACK);
    }
    
    // Kawaii Mouth ^
    oled.drawPixel(cx - 2, cy + 15, SSD1306_WHITE);
    oled.drawPixel(cx - 1, cy + 16, SSD1306_WHITE);
    oled.drawPixel(cx, cy + 16, SSD1306_WHITE);
    oled.drawPixel(cx + 1, cy + 16, SSD1306_WHITE);
    oled.drawPixel(cx + 2, cy + 15, SSD1306_WHITE);
    
    oled.display();
}

static void renderOledRoboEyes(uint32_t elapsedMs) {
    if (!oledReady) return;
    oled.clearDisplay();
    
    uint32_t cycle = elapsedMs % 4000;
    // Chớp mắt kép (Double blink)
    bool blink = (cycle > 1000 && cycle < 1150) || (cycle > 3000 && cycle < 3100);
    
    // Đảo mắt
    int lookOffset = 0;
    if (cycle > 1500 && cycle < 2500) lookOffset = -10;
    else if (cycle > 3500) lookOffset = 10;
    
    int eyeW = 24;
    int eyeH = 34;
    int cx = 128 / 2 + lookOffset;
    int cy = 64 / 2;
    
    if (blink) {
        oled.fillRoundRect(cx - 35, cy, eyeW, 6, 2, SSD1306_WHITE);
        oled.fillRoundRect(cx + 15, cy, eyeW, 6, 2, SSD1306_WHITE);
    } else {
        oled.fillRoundRect(cx - 35, cy - eyeH/2, eyeW, eyeH, 6, SSD1306_WHITE);
        oled.fillRoundRect(cx + 15, cy - eyeH/2, eyeW, eyeH, 6, SSD1306_WHITE);
        
        // Biểu cảm tức giận (Angry) cắt xéo phía trên mắt
        if (cycle > 1500 && cycle < 2500) {
             oled.fillTriangle(cx - 40, cy - eyeH/2 - 5, cx - 8, cy - eyeH/2 - 5, cx - 8, cy - 2, SSD1306_BLACK);
             oled.fillTriangle(cx + 13, cy - eyeH/2 - 5, cx + 45, cy - eyeH/2 - 5, cx + 13, cy - 2, SSD1306_BLACK);
        }
    }
    
    oled.display();
}

void setup()
{
    Serial.begin(115200);
    Serial.println("\n==========================================");
    Serial.println("  ReShape Lab Logo Engine on GMT147SPI");
    Serial.println("  TRIAD Ecosystem - Cinq / Nguyen Trung");
    Serial.println("==========================================");

    // Khoi tao I2C cho OLED / TOF / MPU6050
    Wire.begin(I2C_SDA, I2C_SCL);
    Wire.setClock(400000);
    
    // I2C Bus scan
    Serial.println("[I2C] Scanning bus...");
    for(byte addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        if(Wire.endTransmission() == 0) {
            Serial.printf("[I2C] Found device at 0x%02X\\n", addr);
        }
    }

    if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("[ERR] Khong tim thay OLED SSD1306!");
    } else {
        Serial.println("[OK] OLED SSD1306 san sang.");
        oled.clearDisplay();
        oled.display();
        oledReady = true;
    }

    // MPU6050
    if(!mpu.begin()) {
        Serial.println("[ERR] MPU6050 not found!");
    } else {
        Serial.println("[OK] MPU6050 ready");
        mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
        mpu.setGyroRange(MPU6050_RANGE_500_DEG);
        mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    }

    // VL53L0X
    pinMode(TOF_XSHUT, OUTPUT);
    digitalWrite(TOF_XSHUT, LOW);
    delay(10);
    digitalWrite(TOF_XSHUT, HIGH);
    delay(10);
    tof.setTimeout(500);
    if (!tof.init()) {
        Serial.println("[ERR] VL53L0X not found!");
    } else {
        Serial.println("[OK] VL53L0X ready");
    }

    // Servos
    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);
    ESP32PWM::allocateTimer(2);
    ESP32PWM::allocateTimer(3);
    for(int i=0; i<4; i++) {
        servos[i].setPeriodHertz(50);
        servos[i].attach(servoPins[i], 500, 2400);
        servos[i].write(90);
    }

    // Battery ADC
    analogReadResolution(12);
    pinMode(BATT_SENSE_PIN, INPUT);
    analogSetPinAttenuation(BATT_SENSE_PIN, ADC_11db);
    
    // Audio I2S Mute
    pinMode(SPK_I2S_SD_MODE, OUTPUT);
    digitalWrite(SPK_I2S_SD_MODE, LOW); // Mute initially

    tft.init();
    tft.setRotation(0); // Portrait 240x320
    tft.fillScreen(COLOR_BG);

    // Khoi tao sprite 1bpp cho Logo & Marquee
    logoSprite.setColorDepth(1);
    if (!logoSprite.createSprite(SPRITE_W, SPRITE_H)) {
        Serial.println("[ERR] Khong the tao logoSprite!");
    } else {
        Serial.printf("[OK] logoSprite san sang (%dx%d 1bpp, %d bytes)\n", SPRITE_W, SPRITE_H, (SPRITE_W * SPRITE_H) / 8);
    }

    marqueeSprite.setColorDepth(1);
    if (!marqueeSprite.createSprite(MARQUEE_W, MARQUEE_H)) {
        Serial.println("[ERR] Khong the tao marqueeSprite!");
    } else {
        Serial.printf("[OK] marqueeSprite san sang (%dx%d 1bpp, %d bytes)\n", MARQUEE_W, MARQUEE_H, (MARQUEE_W * MARQUEE_H) / 8);
    }

    // Do do dai text marquee
    gMarqueeTextW = tft.textWidth(kMarqueeText, 2);

    // === CHAY BOOT ANIMATION (Lay tu js-controler) ===
    runLaserWipeIntro(900);  // Phase 1: Laser Scanline Wipe 900ms
    drawStaticUI();          // Ve khung UI tinh
    runBreathingIntro(2500); // Phase 2: Nhip tho 2.5s (Display_BootLogo)

    Serial.println("[OK] Boot Animation hoan tat. Chuyen sang Loop mode.");
}

void loop()
{
    static uint32_t lastFrameMs   = 0;
    static uint32_t themeStartMs  = 0;
    static size_t currentThemeIdx = 0;
    static float breathPhase      = 0.0f;

    const uint32_t now = millis();

    // Hardware Loop Tasks
    if (now - lastServoUpdate >= 20) { // 50Hz update
        lastServoUpdate = now;
        
        // Stagger servo start
        int movingCount = 0;
        for(int i=0; i<4; i++) {
            if(abs(servoTargets[i] - servoCurrents[i]) > 0.1) {
                movingCount++;
            }
        }
        
        for(int i=0; i<4; i++) {
            float diff = servoTargets[i] - servoCurrents[i];
            if(abs(diff) > 0.1) {
                // If not moving yet, and too many are already moving, skip this one to stagger
                if(movingCount > 2 && abs(diff) == abs(servoTargets[i] - 90)) {
                    continue; 
                }
                
                float step = min(abs(diff), (double)servoMaxSlew);
                if(diff > 0) servoCurrents[i] += step;
                else servoCurrents[i] -= step;
                
                servos[i].write(servoCurrents[i]);
            }
        }
        
        // Battery read
        int battRaw = 0;
        for(int i=0; i<16; i++) {
            battRaw += analogRead(BATT_SENSE_PIN);
        }
        battRaw /= 16;
        float vCell = (battRaw / 4095.0) * 3.3 * 2.0;
        filteredBattVoltage = filteredBattVoltage * 0.9 + vCell * 0.1;
    }

    // Duy tri toc do khung hinh ~35 FPS (28ms / frame)
    if (now - lastFrameMs >= 28) {
        lastFrameMs = now;

        // Chuyen doi chu de mau dinh ky moi 4 giay
        if (now - themeStartMs >= 4000) {
            themeStartMs    = now;
            currentThemeIdx = (currentThemeIdx + 1) % NUM_THEMES;
            Serial.printf("[THEME] Doi mau logo index %u (0x%04X)\n", currentThemeIdx, THEME_COLORS[currentThemeIdx]);
        }

        const uint16_t currentColor = THEME_COLORS[currentThemeIdx];

        // Tinh toan nhip tho (Breathing oscillation)
        constexpr float kMinScale = 0.65f;
        constexpr float kMaxScale = 0.86f;
        breathPhase += 0.045f;
        if (breathPhase >= 2.0f * PI) breathPhase -= 2.0f * PI;

        const float scale = kMinScale + (kMaxScale - kMinScale) * (0.5f + 0.5f * (1.0f - cosf(breathPhase)));

        // Render logo len sprite va day ra man hinh
        renderLogoFrame(scale, currentColor);

        // Cap nhat Marquee ticker chay o chan man hinh
        updateMarquee(currentColor);

        // Cap nhat Uptime/Heap
        updateHudStats();
    }

    // --- OLED ANIMATION UPDATE (ROBO EYES) ---
    static uint32_t lastOledMs = 0;
    if (now - lastOledMs >= 40) { // ~25 FPS cho OLED
        lastOledMs = now;
        renderOledRoboEyes(now);
    }
}
