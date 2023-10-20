import multiprocessing
import sys

def PadString(string):
    return (string+"                  ")[:16]

class Display():
    def __init__(self):
        self.lock = multiprocessing.Lock()
        self.rows = ["",""]

    def write(self, row, line):
        self.rows[row] = line
        self.lock.acquire()
        sys.stdout.write("\r"+PadString(self.rows[0])+":"+PadString(self.rows[1]))
        self.lock.release()

