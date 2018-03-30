#!/usr/bin/python3

import RPi.GPIO as GPIO
import picamera
import time
import datetime

GPIO.setmode(GPIO.BCM)

# led
RED   = 2
GREEN = 3
BLUE  = 4
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.output(RED, True)
GPIO.output(GREEN, True)
GPIO.output(BLUE, True)

# ultrason
TRIG = 19
ECHO = 26
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)


# beeper
BEEP = 21
GPIO.setup(BEEP,GPIO.OUT)
GPIO.output(BEEP, False)

def mesureDistance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def beepOnce(beepDuration = 0.2, waitDuration = 0.2):
    GPIO.output(BEEP, True)
    time.sleep(beepDuration)
    GPIO.output(BEEP, False)
    time.sleep(waitDuration)

def beepTooClose():
    for i in range(0, 3):
        beepOnce()

def beepDistanceOk():
    beepOnce(1, 1)

def takePhoto():
    timeStr = '{0:%Y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]

    camera = picamera.PiCamera()
    camera.capture(timeStr + '.jpg')

    return timeStr + '.jpg'

def recognize():
    #

def doResult(result):
    #

def main():
    print("Bing Bin Wall Start")
    run = True
    while run:
        try:
            distance = mesureDistance()
            if(distance < 30):
                beepTooClose()
            else if (distance > 70):
                # do nothing
            else:
                beepDistanceOk()
                doResult(recognize(takePhoto()))
                
        except KeyboardInterrupt:
            run = False
            GPIO.cleanup()

main()
