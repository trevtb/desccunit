from multiprocessing import Process, Queue
from config import DesecConfigParser
from camhelper import CamIO
import motion
from threadedhttp import TimeoutHTTPRequestHandler, ThreadedHTTPServer
import struct
import fcntl
import socket
import os
import sys
import signal

settings = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
SIOCGIFADDR = 0x8915
pids = []
clients = Queue()
cclients = {}
mdq = None


def graceful_exit(msg):
    global pids
    print msg
    for pid in pids:
        if pid is not None:
            os.system('kill -9 {}'.format(pid))
    sys.exit(0)


def sigterm_handler(signal, _stack_frame):
    graceful_exit("Caught SIGTERM, exiting.")


def startcamio(res, portn, sat, clientarray):
    camio = CamIO(res, portn, sat, clientarray)
    camio.startloop()


def startmotiondetection(movthresh, mddir, q):
    mydetector = motion.DesecMotionDetector(movthresh, mddir, q)
    mydetector.start()


def starthttpserver(interface, ip, port, qfc):
    server = ThreadedHTTPServer((ip, port), TimeoutHTTPRequestHandler)
    print "server started"
    server.serve_forever(interface, ip, port, qfc)


def get_ip():
        ifreq = struct.pack('16sH14s', settings['interface'], socket.AF_INET, '\x00'*14)
        try:
            res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
        except:
            return None
        ip = struct.unpack('16sH2x4s8x', res)[2]
        return socket.inet_ntoa(ip)


def main():
    global settings
    global pids
    global clients
    global cclients
    global mdq

    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        # Initialize the config file
        cp = DesecConfigParser()
        settings=cp.getsettings()

        # Check if the camera is available
        if not CamIO.camavailable(settings['portnum']):
            graceful_exit("ERROR: No camera detected.")

        # Start the camera helper service providing images to all the other processes
        cio = Process(target=startcamio, args = (settings['resolution'],
                                             settings['portnum'], settings['saturation'], clients))
        cio.start()
        pids.append(cio.pid)

        if settings['enablemd']:
            mdq = Queue()
            md = Process(target=startmotiondetection, args=(settings['movthreshold'], settings['mddir'], mdq))
            md.start()
            pids.append(md.pid)
            cclients[str(md.pid)] = mdq
            clients.put(cclients)

        if not settings['onlylocalhost']:
            ip = get_ip()
        else:
            ip = '127.0.0.1'

        #httpq = Queue()
        #starthttpserver(settings['interface'], ip, settings['port'], httpq)
        #cclients['http'] = httpq
        #clients.put(cclients)

    except (KeyboardInterrupt, SystemExit, KeyError):
        graceful_exit("Keyboard interrupt or SIGTERM recieved, exiting.")

if __name__ == '__main__':
    main()