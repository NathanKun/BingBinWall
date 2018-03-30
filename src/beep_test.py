import RPi.GPIO as GPIO
import time

BEEP = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEEP,GPIO.OUT)
GPIO.output(BEEP, True)
time.sleep(1)
GPIO.output(BEEP, False)
'''
feq = 1
dc = 0.5

p = GPIO.PWM(BEEP, feq)

p.start(dc)

for i in range(0, 3):
    counter = 0
    while counter < 4000:
        counter = counter + 1
        feq = feq + 1
        p.ChangeFrequency(feq)
        time.sleep(0.0001)
        
    counter = 0
    while counter < 4000:
        counter = counter + 1
        feq = feq - 1
        p.ChangeFrequency(feq)
        time.sleep(0.0001)

p.stop()'''
GPIO.cleanup()
