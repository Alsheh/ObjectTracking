import cv2
import numpy as np

class Trackbar:
    def __init__(self, windowName = "Color Range"):
        self.windowName = windowName
        cv2.namedWindow(windowName)
        for i in ["Min", "Max"]:
            lower = 0 if i == "Min" else 255
            for j in ['H', 'S', 'B']:
                upper = 179 if  j == "H" else 255
                cv2.createTrackbar("%s_%s" % (i, j), windowName, lower, upper, self.callback)

    def callback(self, value):
        lower_limit, upper_limit = self.getTrackbarValues()
        self.setTrackbarValues(lower_limit, upper_limit)
        
    def getTrackbarValues(self):
        values = []
        for i in ["Min", "Max"]:
            for j in ['H','S','B']:
                v = cv2.getTrackbarPos("%s_%s" % (i, j), self.windowName)
                values.append(v)
        return np.array(values[:3]), np.array(values[3:])

    def setTrackbarValues(self, lower_limit, upper_limit):
        MinMax = ["Min", "Max"]
        HSB = ['H','S','B']
        values = [lower_limit, upper_limit]
        windowName = self.windowName
        for i in range(2):
            for j in range(3):
                trackbarName = "%s_%s" % (MinMax[i], HSB[j])
                cv2.setTrackbarPos(trackbarName, windowName, int(values[i][j]))
