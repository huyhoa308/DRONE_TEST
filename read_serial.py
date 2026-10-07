import serial
import time
import sys

try:
    ser = serial.Serial('COM19', 115200, timeout=1)
except Exception as e:
    print(f"Error opening COM19: {e}")
    sys.exit(1)

# Reset ESP32
ser.setDTR(False)
ser.setRTS(True)
time.sleep(0.1)
ser.setDTR(False)
ser.setRTS(False)

print("Listening on COM19...")
while True:
    try:
        line = ser.readline()
        if line:
            print(line.decode('utf-8', errors='ignore'), end='')
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")
        break

ser.close()
