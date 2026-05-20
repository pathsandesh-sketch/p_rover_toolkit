#On laptop
  python3 app.py

#On RPI Terminal 1(motor control):
  sudo python pi_motor_server.py

#On RPI Terminal 2(Video Incoming): {refer to ffmpeg folder}
  ffmpeg -f v4l2 -video_size 640x480 -framerate 30 -i /dev/video0 -vcodec libx264 -preset ultrafast -tune zerolatency -b:v 1500k -f mpegts tcp://10.2.131.184:8282

#Opening Web Interface:
  http://localhost:2712
