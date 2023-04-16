import multiprocessing
from multiprocessing import Process, shared_memory, Value
import subprocess
import atexit
import time
import sys

class AudioDelayer:
    def __init__(self, stream_url, output_sampling_rate=44100, bytes_per_sample=2, audio_chunk_size=88200, buffer_num_audio_chunks=2500):
        self.bytes_per_sample = bytes_per_sample
        self.output_sampling_rate = output_sampling_rate
        self.audio_chunk_size = audio_chunk_size
        self.audio_buffer = shared_memory.SharedMemory(create=True,size=buffer_num_audio_chunks*audio_chunk_size)
        self.audio_write_chunk_idx = Value('i',0)
        self.audio_read_chunk_idx = Value('i',0)
        self.pullerThread = Process(target=self.pullerFunc, args=(stream_url, output_sampling_rate,audio_chunk_size,))
        self.pullerThread.start()
        self.pusherThread = Process(target=self.pusherFunc, args=(output_sampling_rate, bytes_per_sample, audio_chunk_size,))
        self.pusherThread.start()

    def pullerFunc(self, stream_url, output_sampling_rate, audio_chunk_size):
        self.cvlc = subprocess.Popen(['cvlc',stream_url,'--sout','#transcode{acodec=s16l,channels=2,samplerate='+str(output_sampling_rate)+'}:std{access=file,mux=wav,dst=-}'], stdout=subprocess.PIPE)
        while (True):
            segment = self.cvlc.stdout.read(audio_chunk_size)
            #print("Writing")
            wrapped_write_idx = (self.audio_write_chunk_idx.value*audio_chunk_size)%self.audio_buffer.size
            self.audio_buffer.buf[wrapped_write_idx:wrapped_write_idx+audio_chunk_size] = segment
            self.audio_write_chunk_idx.value += 1

    def pusherFunc(self, output_sampling_rate, bytes_per_sample, audio_chunk_size):
        self.audio_play = subprocess.Popen(['aplay','-D','hw:CARD=Device,DEV=0','-c','2','-t','raw','-r',str(output_sampling_rate),'-f','S16_LE','-'],stdin=subprocess.PIPE) 
        while (True):
            if (self.audio_read_chunk_idx.value >= self.audio_write_chunk_idx.value):
                time.sleep(audio_chunk_size/(bytes_per_sample*output_sampling_rate))
                continue
            wrapped_read_idx = (self.audio_read_chunk_idx.value*audio_chunk_size)%self.audio_buffer.size
            audio_chunk = self.audio_buffer.buf[wrapped_read_idx:wrapped_read_idx+audio_chunk_size]
            if (audio_chunk != None):
                self.audio_play.stdin.write(audio_chunk)
                self.audio_read_chunk_idx.value += 1

    def get_audio_latency(self):
        return self.audio_chunk_size*(self.audio_write_chunk_idx.value-self.audio_read_chunk_idx.value)/(self.bytes_per_sample*self.output_sampling_rate)

    def inc_dec_latency(self, delta):
        self.audio_read_chunk_idx.value -= delta

    def destroy(self):
        print("Killing subprocesses")
        self.cvlc.kill()
        self.audio_play.kill()

