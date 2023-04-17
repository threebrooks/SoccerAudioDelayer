from AudioDelayerClass import AudioDelayer
from RotaryClass import Rotary
import LCD1602
import time

LCD1602.init(0x27, 1)   # init(slave address, background light)

#stream_url = 'https://bvb--di--nacs-ice-fb01--01--cdn.cast.addradio.de/bvb/live/mp3/high?_art=dj0yJmlwPTE5Mi41OC4xMzIuMjUwJmlkPWljc2N4bC00NTVyZWxwZ2ImdD0xNjgwODA2NzI0JnM9Nzg2NmYyOWMjNjdjNmYyYWU0ZmQ1YjQ2YzRhNjc3Mjg5OGZmMDgzOGII'
#stream_url = 'http://stream.antenne.de:80/antenne'
stream_url = "bla"

audio_delayer = AudioDelayer(stream_url=stream_url)

def RotaryIncDecCallback(delta):
    audio_delayer.inc_dec_latency(delta)
    LCD1602.write(0, 0, "Latency: "+str(audio_delayer.get_audio_latency()))

def RotaryButtonPushCallback(dummy):
    print("Button pushed")

rotary = Rotary(RotaryIncDecCallback,RotaryButtonPushCallback)

while(True):
    if ((not audio_delayer.running.value) or (not rotary.running.value)):
        break
    time.sleep(0.1)

print("Destroying everything")
audio_delayer.destroy()
rotary.destroy()
#time.sleep(60*60*24)

