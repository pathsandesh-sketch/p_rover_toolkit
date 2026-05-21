import subprocess
import time
import sys
import os

# Target configuration
SCRIPT_TO_RUN = "app_vhwwd.py"
TIMEOUT_SECONDS = 4.0  # Safe grace threshold for frame drops

def launch_and_monitor():
    print(f"\n[WATCHDOG] Initializing execution tree for {SCRIPT_TO_RUN}...")
    
    # Spawn the FFmpeg app as an asynchronous child process
    process = subprocess.Popen(
        [sys.executable, SCRIPT_TO_RUN],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    last_heartbeat = time.time()

    # Set pipe descriptor state to non-blocking to protect execution speed
    os.set_blocking(process.stdout.fileno(), False)

    while True:
        # Check if the process ungracefully exited on its own hardware thread
        if process.poll() is not None:
            print("[WATCHDOG ALERT] Subprocess terminated naturally or via system error.")
            break

        # Check stream log output buffer
        try:
            line = process.stdout.readline()
            if line:
                print(f" -> {line.strip()}") 
                
                if "[HEARTBEAT]" in line:
                    last_heartbeat = time.time()
        except IOError:
            pass 

        # Watchdog assessment metric
        if (time.time() - last_heartbeat) > TIMEOUT_SECONDS:
            print(f"\n[WATCHDOG CRITICAL] Pipeline freeze detected! Hard killing dead stack...")
            process.kill() 
            process.wait()
            break

        time.sleep(0.05)

if __name__ == "__main__":
    print("====================================================")
    print("[SYSTEM WATCHDOG ENGAGED] Ready for fault monitoring.")
    print("====================================================")
    try:
        while True:
            launch_and_monitor()
            print("[WATCHDOG] Clearing process garbage. Resetting system environment in 2s...")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[WATCHDOG DETACHED] Shutting down supervisor gracefully.")
