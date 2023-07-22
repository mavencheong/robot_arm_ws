
import cv2 as cv
from math import atan2, cos, sin, sqrt, pi
import numpy as np
 
drawing = False
preX, preY = -1,-1



def callback(event, x, y, flags, param):
    global preX, preY, drawing, img

    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        preX = x 
        preY = y
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False
        mask = np.zeros_like(img)
        
        # mask[:, :] = [0, 0] 
        # print(mask.shape )
        color = (255,255,255)
        mask = cv.rectangle(mask, (preX, preY), (x,y), color, -1)
        result = cv.bitwise_and(img,mask)
        cv.imshow('Output Image', result)


# Load the image

img = cv.imread("./images/output_img3.jpg")
cv.imshow('ori', img)
alpha = 0.1 # Contrast control
beta = 100 # Brightness control
img = cv.convertScaleAbs(img, alpha=alpha, beta=beta)
cv.imshow('after', img)
print(img.shape)
img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)


# print(img2.shape)
h,w = img.shape[:2]

cv.namedWindow("draw")
cv.setMouseCallback("draw" , callback)
while True:
    cv.imshow("draw", img)
    if cv.waitKey(10) == 27:
        break

# mask = np.zeros_like(img)
# mask[:, :] = [0, 0, 0] 

# start_point = ((w//2),(h//2))
# end_point = ((w//2 + 100),(h//2 + 100))
# color = (255,255,255)

# mask = cv.rectangle(mask, start_point, end_point, color, -1)
# result = cv.bitwise_and(img,mask)
# cv.imshow('Output Image', result)
cv.destroyAllWindows()
  
# Save the output image to the current directory
# cv.imwrite("min_area_rec_output.jpg", img)