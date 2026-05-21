import threading
import time
from flask import Flask, request
import RPi.GPIO as GPIO

app = Flask(__name__)

# Pin Definitions based on your layout (BCM Numbering)
IN1 = 17  # Left Motor Forward
IN2 = 27  # Left Motor Backward
IN3 = 22  # Right Motor Forward
IN4 = 23  # Right Motor Backward

GPIO.setmode(GPIO.BCM)
for pin in [IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# --- MISSION CRITICAL WATCHDOG CONFIGURATION ---
last_command_time = time.time()
TIMEOUT_THRESHOLD = 0.5  # Safe grace window: 500 milliseconds
current_state = 'stop'

def safety_watchdog_loop():
    """Background thread that kills motor power instantly if Wi-Fi drops."""
    global last_command_time, current_state
    while True:
        # If the robot is driving, but we haven't heard from the Mac in 500ms:
        if current_state != 'stop' and (time.time() - last_command_time) > TIMEOUT_THRESHOLD:
            print("[SAFETY ALERT] Lost contact with Mac! Emergency stopping motors...", flush=True)
            stop_motors()
            current_state = 'stop'
        time.sleep(0.05)  # Scan state rapidly every 50ms
# -----------------------------------------------

def stop_motors():
    for pin in [IN1, IN2, IN3, IN4]:
        GPIO.output(pin, GPIO.LOW)

@app.route('/motor', methods=['POST'])
def control_motor():
    global last_command_time, current_state
    command = request.form.get('direction')
    
    # 1. Refresh the safety metrics the instant a packet breaks through the socket
    last_command_time = time.time()
    current_state = command
    
    # 2. Process physical drive logic
    stop_motors() # Reset pins before applying next move
    
    if command == 'forward':
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
    elif command == 'backward':
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN4, GPIO.HIGH)
    elif command == 'left':
        # Spin left: Right motor forward, Left motor backward
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
    elif command == 'right':
        # Spin right: Left motor forward, Right motor backward
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN4, GPIO.HIGH)
    elif command == 'stop':
        stop_motors()
        
    return f"Motor set to {command}", 200

if __name__ == '__main__':
    # Start the safety monitor daemon thread before starting the web server
    watchdog_thread = threading.Thread(target=safety_watchdog_loop, daemon=True)
    watchdog_thread.start()
    
    # Listen on port 8000 on the Pi
    app.run(host='0.0.0.0', port=8000)
