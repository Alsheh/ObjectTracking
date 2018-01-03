import cv2
from trackbar import Trackbar
import numpy as np


class Crop:
    def __init__(self):
        self.trackbar = Trackbar()
        self.image = np.zeros((10,10,3), np.uint8)
        self.trackedObjectImg = np.zeros((10,10,3), np.uint8)
        self.mask = np.zeros((10,10,3), np.uint8)
        self.croppedImg = np.zeros((10,10,3), np.uint8)
        self.point1 = (0, 0)
        self.point2 = (0, 0)
        cv2.namedWindow('Frame')
        cv2.namedWindow("Cropped Frame")
        cv2.namedWindow("Tracked Object Image")
        cv2.setMouseCallback('Frame', self.mouseEvents)
        self.cropping = False
        self.isStillFindingColorRange = False


    def trackObject(self, maxContours=1):
        if self.isStillFindingColorRange:
            return 
        thresh = self.mask
        kernel = np.ones((5,5),np.uint8)
        thresh = cv2.erode(thresh,kernel,iterations = 1)
        thresh = cv2.dilate(thresh,kernel,iterations = 3)


        _, contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #_, contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.RETR_EXTERNAL)
        allContours = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            allContours.append( (area, x, y, w, h) )
            


        bigContours = sorted(allContours, reverse=True)[:maxContours]
        cv2.imshow("mask", self.mask)
        cv2.imshow("thresh", thresh)
        cv2.waitKey(1)
        # draw rectangles around bigest contours
        for bc in bigContours:
            area, x, y, w, h = bc
            cv2.rectangle(self.image, (x, y), (x+w, y+h), (0,255,0), 2)
            

        
            
    def removeBackground(self):
        # get trackbar values 
        lower_limit, upper_limit = self.trackbar.getTrackbarValues()
        
        # remove backroung and leave region of interest
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_limit, upper_limit)
        blackWhite = cv2.bitwise_and(self.image, self.image, mask=mask)

        x, y, w, h = self.getCroppedImgLocation()
        
        # update images
        self.mask = mask
        self.trackedObjectImg = blackWhite
        self.croppedImg = self.image[y:y+h, x:x+w].copy()
        

    def showImage(self, delay=1):
        # If the user presses 's', stop finding color range
        key = cv2.waitKey(delay) & 0xFF
        if key == ord("s"):
            self.point1, self.point2 = (0, 0), (0, 0)
            self.isStillFindingColorRange = False
            print "==> Color range is saved"

        # If we are still finding color range,
        # draw a rectangle slected around the region of interest.
        if self.isStillFindingColorRange:
            cv2.rectangle(self.image, self.point1, self.point2, (0,255,0), 2)

        # Show 3 windows:
        # 1) camera capture window
        cv2.imshow("Frame", self.image)
        # 2) corpped region window
        #if self.croppedImg.size > 0:
            #cv2.imshow("Cropped Frame", self.croppedImg)
        # 3) region of interest window (backround backrond being removed)
        cv2.imshow("Tracked Object Image", self.trackedObjectImg)
            
    def pointsCorrection(self):
        # make sure we have upper left and lower right corners of selected region.
        x1, y1 = self.point1
        x2, y2 = self.point2
        x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
        self.point1 = x1, y1
        self.point2 = x2, y2
            
    def mouseEvents(self, event, x, y, flags, param):
        # If the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being performed.
        if event == cv2.EVENT_LBUTTONDOWN:
            #self.isCroppingDone = False
            #self.isReselect = True
            self.cropping = True
            self.point1 = (x,y)
            self.point2 = (x,y)
            self.isStillFindingColorRange = True
            
        # While the mouse is moving, keep drawing the updated selected region.
        elif self.cropping and event == cv2.EVENT_MOUSEMOVE:
            self.point2 = (x,y)
            self.pointsCorrection()

        # If the left mouse button was released,
        # draw the most recently selected region
        elif self.cropping and event == cv2.EVENT_LBUTTONUP:
            self.point2 = (x,y)
            self.pointsCorrection()
            self.cropping = False

    def getCroppedImgLocation(self):
        # return coordinates of the upper left corner and
        # width and height of the region of interest.
        (x1, y1), (x2, y2) = self.point1, self.point2
        x, y = x1, y1
        w, h = x2-x1, y2-y1
        return x, y, w, h
            
    def findColorRange(self, frame):
        self.image = frame
        x, y, w, h = self.getCroppedImgLocation()

        if w < 1 or h < 1:
            return

        # crop image inside rectangle
        square = self.image[y:y+h, x:x+w].copy()

        # convert image to hsv
        hsv = cv2.cvtColor(square, cv2.COLOR_BGR2HSV)

        # find color range
        h, s, v = cv2.split(hsv)
        min_h, max_h, _, _ = cv2.minMaxLoc(h)
        min_s, max_s, _, _ = cv2.minMaxLoc(s)
        min_v, max_v, _, _ = cv2.minMaxLoc(v)

        # store update the trackbars with the new color range
        lower_limit = np.array([max(min_h, 0), max(min_s, 0), max(min_v, 0)])
        upper_limit = np.array([min(max_h, 179), min(max_s, 255), min(max_v, 255)])
        self.trackbar.setTrackbarValues(lower_limit, upper_limit)
