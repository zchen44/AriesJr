import imutils
import cv2
import os
import numpy as np

#colors in RBG format, backwards since numpy is backward so BGR
COLORS = {'purple': [255, 102, 221], 
		  'yellow_inner':[68, 221, 255],
		  'yellow_outer':[34, 238, 255]}

#load the image and try to detect rune inside image
path = os.getcwd() + '\\Screenshots\\arrows.bmp'
image = cv2.imread(path)

#purple = np.array(COLORS['purple'], dtype = "uint8")
#yellow_inner = np.array(COLORS['yellow_inner'], dtype = "uint8")
#yellow_outer = np.array(COLORS['yellow_outer'], dtype = "uint8")

#mask1 = cv2.inRange(image, purple, purple)
#x,y = np.where(mask1 == 255)
#rune = set(zip(x,y))

#center coordinate of rune
#rune_c = (int(np.mean(x)), int(np.mean(y)))

#mask2 = cv2.inRange(image, yellow_inner, yellow_inner)
#x,y = np.where(mask2 == 255)
#character = set(zip(x,y))

#center coordinate of character
#character_c = (int(np.mean(x)), int(np.mean(y)))

#isdisjoint returns True is the sets have no instersection
if (not rune.isdisjoint(character)):
	pass
mask3 = cv2.inRange(image, yellow_outer, yellow_outer)

#checks if any purple shows up
if (np.any(mask1)):
	pass

final_mask = cv2.bitwise_or(mask1,mask2)
final_mask = cv2.bitwise_or(final_mask,mask3)
result = cv2.bitwise_and(image, image, mask = final_mask)

cv2.imshow('hsvimage',np.hstack([image,result]))

cv2.waitKey(0)
cv2.destroyAllWindows()



