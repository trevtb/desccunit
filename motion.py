from camhelper import CamIO
import datetime


class DesecMotionDetector:
    qfc = None
    movthreshold = None
    directory = None
    t_minus = None
    t = None
    t_plus = None

    def __init__(self, movthreshold, mddir, qfc):
        self.movthreshold = movthreshold
        self.qfc = qfc
        self.directory = mddir

    def start(self):
        while self.qfc.qsize() < 3:
            pass
        self.t_minus = self.qfc.get()
        self.t = self.qfc.get()
        self.t_plus = self.qfc.get()

        while True:
            if not self.qfc.empty():
                dimg = CamIO.diffimg(self.t_minus, self.t, self.t_plus)

                # Write images if motion is detected
                if CamIO.getvalidpixels(dimg) > self.movthreshold:
                    self.motion_detected()

                # Read next image
                self.t_minus = self.t
                self.t = self.t_plus
                self.t_plus = self.qfc.get()

                self.qfc.task_done()

    def motion_detected(self, img):
        CamIO.writeimg(self.directory + datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.jpg', img)
