[Unit]
Description=Rover State Machine
After=network.target pigpio.service
Requires=pigpio.service

[Service]
Type=simple
User=sahassandesh
WorkingDirectory=/home/sahassandesh
# Execute using your specific python path or virtual environment
ExecStart=/usr/bin/python3 /home/sahassandesh/pi_motor_server.py
Restart=on-failure
RestartSec=3
KillMode=process

[Install]
WantedBy=multi-user.target

# open using
sudo nano /etc/systemd/system/robot_mission.service
