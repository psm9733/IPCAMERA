import signal, os, time, io
from camera_module import set_resolution
from f_module import F_read
from threading import Lock
import picamera
from time import sleep

lck = Lock()
mode = 0
effect = 0
resolution = "1920x1080"
annotate="CAM1"
bright = 0
def signal_handler(signum, frame):
        global resolution, annotate, mode, effect
        lck.acquire()
        print 'Signal handler called with signal', signum     
        annotate = F_read("annotate")
        mode = int(F_read("mode"))
        effect = int(F_read("effect"))
        resolution = F_read("resolution")
        bright = int(F_read("bright"))
        print annotate
        print mode
        print effect 
        print resolution
        print bright
        lck.release()

signal.signal(signal.SIGUSR1, signal_handler)
Wfile = open("/home/pi/Desktop/project/info_pid.txt", 'w')

Wfile.write(str(os.getpid()))
Wfile.close()


while True:
        lck.acquire()
        mode = int(mode)
        lck.release()
        print "mode = " + str(mode)
        if mode == 0:
                print "capture camera"
        elif mode == 1:
                print "streaming camera"
        else:   
                print "detection camera"
