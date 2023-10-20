from AudioDelayerClass import AudioDelayer
import time
from enum import Enum
import os


stream_url = ('BVB Netradio','https://bvb--di--nacs-ice-fb01--01--cdn.cast.addradio.de/bvb/live/mp3/high?_art=dj0yJmlwPTE5Mi41OC4xMzIuMjUwJmlkPWljc2N4bC00NTVyZWxwZ2ImdD0xNjgwODA2NzI0JnM9Nzg2NmYyOWMjNjdjNmYyYWU0ZmQ1YjQ2YzRhNjc3Mjg5OGZmMDgzOGII')
#stream_url = 'http://stream.antenne.de:80/antenne'

output_sampling_rate = 44100
bytes_per_sample = 2
audio_chunk_size_seconds = 0.1
audio_chunk_size = int(audio_chunk_size_seconds*bytes_per_sample*output_sampling_rate)
buffer_num_audio_chunks = 2500

if (os.uname()[4][:3] == 'arm'):
    from LCD1602Class import LCD1602Class
    display = LCD1602Class()
else:
    from DisplayClass import Display
    display = Display()

last_status_update = time.time()
def AudioDelayerStatusCallback(status_line):
    global last_status_update
    global display
    if ((time.time()-last_status_update) > 0.5):
        display.write(0, status_line)
        last_status_update = time.time()

audio_delayer = AudioDelayer(stream_url=stream_url, status_callback=AudioDelayerStatusCallback, output_sampling_rate=output_sampling_rate, bytes_per_sample=bytes_per_sample, audio_chunk_size=audio_chunk_size, buffer_num_audio_chunks=buffer_num_audio_chunks)

def RotaryIncDecCallback(delta):
    audio_delayer.inc_dec_latency(delta)

class ButtonStateMachine(Enum):
    NONE = 1
    BUTTON_DOWN_AMBIGUOUS = 2
    LATENCY_MEASURING = 3

bsm = ButtonStateMachine.NONE
last_button_push_time = None
def RotaryButtonPushCallback(downPress):
    global last_button_push_time
    global display
    global bsm
    if (downPress):
        if (bsm == ButtonStateMachine.NONE):
            bsm = ButtonStateMachine.BUTTON_DOWN_AMBIGUOUS
            last_button_push_time = time.time()
        elif (bsm == ButtonStateMachine.LATENCY_MEASURING):
            latency = time.time()-last_button_push_time
            audio_delayer.set_audio_latency(latency)
            display.write(1, "")
            last_button_push_time = None
            bsm = ButtonStateMachine.NONE
    else:
        if (bsm == ButtonStateMachine.BUTTON_DOWN_AMBIGUOUS):
            if ((time.time()-last_button_push_time) < 3.0):
                display.write(1, "Measuring latency...")
                bsm = ButtonStateMachine.LATENCY_MEASURING
            else:
                if (os.uname()[4][:3] == 'arm'):
                    display.write(1, "Shutting down...")
                    os.system("sudo shutdown -h now")

if (os.uname()[4][:3] == 'arm'):
    from RotaryClass import Rotary
    interactor = Rotary(RotaryIncDecCallback,RotaryButtonPushCallback)
else:
    from KeyboardInteractorClass import KeyboardInteractor
    interactor = KeyboardInteractor(RotaryIncDecCallback,RotaryButtonPushCallback)

while(True):
    if ((not audio_delayer.running.value) or (not interactor.running.value)):
        break
    time.sleep(0.1)

print("Destroying everything")
audio_delayer.destroy()
interactor.destroy()
#time.sleep(60*60*24)

