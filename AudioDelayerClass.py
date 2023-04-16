import multiprocessing
from multiprocessing import Process, shared_memory, Value
import subprocess
import atexit
import time
import sys

#stream_url = 'https://bvb--di--nacs-ice-fb01--01--cdn.cast.addradio.de/bvb/live/mp3/high?_art=dj0yJmlwPTE5Mi41OC4xMzIuMjUwJmlkPWljc2N4bC00NTVyZWxwZ2ImdD0xNjgwODA2NzI0JnM9Nzg2NmYyOWMjNjdjNmYyYWU0ZmQ1YjQ2YzRhNjc3Mjg5OGZmMDgzOGII'
stream_url = 'http://stream.antenne.de:80/antenne'

sampling_rate = 44100
bytes_per_sample = 2
audio_chunk_size = 4096
buffer_num_audio_chunks = 2500

class AudioProcessor:
    def __init__(self):
        self.audio_buffer = shared_memory.SharedMemory(create=True,size=buffer_num_audio_chunks*audio_chunk_size)
        self.audio_write_chunk_idx = Value('i',0)
        self.audio_read_chunk_idx = Value('i',0)
        self.pullerThread = Process(target=self.pullerFunc)
        self.pullerThread.start()
        self.pusherThread = Process(target=self.pusherFunc)
        self.pusherThread.start()

    def pullerFunc(self):
        self.cvlc = subprocess.Popen(['cvlc',stream_url,'--sout','#transcode{acodec=s16l,channels=2,samplerate='+str(sampling_rate)+'}:std{access=file,mux=wav,dst=-}'], stdout=subprocess.PIPE)
        while (True):
            segment = self.cvlc.stdout.read(audio_chunk_size)
            #print("Writing")
            wrapped_write_idx = (self.audio_write_chunk_idx.value*audio_chunk_size)%self.audio_buffer.size
            self.audio_buffer.buf[wrapped_write_idx:wrapped_write_idx+audio_chunk_size] = segment
            self.audio_write_chunk_idx.value += 1

    def pusherFunc(self):
        self.audio_play = subprocess.Popen(['aplay','-D','hw:CARD=Device,DEV=0','-c','2','-t','raw','-r',str(sampling_rate),'-f','S16_LE','-'],stdin=subprocess.PIPE) 
        while (True):
            if (self.audio_read_chunk_idx.value >= self.audio_write_chunk_idx.value):
                time.sleep(audio_chunk_size/(bytes_per_sample*sampling_rate))
                continue
            sys.stdout.write("\rLatency: "+str((self.audio_write_chunk_idx.value-self.audio_read_chunk_idx.value)/(bytes_per_sample*sampling_rate)))
            wrapped_read_idx = (self.audio_read_chunk_idx.value*audio_chunk_size)%self.audio_buffer.size
            audio_chunk = self.audio_buffer.buf[wrapped_read_idx:wrapped_read_idx+audio_chunk_size]
            if (audio_chunk != None):
                self.audio_play.stdin.write(audio_chunk)
                self.audio_read_chunk_idx.value += 1

    def destroy(self):
        print("Killing subprocesses")
        self.cvlc.kill()
        self.audio_play.kill()

audioProc = AudioProcessor()

def onExit():
    audioProc.destroy()

atexit.register(onExit)

time.sleep(60*60*24)
