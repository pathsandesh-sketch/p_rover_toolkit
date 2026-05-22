import cv2
import requests
from flask import Flask, Response, render_template_string, request as flask_request
from ultralytics import YOLO

app = Flask(__name__)

# 1. Load the OpenVINO optimized model on your laptop CPU
# This will handle the inference extremely fast inside the web thread
model = YOLO("best_openvino_model/")

# Explicitly map your custom rust categories
CLASS_NAMES = {
    0: "mild-corrosion",
    1: "moderate-corrosion",
    2: "severe-corrosion"
}

# 2. Your Raspberry Pi's IP Address
PI_IP = "10.2.140.109" 

# 3. Listen for incoming raw video from the Pi
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
        
        /* Metrics Overlay Bar */
        .metrics-bar { display: flex; gap: 15px; justify-content: center; margin-bottom: 5px; }
        .metric-card { background: #2a2a2a; padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 14px; border: 1px solid #444; }
        .mild { border-left: 4px solid #00ff00; }
        .mod { border-left: 4px solid #ffa500; }
        .sev { border-left: 4px solid #ff0000; }
        
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
        
        <h3>Corrosion Detection Metrics</h3>
        <div class="metrics-bar">
            <div id="m-mild" class="metric-card mild">Mild: 0</div>
            <div id="m-mod" class="metric-card mod">Moderate: 0</div>
            <div id="m-sev" class="metric-card sev">Severe: 0</div>
        </div>
        
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

        // Long-polling system to fetch raw rust count metrics continuously from backend 
        setInterval(async () => {
            try {
                let response = await fetch('/live_counts');
                if (response.ok) {
                    let data = await response.json();
                    document.getElementById('m-mild').innerText = "Mild: " + data.mild;
                    document.getElementById('m-mod').innerText = "Moderate: " + data.mod;
                    document.getElementById('m-sev').innerText = "Severe: " + data.severe;
                }
            } catch (e) { /* suppress connection drops */ }
        }, 300); // refresh 3 times per second
    </script>
</body>
</html>
"""

# Dynamic thread storage for updating the API dashboard
latest_counts = {"mild": 0, "moderate": 0, "severe": 0}

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/live_counts')
def live_counts():
    return latest_counts, 200

@app.route('/move', methods=['POST'])
def move_robot():
    direction = flask_request.form.get('direction')
    try:
        requests.post(f"http://{PI_IP}:8000/motor", data={'direction': direction}, timeout=0.1)
    except requests.exceptions.RequestException:
        pass 
    return "OK", 200

def gen_frames():
    global latest_counts
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # 4. RUN OPEN-VINO OBB INFERENCE ON INCOMING PIPED FRAME
        # verbose=False cleans your server logs from clutter
        results = model.predict(source=frame, verbose=False)
        
        frame_counts = {"mild": 0, "moderate": 0, "severe": 0}
        
        if len(results) > 0 and results[0].obb is not None:
            result = results[0]
            
            # Use Ultralytics built-in plotting to render oriented boxes natively
            # This handles custom text orientation, label flags, and color spaces cleanly
            frame = result.plot()
            
            # Parse classes to update the dashboard count state
            class_ids = result.obb.cls.cpu().numpy().astype(int)
            for cid in class_ids:
                if cid == 0: frame_counts["mild"] += 1
                elif cid == 1: frame_counts["moderate"] += 1
                elif cid == 2: frame_counts["severe"] += 1
                
        # Pipe counts back out to global scope for API long-polling
        latest_counts = frame_counts
        
        # Static UI confirmation signature
        cv2.putText(frame, "Engine: YOLO11s-OBB OpenVINO", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2712, threaded=True)
