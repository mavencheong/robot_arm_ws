from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours

import numpy as np
import imutils
import cv2

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0] ) * 0.5, (ptA[1] + ptB[1] ) * 0.5)

cap = cv2.VideoCapture("http://192.168.43.1:8080/video")

while True:
    ref, frame = cap.read()
    frame = cv2.resize(frame, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
    orig = frame[:480, 0:640]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15,15), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9,2)
    # _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY| cv2.THRESH_OTSU)
    kernel = np.ones((3,3), np.uint8)
    closing = cv2.dilate(thresh, kernel)
    closing = cv2.erode(closing, kernel)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel,iterations=3)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel,iterations=3)

    # result_img = closing.copy()

    cont, hierarchy = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    pixelPerMetrics = None

    for i, cnt in enumerate(cont):
        area = cv2.contourArea(cnt)
        # if (area < 1000 or area > 100000):
        #     continue
        
        orig = frame.copy()
        box = cv2.minAreaRect(cnt)
        # box = cv2.boxPoints(box)
        # box = np.array(box, dtype="int")
        # box = perspective.order_points(box)
        # cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 64), 2)

        cv2.polylines(frame, [cnt], True, (255, 0, 0), 2)
        center = (int(box[0][0]),int(box[0][1])) 
        # (x,y), (w, h), angle = cv2.minAreaRect(cnt)

        cv2.circle(orig, center, 5, (0, 0, 255), -1)


    cv2.imshow('thresh', thresh)
    cv2.imshow('closing', closing)
    cv2.imshow('img', orig)
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()