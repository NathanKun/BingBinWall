#!/usr/bin/python3
	
# sudo apt-get install python3-picamera

import picamera
import datetime
timeStr = '{0:%Y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]

camera = picamera.PiCamera()
camera.capture(timeStr + '.jpg')
