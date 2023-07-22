	
# This programs calculates the orientation of an object.
# The input is an image, and the output is an annotated image
# with the angle of otientation for each object (0 to 180 degrees)
 
import cv2   as cv
from math import atan2, cos, sin, sqrt, pi
import numpy as np
 
# Load the image
img = cv.imread("./images/output_img3.jpg")

# cap = cv.VideoCapture("http://192.168.43.1:8080/video")

dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_50)
params = cv.aruco.DetectorParameters()

detector = cv.aruco.ArucoDetector(dict, params)

cv.imshow('Input Image', img)
 

(corners, ids, rejected)= detector.detectMarkers(img)

# cv.polylines(img, markerCorners, True, (0, 255, 64), 2)


print(corners)

int_corners = np.int0(corners)

cv.polylines(img,  int_corners , True, (0, 255, 65), 2)
aruco_perimeter = cv.arcLength(corners[0], True)

pixel_to_cm_ratio = aruco_perimeter / 20

print(pixel_to_cm_ratio)

alpha = 0.5 # Contrast control
beta = 0.5 # Brightness control
img = cv.convertScaleAbs(img, alpha=alpha, beta=beta)
# # Convert image to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
blur = cv.GaussianBlur(gray, (9,9), sigmaX=2,sigmaY=2)
kernel = np.ones((5,5), np.uint8)
_, bw = cv.threshold(blur, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU) 
# closing = cv.morphologyEx(bw, cv.MORPH_OPEN, kernel,iterations=3)
# thresh = cv.adaptiveThreshold(blur, 20, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 9,2)
canny = cv.Canny(bw, 100, 255, 4)
# # Convert image to binary

closing = cv.erode(canny, kernel)
closing = cv.dilate(closing, kernel)
# closing = cv.erode(closing, kernel)


# closing = cv.morphologyEx(bw, cv.MORPH_CLOSE, kernel,iterations=3)
contours, _ = cv.findContours(canny, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

 
# # # Find all the contours in the thresholded image
# contours, _ = cv.findContours(closing, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
 
for i, c in enumerate(contours):
 
  # Calculate the area of each contour
  area = cv.contourArea(c)
 
  # Ignore contours that are too small or too large
  # if area < 3700 or 100000 < area:
  #   continue
 
  # cv.minAreaRect returns:
  # (center(x, y), (width, height), angle of rotation) = cv2.minAreaRect(c)
  rect = cv.minAreaRect(c)
  box = cv.boxPoints(rect)
  box = np.int0(box)
  
  point1 = np.array((int((box[0][0] + box[1][0]) * .5), int((box[0][1] + box[1][1]) * .5)))

  point2 = np.array((int((box[2][0] + box[3][0]) * .5), int((box[2][1] + box[3][1]) * .5)))


  point3 = np.array((int((box[1][0] + box[2][0]) * .5), int((box[1][1] + box[2][1]) * .5)))

  point4 = np.array((int((box[0][0] + box[3][0]) * .5), int((box[0][1] + box[3][1]) * .5)))

  dist1 = np.linalg.norm( point1 - point2 )
	dist2 = np.linalg.norm(point3 - point4)



  # print(rect)
  # Retrieve the key parameters of the rotated bounding box
  center = (int(rect[0][0]),int(rect[0][1])) 
  width = round(rect[1][0] / pixel_to_cm_ratio, 1)
  height = round(rect[1][1] / pixel_to_cm_ratio, 1)
  angle = int(rect[2])
  deg = int(rect[2])
 
  # print(box)
  # print(width)
  # print(height)
     
  # if width < height:
  #   angle = 90 - angle
  # else:
  #   angle = -angle
         
  # label = "  Height: " + str(height) + " cm, Width " + str(width) + " cm, angle: " + str(angle)
  #   #   textbox = cv.rectangle(img, (center[0]-35, center[1]-25), 
  #   #     (center[0] + 295, center[1] + 10), (255,255,255), -1)
  # cv.putText(img, label, (center[0], center[1]), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 1, cv.LINE_AA)

  

#   cv.circle(img, box[2], 3, (255, 0, 255), 2)

  print(box)

  cv.line(img, point1, point2  , (255, 255, 0), 3, cv.LINE_AA)
  cv.line(img, point3, point4  , (255, 255, 0), 3, cv.LINE_AA)

  cv.drawContours(img,[box],0,(0,0,255),2)
 
cv.imshow('Output Image', img)
cv.imshow('blur', blur)
cv.imshow('bw', bw)
cv.imshow('closing', closing)
cv.imshow('canny', canny)
cv.waitKey(0)
cv.destroyAllWindows()


# import cv2 as cv
# from math import atan2, cos, sin, sqrt, pi
# import numpy as np
 
# def drawAxis(img, p_, q_, color, scale):
#   p = list(p_)
#   q = list(q_)
 
#   ## [visualization1]
#   angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
#   hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
 
#   # Here we lengthen the arrow by a factor of scale
#   q[0] = p[0] - scale * hypotenuse * cos(angle)
#   q[1] = p[1] - scale * hypotenuse * sin(angle)
#   cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)
 
#   # create the arrow hooks
#   p[0] = q[0] + 9 * cos(angle + pi / 4)
#   p[1] = q[1] + 9 * sin(angle + pi / 4)
#   cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)
 
#   p[0] = q[0] + 9 * cos(angle - pi / 4)
#   p[1] = q[1] + 9 * sin(angle - pi / 4)
#   cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)
#   ## [visualization1]
 
# def getOrientation(pts, img):
#   ## [pca]
#   # Construct a buffer used by the pca analysis
#   sz = len(pts)
#   data_pts = np.empty((sz, 2), dtype=np.float64)
#   for i in range(data_pts.shape[0]):
#     data_pts[i,0] = pts[i,0,0]
#     data_pts[i,1] = pts[i,0,1]
 
#   # Perform PCA analysis
#   mean = np.empty((0))
#   mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, mean)
 
#   # Store the center of the object
#   cntr = (int(mean[0,0]), int(mean[0,1]))
#   ## [pca]
 
#   ## [visualization]
#   # Draw the principal components
#   cv.circle(img, cntr, 3, (255, 0, 255), 2)
#   p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
#   p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
#   drawAxis(img, cntr, p1, (255, 255, 0), 1)
#   drawAxis(img, cntr, p2, (0, 0, 255), 5)
 
#   angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
#   ## [visualization]
 
#   # Label with the rotation angle
#   label = "  Rotation Angle: " + str(-int(np.rad2deg(angle)) - 90) + " degrees"
#   textbox = cv.rectangle(img, (cntr[0], cntr[1]-25), (cntr[0] + 250, cntr[1] + 10), (255,255,255), -1)
#   cv.putText(img, label, (cntr[0], cntr[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv.LINE_AA)
 
#   return angle
 
# # Load the image
# img = cv.imread("./images/input_img_600.jpg")
 
# # Was the image there?
# if img is None:
#   print("Error: File not found")
#   exit(0)
 
# cv.imshow('Input Image', img)
 
# # Convert image to grayscale
# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
 
# # Convert image to binary
# _, bw = cv.threshold(gray, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
 
# # Find all the contours in the thresholded image
# contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
 
# for i, c in enumerate(contours):
 
#   # Calculate the area of each contour
#   area = cv.contourArea(c)
 
#   # Ignore contours that are too small or too large
#   if area < 3700 or 100000 < area:
#     continue
 
#   # Draw each contour only for visualisation purposes
#   cv.drawContours(img, contours, i, (0, 0, 255), 2)
 
#   # Find the orientation of each shape
#   getOrientation(c, img)
 
# cv.imshow('Output Image', img)
# cv.waitKey(0)
# cv.destroyAllWindows()
  
# # Save the output image to the current directory
# # cv.imwrite("output_img.jpg", img)