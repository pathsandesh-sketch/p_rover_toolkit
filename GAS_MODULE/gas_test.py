import serial
import time

# Configure the serial port connection
arduino_port = '/dev/ttyUSB0'  # Or '/dev/ttyACM0'
baud_rate = 9600

try:
    # Open connection to the Nano
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    ser.reset_input_buffer()
    print("Connected to Arduino Nano successfully!")
    print("Relaying live multi-sensor data stream:\n")
    
    while True:
        if ser.in_waiting > 0:
            # 1. Read the raw text line coming from your Arduino code
            raw_line = ser.readline()
            
            # 2. Convert it from raw bytes to a standard readable string
            decoded_line = raw_line.decode('utf-8', errors='ignore').rstrip()
            
            # 3. Print the relayed string directly onto the Pi's terminal screen
            print(f"[Pi Relay] -> {decoded_line}")
            
        time.sleep(0.05) # Fast check cycle to keep up with the 1-second interval

except KeyboardInterrupt:
    print("\nData relay stopped by user.")
    ser.close()
    
except Exception as e:
    print(f"Error reading from Arduino: {e}")
