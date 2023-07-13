from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import camhelper
import Image
import StringIO
import time
import base64


class DesecHttpHandler(SimpleHTTPRequestHandler):
    # Basic initialization
    ip = None
    interface = None
    port = None
    key = None
    qfc = None
    useauth = None
    useaccessprotect = None
    allowip = None
    camh = None

    def do_HEAD(self):
        print "send header"
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        print "send header"
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Authorization required\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.useaccessprotect and self.allowip != self.client_address[0]:
            self.wfile.write('Access denied for your ip address ' + str(self.client_address[0]))
            return

        if self.headers.getheader('Authorization') is None and self.useauth:
            self.do_AUTHHEAD()
            self.wfile.write('Access denied')
            pass
        elif self.headers.getheader('Authorization') == 'Basic ' + self.key or not self.useauth:
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
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')
            pass


class DesecHttpServer(HTTPServer):
    qfc = None

    def serve_forever(self, interface, ip, port, username, password, qfc,
                      allowedip, camport=None, resolution=None, saturation=None, useauthentication=True, useaccessprotection=False):
        self.RequestHandlerClass.interface = interface
        self.RequestHandlerClass.port = port
        self.RequestHandlerClass.key = base64.b64encode(username+':'+password)
        self.RequestHandlerClass.qfc = qfc
        self.RequestHandlerClass.ip = ip
        self.RequestHandlerClass.allowip = allowedip
        if qfc is None:
            self.RequestHandlerClass.camh = camhelper.CamIO(resolution, camport, saturation)

        self.RequestHandlerClass.useauth = useauthentication
        self.RequestHandlerClass.useaccessprotect = useaccessprotection

        HTTPServer.serve_forever(self)