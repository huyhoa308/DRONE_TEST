import socket
import struct
import math
import sys

UDP_IP = "0.0.0.0"
UDP_PORT = 12345
SAMPLE_RATE = 16000

print(f"Đang lắng nghe ở cổng UDP {UDP_PORT}...")
print("Hãy nói vào mic để xem thanh âm lượng nhảy nhé (Bấm Ctrl+C để thoát)!\n")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Ký tự để vẽ VU meter
BAR_CHAR = '█'
MAX_BAR_LENGTH = 50

try:
    while True:
        data, addr = sock.recvfrom(2048)
        
        # ESP32 gửi mảng int16_t (2 bytes mỗi sample)
        num_samples = len(data) // 2
        
        # Bỏ qua gói tin rác
        if num_samples == 0:
            continue
            
        # Giải mã dữ liệu binary thành mảng số nguyên 16-bit
        # '<' = little-endian, 'h' = short (2 bytes)
        format_str = f"<{num_samples}h"
        samples = struct.unpack(format_str, data)
        
        # Tính toán giá trị RMS (Root Mean Square) để thể hiện độ lớn âm thanh
        sum_sq = sum((s * s for s in samples))
        rms = math.sqrt(sum_sq / num_samples)
        
        # Vẽ thanh âm lượng
        # rms thường dao động từ 0 đến khoảng 3000-5000 khi nói bình thường, tối đa 32768
        # Dùng logarit hoặc chia tỷ lệ để hiển thị đẹp hơn
        volume_level = int(rms / 100) # Điều chỉnh số 100 này nếu thanh chạy quá ngắn hoặc quá dài
        
        if volume_level > MAX_BAR_LENGTH:
            volume_level = MAX_BAR_LENGTH
            
        # Đổi màu cho sinh động (nếu Terminal hỗ trợ ANSI escape codes)
        # Xanh lá -> Vàng -> Đỏ
        color = '\033[92m' # Xanh lá
        if volume_level > MAX_BAR_LENGTH * 0.5:
            color = '\033[93m' # Vàng
        if volume_level > MAX_BAR_LENGTH * 0.8:
            color = '\033[91m' # Đỏ
            
        bar = BAR_CHAR * volume_level
        padding = " " * (MAX_BAR_LENGTH - volume_level)
        
        # \r để in đè lên dòng cũ, \033[0m để reset màu
        sys.stdout.write(f"\r{color}[{bar}{padding}] {int(rms):5d} \033[0m")
        sys.stdout.flush()
        
except KeyboardInterrupt:
    print("\n\nĐã dừng VU Meter. Nghịch vui ghê! 😎")
    sock.close()
