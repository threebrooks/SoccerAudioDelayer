#!/usr/bin/env python3

import time
from pynput import keyboard
from pynput.keyboard import Key,KeyCode
from multiprocessing import Process, shared_memory, Value

class KeyboardInteractor():
    def __init__(self, inc_dec_callback, button_push_callback):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        self.keyboard_listener.start()
        self.button_push_callback = button_push_callback
        self.inc_dec_callback = inc_dec_callback
        self.running = Value('b',True)
        self.locked = False
        self.ctrl_pressed = False

    def on_press(self, key):
        if (key == Key.ctrl):
            self.ctrl_pressed = True
            return
        if (key == KeyCode.from_char('l') and self.ctrl_pressed):
            self.locked = not self.locked
            if (self.locked):
                print("AudioDelayer input is locked")
            else:
                print("AudioDelayer input is unlocked")

        if (self.locked):
            return
        if (key == Key.up):
            self.inc_dec_callback(1)
        elif (key == Key.down):
            self.inc_dec_callback(-1)
        elif (key == Key.space):
            self.button_push_callback(True)

    def on_release(self, key):
        if (key == Key.ctrl):
            self.ctrl_pressed = False
            return
        if (key == Key.space):
            self.button_push_callback(False)

    def destroy(self):
        pass

def IncDecCallback(counter):
    print("Counter: "+str(counter))

def ButtonPushCallback(pressed):
    if (pressed):
        print("Button pushed")
    else:
        print("Button released")
        
if __name__ == '__main__':
    try:
        rotary = KeyboardInteractor(IncDecCallback, ButtonPushCallback)
        rotary.keyboard_listener.join() 
    except KeyboardInterrupt:
        pass

