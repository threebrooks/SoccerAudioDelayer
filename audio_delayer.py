from AudioDelayerClass import AudioDelayer
from RotaryClass import Rotary
from LCD1602Class import LCD1602Class
import time

lcd1602 = LCD1602Class()

#stream_url = 'https://bvb--di--nacs-ice-fb01--01--cdn.cast.addradio.de/bvb/live/mp3/high?_art=dj0yJmlwPTE5Mi41OC4xMzIuMjUwJmlkPWljc2N4bC00NTVyZWxwZ2ImdD0xNjgwODA2NzI0JnM9Nzg2NmYyOWMjNjdjNmYyYWU0ZmQ1YjQ2YzRhNjc3Mjg5OGZmMDgzOGII'
stream_url = 'http://stream.antenne.de:80/antenne'

output_sampling_rate = 44100
bytes_per_sample = 2
audio_chunk_size_seconds = 0.1
audio_chunk_size = int(audio_chunk_size_seconds*bytes_per_sample*output_sampling_rate)
buffer_num_audio_chunks = 2500

last_status_update = time.time()
def AudioDelayerStatusCallback(status_line):
    global last_status_update
    global lcd1602
    if ((time.time()-last_status_update) > 0.5):
        lcd1602.write(0, status_line)
        last_status_update = time.time()

audio_delayer = AudioDelayer(stream_url=stream_url, status_callback=AudioDelayerStatusCallback, output_sampling_rate=output_sampling_rate, bytes_per_sample=bytes_per_sample, audio_chunk_size=audio_chunk_size, buffer_num_audio_chunks=buffer_num_audio_chunks)

def RotaryIncDecCallback(delta):
    audio_delayer.inc_dec_latency(delta)

last_button_push_time = None
def RotaryButtonPushCallback(dummy):
    global last_button_push_time
    global lcd1602
    if (last_button_push_time == None):
        last_button_push_time = time.time()
        lcd1602.write(1, "Measuring latency...")
    else:
        latency = time.time()-last_button_push_time
        audio_delayer.set_audio_latency(latency)
        lcd1602.write(1, "")
        last_button_push_time = None

rotary = Rotary(RotaryIncDecCallback,RotaryButtonPushCallback)

while(True):
    if ((not audio_delayer.running.value) or (not rotary.running.value)):
        break
    time.sleep(0.1)

print("Destroying everything")
audio_delayer.destroy()
rotary.destroy()
#time.sleep(60*60*24)

