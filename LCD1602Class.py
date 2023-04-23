import LCD1602
import multiprocessing

def PadString(string):
    return (string+"                  ")[:16]

class LCD1602Class():
    def __init__(self):
        self.lock = multiprocessing.Lock()
        LCD1602.init(0x27, 1)   # init(slave address, background light)

    def write(self, row, line):
        self.lock.acquire()
        LCD1602.write(0, row, PadString(line))
        self.lock.release()

