	
# This programs calculates the orientation of an object.
# The input is an image, and the output is an annotated image
# with the angle of otientation for each object (0 to 180 degrees)
 
import cv2   as cv
import math
import numpy as np

mask = []
gray = []


def gradient(pt1, pt2):
	diff1 = 0
	diff2 = 0

	diff1 = pt2[1] - pt1[1]
	diff2 = pt2[0] - pt1[0]


	print (pt1, pt2)
	print(diff2)
	print("diff")
	return (diff1) / (diff2)



def getAngle(pt1, pt2, pt3):
	m1 = gradient(pt1, pt2)
	m2 = gradient(pt1, pt3)
	print((m2-m1))
	print((1 + (m2*m1)))
	print("--")


	ang = math.atan((m2-m1)/ (1 + (m2*m1)))

	print(ang)
	ang = math.degrees(ang)

	return ang


def calAngle(box):
	point1 = np.array((int((box[0][0] + box[1][0]) * .5), int((box[0][1] + box[1][1]) * .5)))
	point2 = np.array((int((box[2][0] + box[3][0]) * .5), int((box[2][1] + box[3][1]) * .5)))
	point3 = np.array((int((box[1][0] + box[2][0]) * .5), int((box[1][1] + box[2][1]) * .5)))
	point4 = np.array((int((box[0][0] + box[3][0]) * .5), int((box[0][1] + box[3][1]) * .5)))

	dist1 = np.linalg.norm( point1 - point2 )
	dist2 = np.linalg.norm(point3 - point4)
	workPoint1 = point1 
	workPoint2 = point2

	if dist2 > dist1:
		workPoint1 = point3
		workPoint2 = point4	

	basePoint = np.array((0,0))
	targetPoint = np.array((0,0))
	if workPoint1[0] <= workPoint2[0]: # X1 < X2
		if workPoint1[1] >= workPoint2[1]: #y1 > y2 = "/" direction
			basePoint = workPoint1
			targetPoint = workPoint2
		else: # "\"
			basePoint = workPoint2
			targetPoint = workPoint1
	else: #X1 > X2
		if workPoint1[1] <= workPoint2[1]: #y1 < y2 "/"
			basePoint = workPoint2
			targetPoint = workPoint1
		else: # "\"
			basePoint = workPoint1
			targetPoint = workPoint2

	basePointTan = np.array((basePoint[0]-1, basePoint[1] - 100))
	angle = getAngle(basePoint,  basePointTan, targetPoint)

	return angle

def controller(img, brightness=255,
			contrast=127):
	
	brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))

	contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))

	if brightness != 0:

		if brightness > 0:

			shadow = brightness

			max = 255

		else:

			shadow = 0
			max = 255 + brightness

		al_pha = (max - shadow) / 255
		ga_mma = shadow

		# The function addWeighted calculates
		# the weighted sum of two arrays
		cal = cv.addWeighted(img, al_pha,
							img, 0, ga_mma)

	else:
		cal = img

	if contrast != 0:
		Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
		Gamma = 127 * (1 - Alpha)

		# The function addWeighted calculates
		# the weighted sum of two arrays
		cal = cv.addWeighted(cal, Alpha,
							cal, 0, Gamma)

	# putText renders the specified text string in the image.
	# cv2.putText(cal, 'B:{},C:{}'.format(brightness,
	# 									contrast), (10, 30),
	# 			cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

	return cal


def BrightnessContrast(img, brightness=0):
	brightness = cv.getTrackbarPos('Brightness','GEEK')
	
	contrast = cv.getTrackbarPos('Contrast','GEEK')
	
	effect = controller(img, brightness, contrast)
	return effect 
	
	
def mouseCallback(event, x, y, flags, param):
    global preX, preY, mask, gray
	
    if event == cv.EVENT_LBUTTONDOWN:
	    preX = x
	    preY = y
    elif event == cv.EVENT_LBUTTONUP:
	    mask = np.zeros_like(gray)
	    color = (255,255,255)
	    mask = cv.rectangle(mask, (preX, preY), (x,y), color, -1)
	    
def callback(x):
	pass



        

# Load the image
# img = cv.imread("./images/input_img_600.jpg")
dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_50)
params = cv.aruco.DetectorParameters()

detector = cv.aruco.ArucoDetector(dict, params)

cap = cv.VideoCapture("http://192.168.43.1:8080/video")


cv.namedWindow('GEEK')
cv.namedWindow("MAIN")

cv.createTrackbar('Brightness',
        'GEEK', 255, 2 * 255,
        callback)

cv.createTrackbar('Contrast', 'GEEK',
        127, 2 * 127,
        callback)

cv.createTrackbar('Threshold', 'GEEK',
        50, 255,
        callback)

cv.createTrackbar('blur', 'GEEK',
        5, 255,
        callback)

cv.createTrackbar('zoom', 'GEEK',
        50, 50,
        callback)

cv.setMouseCallback("MAIN", mouseCallback)


pixel_to_cm_ratio = 1
while True:
    ret, frame = cap.read()
    
    cv.imshow('GEEK', frame)

    (corners, ids, rejected)= detector.detectMarkers(frame)

    if len(corners) > 0:
        int_corners = np.int0(corners)
        aruco_perimeter = cv.arcLength(corners[0], True)
        pixel_to_cm_ratio = aruco_perimeter / 20

    brightness = cv.getTrackbarPos('Brightness','GEEK')
    contrast = cv.getTrackbarPos('Contrast','GEEK')
    threshold = cv.getTrackbarPos('Threshold','GEEK')
    blurval = cv.getTrackbarPos('blur','GEEK')
    zoom = cv.getTrackbarPos('zoom','GEEK')


    
    if blurval % 2 == 0:
	    blurval = blurval + 1
    
    effect = controller(frame, brightness,contrast)

    gray = cv.cvtColor(effect, cv.COLOR_BGR2GRAY)

    height, width = gray.shape
    centerX, centerY = int(height/2), int(width/2)
    radiusX, radiusY = int(zoom*height/100), int(zoom*width/100)

    minX,maxX=centerX-radiusX,centerX+radiusX
    minY,maxY=centerY-radiusY,centerY+radiusY

    cropped  = gray[minX:maxX, minY:maxY]
    gray = cv.resize(cropped, (width, height))


    if len(mask) > 0:
	    gray = cv.bitwise_and(gray, mask)

    cv.imshow('MAIN', gray)
    output = gray.copy()
    blur = cv.GaussianBlur(output, (blurval,blurval), 0)
    _, bw = cv.threshold(blur, threshold, 255, cv.THRESH_BINARY | cv.THRESH_OTSU) 
    # # Convert image to binary
    canny = cv.Canny(bw, 100, 255, 4)
    kernel = np.ones((5,5), np.uint8)
    closing = cv.erode(canny, kernel)
    closing = cv.dilate(closing, kernel)
    
    closing = cv.morphologyEx(bw, cv.MORPH_OPEN, kernel,iterations=3)
    contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    for i, c in enumerate(contours):
        # Calculate the area of each contour
        area = cv.contourArea(c)
 
        # # Ignore contours that are too small or too large
        if area < 500 or 100000 < area:
            continue
 
        # cv.minAreaRect returns:
        # (center(x, y), (width, height), angle of rotation) = cv2.minAreaRect(c)
        rect = cv.minAreaRect(c)
        rect_fit = cv.fitEllipse(c)
        box = cv.boxPoints(rect)
        box = np.int0(box)

        angle = calAngle(box)
 
        # Retrieve the key parameters of the rotated bounding box
        center = (int(rect[0][0]),int(rect[0][1])) 
        width = round(rect[1][0] / pixel_to_cm_ratio, 1)
        height = round(rect[1][1] / pixel_to_cm_ratio, 1)
        # angle = int(rect_fit[2])
        deg = int(rect[2])
        m = cv.moments(c)

        
        
        # if width < height:
        #     angle = 90 - angle
        # else:
        #     angle = -angle
        label = "H: " + str(height) + "cm, W " + str(width) + "cm, D: " + str(angle)
        textbox = cv.rectangle(output, (center[0]-35, center[1]-25), 
            (center[0] + 295, center[1] + 10), (255,255,255), -1)
        cv.putText(output, label, (center[0]-50, center[1]), 
        cv.FONT_HERSHEY_SIMPLEX, 0.3, (0,0,0), 1, cv.LINE_AA)
        cv.circle(output, center, 3, (255, 0, 255), 2)
        cv.drawContours(output,[box],0,(0,0,255),2)

    cv.imshow('Output Image', output)
    cv.imshow('bw', bw)
    cv.imshow('gray', gray)
    cv.imshow('blur', blur)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
 

cap.release()
cv.destroyAllWindows()

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
 
#   # cv.minAreaRect returns:
#   # (center(x, y), (width, height), angle of rotation) = cv2.minAreaRect(c)
#   rect = cv.minAreaRect(c)
#   box = cv.boxPoints(rect)
#   box = np.int0(box)
 
#   print(rect)
#   # Retrieve the key parameters of the rotated bounding box
#   center = (int(rect[0][0]),int(rect[0][1])) 
#   width = int(rect[1][0])
#   height = int(rect[1][1])
#   angle = int(rect[2])
#   deg = int(rect[2])
 
#   print(box)
#   print(width)
#   print(height)
     
#   if width < height:
#     angle = 90 - angle
#   else:
#     angle = -angle
         
# #   label = "  Rotation Angle: " + str(angle) + " degrees"
# #   textbox = cv.rectangle(img, (center[0]-35, center[1]-25), 
# #     (center[0] + 295, center[1] + 10), (255,255,255), -1)
# #   cv.putText(img, label, (center[0]-50, center[1]), 
# #     cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 1, cv.LINE_AA)
#   cv.circle(img, center, 3, (255, 0, 255), 2)

#   x2 = int(round(center[0] + height * cos(np.deg2rad(deg))))
#   y2 = int(round(center[1] + height * sin(np.deg2rad(deg))))

#   cv.line(img, center, (x2, y2), (255, 255, 0), 3, cv.LINE_AA)
#   cv.drawContours(img,[box],0,(0,0,255),2)
 
# cv.imshow('Output Image', img)
# cv.waitKey(0)
# cv.destroyAllWindows()


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