import multiprocessing
from multiprocessing import Process, shared_memory, Value
import subprocess
import atexit
import time
import sys
import os

def GetDefaultAudioDevice():
    output = subprocess.check_output(['aplay','-L']).decode('utf-8').split("\n")
    for line in output:
        if (line.startswith("default:")):
            return line
    raise RuntimeError("Could not find default sound card!")

class AudioDelayer:
    def __init__(self, stream_url, status_callback, output_sampling_rate, bytes_per_sample, audio_chunk_size, buffer_num_audio_chunks):
        self.status_callback = status_callback
        self.bytes_per_sample = bytes_per_sample
        self.output_sampling_rate = output_sampling_rate
        self.audio_chunk_size = audio_chunk_size
        self.cvlc = None
        self.audio_play = None
        self.audio_buffer = shared_memory.SharedMemory(create=True,size=buffer_num_audio_chunks*audio_chunk_size)
        self.audio_write_chunk_idx = Value('i',0)
        self.audio_read_chunk_idx = Value('i',0)
        self.running = Value('b',True)
        self.pullerThread = Process(target=self.pullerFunc, args=(stream_url, output_sampling_rate,audio_chunk_size,))
        self.pullerThread.start()
        self.pusherThread = Process(target=self.pusherFunc, args=(output_sampling_rate, bytes_per_sample, audio_chunk_size, GetDefaultAudioDevice(), ))
        self.pusherThread.start()

    def pullerFunc(self, stream_url, output_sampling_rate, audio_chunk_size):
        while (self.running.value):
            self.status_callback("Connecting to "+stream_url)
            self.cvlc = subprocess.Popen(['cvlc',stream_url,'--sout','#transcode{acodec=s16l,channels=2,samplerate='+str(output_sampling_rate)+'}:std{access=file,mux=wav,dst=-}','vlc://quit'], stdout=subprocess.PIPE)
            while (self.running.value):
                if (self.cvlc.poll() != None):
                    break
                segment = self.cvlc.stdout.read(audio_chunk_size)
                if (len(segment) > 0):
                    wrapped_write_idx = (self.audio_write_chunk_idx.value*audio_chunk_size)%self.audio_buffer.size
                    self.audio_buffer.buf[wrapped_write_idx:wrapped_write_idx+audio_chunk_size] = segment
                    self.audio_write_chunk_idx.value += 1
            time.sleep(5)
        print("pullerFunc done")

    def pusherFunc(self, output_sampling_rate, bytes_per_sample, audio_chunk_size, audio_device):
        self.audio_play = subprocess.Popen(['aplay','-D',audio_device,'-c','2','-t','raw','-r',str(output_sampling_rate),'-f','S16_LE','-'],stdin=subprocess.PIPE) 
        while (self.running.value):
            if (self.audio_play.poll() != None):
                self.destroy()
                break
            if (self.audio_read_chunk_idx.value >= self.audio_write_chunk_idx.value):
                time.sleep(audio_chunk_size/(bytes_per_sample*output_sampling_rate))
                continue
            self.status_callback("Latency: "+str(self.get_audio_latency()))
            wrapped_read_idx = (self.audio_read_chunk_idx.value*audio_chunk_size)%self.audio_buffer.size
            audio_chunk = self.audio_buffer.buf[wrapped_read_idx:wrapped_read_idx+audio_chunk_size]
            if (audio_chunk != None):
                self.audio_play.stdin.write(audio_chunk)
                self.audio_read_chunk_idx.value += 1
        print("pusherFunc done")

    def get_audio_latency(self):
        return self.audio_chunk_size*(self.audio_write_chunk_idx.value-self.audio_read_chunk_idx.value)/(self.bytes_per_sample*self.output_sampling_rate)

    def set_audio_latency(self, latency):
        self.audio_read_chunk_idx.value = self.audio_write_chunk_idx.value-self.bytes_per_sample*int(latency*self.output_sampling_rate/self.audio_chunk_size)

    def inc_dec_latency(self, delta):
        self.audio_read_chunk_idx.value -= delta

    def destroy(self):
        self.running.value = False


if __name__ == '__main__':
    try:
        def DummyStatusCallback(line1, line2):
            pass
        audio_delayer = AudioDelayer(stream_url='http://stream.antenne.def:80/antenne', status_callback=DummyStatusCallback, output_sampling_rate=44100, bytes_per_sample=2, audio_chunk_size=88200, buffer_num_audio_chunks=2500)
    except KeyboardInterrupt:
        pass

