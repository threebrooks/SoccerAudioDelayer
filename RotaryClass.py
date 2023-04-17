#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import multiprocessing
from multiprocessing import Process, shared_memory, Value

class Rotary():
    def __init__(self, inc_dec_callback, button_push_callback):
        # Rotary A Pin
        self.RoAPin = 18
        # Rotary B Pin
        self.RoBPin = 17
        # Rotary Switch Pin
        self.RoSPin = 27

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RoSPin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Set up a falling edge detect to callback clear
        GPIO.add_event_detect(self.RoSPin, GPIO.FALLING, callback=button_push_callback)

        self.running = Value('b',True)
        self.pollThread = Process(target=self.pollFunc, args=(inc_dec_callback,))
        self.pollThread.start()
     
    def pollFunc(self, callback):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RoAPin, GPIO.IN)
        GPIO.setup(self.RoBPin, GPIO.IN)
        Last_RoB_Status = 0
        Current_RoB_Status = 0
        while(True):
            flag = 0
            Last_RoB_Status = GPIO.input(self.RoBPin)
            # When RoAPin level changes
            while(not GPIO.input(self.RoAPin)):
                Current_RoB_Status = GPIO.input(self.RoBPin)
                flag = 1
            if flag == 1:
                # Reset flag
                flag = 0
                if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
                    callback(1)
                if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
                    callback(-1)

    def destroy(self):
        for child in multiprocessing.active_children():
            child.kill()
        self.running.value = False

def IncDecCallback(counter):
    print("Counter: "+str(counter))

def ButtonPushCallback(counter):
    print("Button pushed")
        
if __name__ == '__main__':
    try:
        rotary = Rotary(IncDecCallback, ButtonPushCallback)
    except KeyboardInterrupt:
        pass

