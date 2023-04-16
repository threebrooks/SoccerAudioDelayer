from AudioDelayerClass import AudioDelayer
from RotaryClass import Rotary
import LCD1602

#stream_url = 'https://bvb--di--nacs-ice-fb01--01--cdn.cast.addradio.de/bvb/live/mp3/high?_art=dj0yJmlwPTE5Mi41OC4xMzIuMjUwJmlkPWljc2N4bC00NTVyZWxwZ2ImdD0xNjgwODA2NzI0JnM9Nzg2NmYyOWMjNjdjNmYyYWU0ZmQ1YjQ2YzRhNjc3Mjg5OGZmMDgzOGII'
stream_url = 'http://stream.antenne.de:80/antenne'

#audio_delayer = AudioDelayer(stream_url=stream_url)

def RotaryIncDecCallback(delta):
    print("Delta: "+str(delta))

def RotaryButtonPushCallback(dummy):
    print("Button pushed")

#rotary = Rotary(RotaryIncDecCallback,RotaryButtonPushCallback)

LCD1602.init(0x27, 1)   # init(slave address, background light)
LCD1602.write(0, 0, 'Greetings!!')

