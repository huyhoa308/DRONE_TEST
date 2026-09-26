/**
 * hello_gmt147.cpp
 * Demo "Hello World" cho ESP32-S3 WeAct N16R8 + GMT147SPI (ST7789V3, 172x320 IPS)
 * Env: esp32s3_gmt147
 *
 * So do noi:
 *   GMT147  |  ESP32-S3 WeAct N16R8
 *   --------+----------------------
 *   VCC     |  3.3V
 *   GND     |  GND
 *   SCL     |  GPIO40 (SCLK - SPI3/HSPI)
 *   SDA     |  GPIO41 (MOSI - SPI3/HSPI)
 *   RES     |  GPIO47 (RST)
 *   DC      |  GPIO38 (DC)
 *   CS      |  GPIO39 (CS)
 *   BL      |  3.3V truc tiep (khong can dieu khien software)
 */

#include <Arduino.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI();

// Mau nen tung vung - khai bao const de dung lai khi blink
static const uint16_t BG_TOP = 0x0254;   // ~color565(0,20,60)
static const uint16_t BG_MID = 0x0128;   // ~color565(0,10,40)
static const uint16_t BG_BOT = 0x0094;   // ~color565(0,5,20)

void setup() {
    Serial.begin(115200);
    Serial.println("GMT147SPI Hello World starting...");

    // BL noi 3.3V truc tiep - khong can pinMode
    tft.init();
    tft.setRotation(0);
    tft.fillScreen(TFT_BLACK);

    // --- Nen gradient 3 vung ---
    tft.fillRect(0,   0, 172, 107, BG_TOP);
    tft.fillRect(0, 107, 172, 107, BG_MID);
    tft.fillRect(0, 214, 172, 106, BG_BOT);

    tft.setTextDatum(MC_DATUM);

    // --- GMT147SPI (tren) ---
    tft.setTextColor(TFT_CYAN, BG_TOP);
    tft.drawString("GMT147SPI", 86, 60, 4);

    // --- HELLO (giua) - dung mau nen tuong minh, KHONG dung TFT_TRANSPARENT ---
    tft.setTextColor(TFT_WHITE, BG_MID);
    tft.setTextSize(2); // Phong to Font 4 len x2 (vi Font 6 chi co chu so, khong co chu cai)
    tft.drawString("HELLO", 86, 140, 4);
    tft.setTextSize(1); // Tra ve size 1 cho cac chu khac

    // --- ESP32-S3 + model (duoi) ---
    tft.setTextColor(tft.color565(100, 200, 255), BG_BOT);
    tft.drawString("ESP32-S3", 86, 220, 4);

    tft.setTextColor(tft.color565(60, 140, 200), BG_BOT);
    tft.drawString("ST7789V3 172x320", 86, 270, 2);

    Serial.println("Display initialized. Hello World shown!");
}

void loop() {
    static bool blink = false;
    static uint32_t lastMs = 0;

    if (millis() - lastMs > 1000) {
        lastMs = millis();
        blink = !blink;

        tft.setTextDatum(MC_DATUM);
        tft.setTextColor(blink ? TFT_WHITE : TFT_CYAN, BG_MID);
        tft.setTextSize(2);
        tft.drawString("HELLO", 86, 140, 4);
        tft.setTextSize(1);

        Serial.printf("Blink: %s\n", blink ? "WHITE" : "CYAN");
    }
}
