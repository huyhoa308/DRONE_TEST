#pragma once
#include <Arduino.h>

void Xiaozhi_Init();
void Xiaozhi_Update();
void Xiaozhi_SendAudio(const uint8_t* payload, size_t length);
bool Xiaozhi_IsConnected();
