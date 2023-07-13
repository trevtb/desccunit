import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import socket
import camhelper
import Image
import StringIO
import time
import base64


class ThreadedHTTPServer(SocketServer.ThreadingMixIn,
                         BaseHTTPServer.HTTPServer):
    def __init__(self, *args):
        BaseHTTPServer.HTTPServer.__init__(self, *args)

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except socket.timeout:
            print 'Timeout during processing of request from',
            print client_address
        except socket.error, e:
            print e, 'during processing of request from',
            print client_address
        except:
            self.handle_error(request, client_address)
            self.close_request(request)

    def serve_forever(self, interface, ip, port, qfc):
        self.RequestHandlerClass.interface = interface
        self.RequestHandlerClass.port = port
        self.RequestHandlerClass.qfc = qfc
        self.RequestHandlerClass.ip = ip
        BaseHTTPServer.HTTPServer.serve_forever(self)


class TimeoutHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    timeout = 3 * 60
    camh = None
    qfc = None
    ip = None
    port = None

    def setup(self):
        self.request.settimeout(self.timeout)
        SimpleHTTPServer.SimpleHTTPRequestHandler.setup(self)

    def do_HEAD(self):
        print "send header"
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            while True:
                if self.qfc is None or not self.qfc.empty():
                    if self.camh is not None:
                        img = self.camh.getimage()
                    else:
                        img = self.qfc.get()

                    imgrgb = camhelper.CamIO.torgb(img)
                    jpg = Image.fromarray(imgrgb)
                    tmpfile = StringIO.StringIO()
                    jpg.save(tmpfile, 'JPEG')
                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(tmpfile.len))
                    self.end_headers()
                    jpg.save(self.wfile, 'JPEG')
                    time.sleep(0.05)
            return

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="http://' + self.ip + ':' + str(self.port) + '/cam.mjpg"/>')
            self.wfile.write('</body></html>')
            return
        return
