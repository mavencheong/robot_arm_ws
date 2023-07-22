import cv2
import numpy as np
import math


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

	##add additional 1 degree
	if angle < 0:
		angle = angle -1
	else:
		angle = angle + 1
	return angle

def BrightnessContrast(brightness=0):
	global pixel_to_cm_ratio
	# getTrackbarPos returns the current
	# position of the specified trackbar.
	brightness = cv2.getTrackbarPos('Brightness',
									'GEEK')
	
	contrast = cv2.getTrackbarPos('Contrast',
								'GEEK')
	final = img.copy()
	final = controller(final, brightness,
						contrast)

	# The function imshow displays an image
	# in the specified window
	
	gray = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (9,9), sigmaX=2,sigmaY=2)
	kernel = np.ones((5,5), np.uint8)
	_, bw = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
	canny = cv2.Canny(bw, 100, 255, 4)
	closing = cv2.erode(canny, kernel)
	closing = cv2.dilate(closing, kernel)
	contours, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	for i, c in enumerate(contours):
 
		# Calculate2 the area of each contour
		area = cv2.contourArea(c)
		 # # Ignore contours that are too small or too large
		if area < 500 or 100000 < area:
			continue
		rect = cv2.minAreaRect(c)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		
		angle = calAngle(box)


		
		
		
		# print(basePoint)
		# print(targetPoint)
		# print(basePointTan)
		

		# angle = 0

		# if dist1 > dist2:
			
		# 	if point1[1] < point2[1]:
		# 		angle = math.degrees(math.atan2(point2[1] - point1[1], point2[0] - point1[0]))
				
		# 		# ang1 = np.arctan2(*point1[::-1])
		# 		# ang2 = np.arctan2(*point2[::-1])
		# 		print("1,2")
		# 		print(point1)
		# 		print(point2)
		# 		print(angle)
		# 	else:
		# 		angle = math.degrees(math.atan2(point1[1] - point2[1], point1[0] - point2[0]))
		# 		# ang1 = np.arctan2(*point2[::-1])
		# 		# ang2 = np.arctan2(*point1[::-1])
		# 		print("2,1")
		# 		print(point2)
		# 		print(point1)
		# 		print(angle)

		# 	# angle = np.rad2deg((ang1 - ang2) % (2 * np.pi))

		# else:
		# 	if point3[0] < point4[0]:
		# 		angle = math.degrees(math.atan2(point3[1] - point4[1], point3[0] - point4[0]))
		# 		print("3,4")
		# 		print(point3)
		# 		print(point4)
		# 		print(angle)
		# 		# ang1 = np.arctan2(*point3[::-1])
		# 		# ang2 = np.arctan2(*point4[::-1])
		# 	else:
		# 		angle = math.degrees(math.atan2(point4[1] - point3[1], point4[0] - point3[0]))
		# 		# ang1 = np.arctan2(*point4[::-1])
		# 		# ang2 = np.arctan2(*point3[::-1])
		# 		print("4,3")
		# 		print(point4)
		# 		print(point3)
		# 		print(angle)

			# angle = np.rad2deg((ang1 - ang2) % (2 * np.pi))
	

		# if abs(angle) > 90:
		# 	angle = 180 - angle
		# else:
		# 	angle = 90 - angle

		# print(rect)
		# Retrieve the key parameters of the rotated bounding box
		center = (int(rect[0][0]),int(rect[0][1])) 
		# width = round(rect[1][0] / pixel_to_cm_ratio, 1)
		# height = round(rect[1][1] / pixel_to_cm_ratio, 1)
		# angle = int(rect[2])
		deg = int(rect[2])
 
		# label = "  Height: " + str(height) + " cm, Width " + str(width) + " cm, angle: " + str(angle)
		label = "angle: " + str(angle)
		cv2.putText(final, label, (center[0]+ 50, center[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1, cv2.LINE_AA)

		

#   cv.circle(img, box[2], 3, (255, 0, 255), 2)

		# cv2.line(final, point1, point2  , (255, 255, 0), 3, cv2.LINE_AA)
		# cv2.line(final, point3, point4  , (255, 255, 0), 3, cv2.LINE_AA)

		# cv2.putText(final, "1", point1, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)
		# cv2.putText(final, "2", point2, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)
		# cv2.putText(final, "3", point3, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)
		# cv2.putText(final, "4", point4, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)
		# cv2.circle(final, basePoint, 3, (255, 0, 255), 2)

		# cv2.circle(final, basePointTan, 3, (255, 0, 255), 2)
		
		cv2.drawContours(final,[box],0,(0,0,255),2)
		cv2.imshow('Effect', final)
		cv2.imshow('blur', blur)
		cv2.imshow('bw', bw)
		cv2.imshow('closing', closing)
		cv2.imshow('canny', canny)

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
		cal = cv2.addWeighted(img, al_pha,
							img, 0, ga_mma)

	else:
		cal = img

	if contrast != 0:
		Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
		Gamma = 127 * (1 - Alpha)

		# The function addWeighted calculates
		# the weighted sum of two arrays
		cal = cv2.addWeighted(cal, Alpha,
							cal, 0, Gamma)

	# putText renders the specified text string in the image.
	# cv2.putText(cal, 'B:{},C:{}'.format(brightness,
	# 									contrast), (10, 30),
	# 			cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

	return cal

# The function imread loads an image
# from the specified file and returns it.
original = cv2.imread("./images/output_img3.jpg")
# Making another copy of an image.
img = original.copy()

# dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
# params = cv2.aruco.DetectorParameters()

# detector = cv2.aruco.ArucoDetector(dict, params)
# (corners, ids, rejected)= detector.detectMarkers(img)
# int_corners = np.int0(corners)
# aruco_perimeter = cv2.arcLength(corners[0], True)
# pixel_to_cm_ratio = aruco_perimeter / 20

# The function namedWindow creates a
# window that can be used as a placeholder
# for images.
cv2.namedWindow('GEEK')

# The function imshow displays an
# image in the specified window.
cv2.imshow('GEEK', original)

# createTrackbar(trackbarName,
# windowName, value, count, onChange)
# Brightness range -255 to 255
cv2.createTrackbar('Brightness',
        'GEEK', 255, 2 * 255,
        BrightnessContrast)

# Contrast range -127 to 127
cv2.createTrackbar('Contrast', 'GEEK',
        127, 2 * 127,
        BrightnessContrast)


BrightnessContrast(0)

# The function waitKey waits for
# a key event infinitely or for delay
# milliseconds, when it is positive.
cv2.waitKey(0)
