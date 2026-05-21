gst-launch-1.0 v4l2src device=/dev/video0 ! video/x-raw,width=640,height=480,framerate=30/1 ! v4l2h264enc extra-controls="controls,h264_profile=4,h264_level=10,video_bitrate=1500000;" ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=10.2.131.184 port=8282
# if that doesnt work
gst-launch-1.0 v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,width=640,height=480,framerate=30/1 ! x264enc tune=zerolatency bitrate=1500 speed-preset=ultrafast ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=10.2.131.184 port=8282
