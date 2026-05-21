
gst-launch-1.0 v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,width=640,height=480,framerate=30/1 ! x264enc tune=zerolatency bitrate=1500 speed-preset=ultrafast ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=10.2.131.184 port=8282
