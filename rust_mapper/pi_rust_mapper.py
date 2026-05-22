import csv
from datetime import datetime
from collections import Counter
from ultralytics import YOLO

# 1. Load the OPENVINO optimized model folder instead of the .pt file
# This tells Ultralytics to use the highly optimized CPU runtime
model = YOLO("best_openvino_model/")

# 2. Set source to 0 to use the Raspberry Pi's local camera module
# (If you have multiple cameras, it might be 1 or 2, but 0 is standard)
camera_source = 0 

# Explicitly map your rust categories
CLASS_NAMES = {
    0: "mild-corrosion",
    1: "moderate-corrosion",
    2: "severe-corrosion"
}

corrosion_history_map = []

print("Initializing local Pi camera and loading optimized OpenVINO model...")
print("Mapping in progress... Press 'Ctrl+C' in the terminal to stop and save.")

try:
    # 3. Predict on the local camera
    # vid_stride=2 skips every other frame to keep the video smooth and live on the Pi
    results = model.predict(source=camera_source, stream=True, show=True, vid_stride=2)
    
    for result in results:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        frame_categories = []
        max_confidence = 0.0
        
        if result.obb is not None and len(result.obb) > 0:
            class_ids = result.obb.cls.cpu().numpy().astype(int)
            confidences = result.obb.conf.cpu().numpy()
            
            max_confidence = float(max(confidences))
            
            for cid in class_ids:
                class_str = CLASS_NAMES.get(cid, f"unknown-{cid}")
                frame_categories.append(class_str)
        
        counts_aggregator = Counter(frame_categories)
        total_rust_patches = sum(counts_aggregator.values())
        
        stream_snapshot = {
            "timestamp": current_time,
            "total_detections": total_rust_patches,
            "peak_confidence": round(max_confidence, 4),
            "mild-corrosion": counts_aggregator.get("mild-corrosion", 0),
            "moderate-corrosion": counts_aggregator.get("moderate-corrosion", 0),
            "severe-corrosion": counts_aggregator.get("severe-corrosion", 0)
        }
        
        corrosion_history_map.append(stream_snapshot)
        
        # Live console logging
        if total_rust_patches > 0:
            print(f"[{current_time}] RUST DETECTED! Total: {total_rust_patches} | Mild: {stream_snapshot['mild-corrosion']} Mod: {stream_snapshot['moderate-corrosion']} Sev: {stream_snapshot['severe-corrosion']}")
        else:
            print(f"[{current_time}] Monitoring... Surface Clear.")

except KeyboardInterrupt:
    print("\n[INFO] Stopped by user signal.")

finally:
    # 4. Save out the timeline map to a CSV file on the Pi
    output_filename = "pi_rust_live_map.csv"
    
    if corrosion_history_map:
        headers = ["timestamp", "total_detections", "peak_confidence", "mild-corrosion", "moderate-corrosion", "severe-corrosion"]
        with open(output_filename, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(corrosion_history_map)
            
        print(f"[SUCCESS] Data map exported on the Pi to: '{output_filename}'")
    else:
        print("[WARNING] No data collected.")
