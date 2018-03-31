#!/usr/bin/python

# 200 ohm resistor * 3

import time
import RPi.GPIO as GPIO

redPin   = 2
greenPin = 3
bluePin  = 4

def turnOn(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def turnOff(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def redOn():
    turnOn(redPin)

def greenOn():
    turnOn(greenPin)

def blueOn():
    turnOn(bluePin)

def yellowOn():
    turnOn(redPin)
    turnOn(greenPin)

def cyanOn():
    turnOn(greenPin)
    turnOn(bluePin)

def magentaOn():
    turnOn(redPin)
    turnOn(bluePin)

def whiteOn():
    turnOn(redPin)
    turnOn(greenPin)
    turnOn(bluePin)
    
def redOff():
    turnOff(redPin)

def greenOff():
    turnOff(greenPin)

def blueOff():
    turnOff(bluePin)

def yellowOff():
    turnOff(redPin)
    turnOff(greenPin)

def cyanOff():
    turnOff(greenPin)
    turnOff(bluePin)

def magentaOff():
    turnOff(redPin)
    turnOff(bluePin)

def whiteOff():
    turnOff(redPin)
    turnOff(greenPin)
    turnOff(bluePin)
    
def main():
    counter = 0;
    GPIO.setmode(GPIO.BCM)
    while counter < 3:
        counter = counter + 1
        redOn()
        time.sleep(0.5)
        redOff()
        greenOn()
        time.sleep(0.5)
        greenOff()
        blueOn()
        time.sleep(0.5)
        blueOff()
        yellowOn()
        time.sleep(0.5)
        yellowOff()
        cyanOn()
        time.sleep(0.5)
        cyanOff()
        magentaOn()
        time.sleep(0.5)
    	magentaOff()
        whiteOn()
        time.sleep(0.5)
        whiteOff()
    GPIO.cleanup()

main()
