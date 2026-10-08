import socket
import wave
import sys
import struct

UDP_IP = "0.0.0.0"
UDP_PORT = 12345
RECORD_SECONDS = 5
SAMPLE_RATE = 16000

print(f"Đang lắng nghe ở cổng UDP {UDP_PORT}...")
print(f"Chuẩn bị ghi âm trong {RECORD_SECONDS} giây.")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

audio_data = bytearray()
total_bytes_needed = RECORD_SECONDS * SAMPLE_RATE * 2 # 16-bit = 2 bytes

print("Chờ gói tin đầu tiên từ ESP32...")
data, addr = sock.recvfrom(2048)
print(f"Đã nhận gói tin từ {addr}, BẮT ĐẦU GHI ÂM!")
audio_data.extend(data)

while len(audio_data) < total_bytes_needed:
    data, addr = sock.recvfrom(2048)
    audio_data.extend(data)
    
print("Đã ghi âm xong! Lưu vào file 'mic_test.wav'...")

with wave.open("mic_test.wav", "wb") as wf:
    wf.setnchannels(1) # Mono
    wf.setsampwidth(2) # 16-bit
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_data)
    
print("Hoàn tất! Cậu có thể mở file 'mic_test.wav' để nghe thành quả.")
