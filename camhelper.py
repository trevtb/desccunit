import cv2


class CamIO:
    capture = None
    mainq = None
    clientqs = []

    def __init__(self, resolution, port, saturation, clientlist):
        res = resolution.split('x')
        self.capture = cv2.VideoCapture(port)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, float(res[0]))
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, float(res[1]))
        self.capture.set(cv2.cv.CV_CAP_PROP_SATURATION, float(saturation))
        self.mainq = clientlist

    def getimage(self):
        return cv2.GaussianBlur(self.capture.read()[1], (5, 5), 0)

    @staticmethod
    def writeimg(path, img):
        cv2.imwrite(path, img)

    @staticmethod
    def togray(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def torgb(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @staticmethod
    def diffimg(t_minus, t, t_plus):
        t_minus = cv2.cvtColor(t_minus, cv2.COLOR_BGR2GRAY)
        t = cv2.cvtColor(t, cv2.COLOR_BGR2GRAY)
        t_plus = cv2.cvtColor(t_plus, cv2.COLOR_BGR2GRAY)
        d1 = cv2.absdiff(t_plus, t)
        d2 = cv2.absdiff(t, t_minus)
        return cv2.bitwise_and(d1, d2)

    @staticmethod
    def getvalidpixels(img):
        return cv2.countNonZero(img)

    @staticmethod
    def camavailable(port):
        try:
            cap = cv2.VideoCapture(port)
            img = cap.read()[1]
            cap.release()
        except:
            return False
        return True

    def startloop(self):
        while True:
            if not self.mainq.empty():
                self.clientqs = self.mainq.get()

            img1 = self.capture.read()[1]
            img2 = self.capture.read()[1]
            img3 = self.capture.read()[1]
            for clientq in self.clientqs:
                if not clientq.empty():
                    clientq.put(img1)
                    clientq.put(img2)
                    clientq.put(img3)