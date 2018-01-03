import cv2
from crop import Crop
import numpy as np

capture = cv2.VideoCapture(0)
crop = Crop()

while True:
    ok, frame = capture.read()
    w, h = frame.shape[1::-1]
    frame = cv2.resize(frame, (int(w*.5), int(h*.5)))
    crop.findColorRange(frame)
    crop.removeBackground()
    crop.trackObject()
    crop.showImage(delay=1)
    
cv2.destroyAllWindows()    
capture.release()

