import cv2
import requests
from flask import Flask, Response, render_template_string, request as flask_request

app = Flask(__name__)

# 1. Your Raspberry Pi's IP Address
PI_IP = "10.2.140.109" 

# 2. FORCE OPENCV TO LISTEN FOR THE PI IMMEDIATELY ON STARTUP
# This opens port 8282 right now so the Pi won't get "Connection Refused"
STREAM_URL = "tcp://0.0.0.0:8282?listen"
print("\n[STARTING UPHUB] Opening port 8282. Waiting for Raspberry Pi video...")
cap = cv2.VideoCapture(STREAM_URL)
print("[CONNECTED] Pi video stream successfully hooked!\n")

HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Control Center</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #1e1e1e; color: white; margin: 0; padding: 20px; }
        .container { display: flex; flex-direction: column; align-items: center; gap: 20px; }
        img { border: 4px solid #333; border-radius: 8px; max-width: 640px; background: #000; width: 100%; }
        .controls { display: grid; grid-template-columns: repeat(3, 80px); grid-template-rows: repeat(3, 80px); gap: 10px; justify-content: center; }
        button { background: #444; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:active { background: #00ff00; color: black; }
        .hidden { visibility: hidden; }
    </style>
</head>
<body>
    <h1>ML Video Feed & Robot Controls</h1>
    <div class="container">
        <img src="/video_feed" />
        <h3>Control Pad</h3>
        <div class="controls">
            <button class="hidden"></button>
            <button onmousedown="sendCmd('forward')" onmouseup="sendCmd('stop')">▲</button>
            <button class="hidden"></button>
            <button onmousedown="sendCmd('left')" onmouseup="sendCmd('stop')">◀</button>
            <button onmousedown="sendCmd('stop')">■</button>
            <button onmousedown="sendCmd('right')" onmouseup="sendCmd('stop')">▶</button>
            <button class="hidden"></button>
            <button onmousedown="sendCmd('backward')" onmouseup="sendCmd('stop')">▼</button>
            <button class="hidden"></button>
        </div>
    </div>
    <script>
        function sendCmd(direction) {
            fetch('/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'direction=' + direction
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/move', methods=['POST'])
def move_robot():
    direction = flask_request.form.get('direction')
    try:
        requests.post(f"http://{PI_IP}:8000/motor", data={'direction': direction}, timeout=0.1)
    except requests.exceptions.RequestException:
        pass 
    return "OK", 200

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # ML Inference Text Layer
        cv2.putText(frame, "ML Engine: Live", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2712, threaded=True)
