import win32gui
import cv2
import numpy as np
from mss import mss
 
COLORS = {'purple': [255, 102, 221, 255], 
		  'yellow_inner':[68, 221, 255, 255],
		  'yellow_outer':[34, 238, 255, 255]}

 
def _get_windows_bytitle(title_text, exact = False):
	def _window_callback(hwnd, all_windows):
		all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
	windows = []
	win32gui.EnumWindows(_window_callback, windows)
	if exact:
		return [hwnd for hwnd, title in windows if title_text == title]
	else:
		return [hwnd for hwnd, title in windows if title_text in title]
 
def record(hwnd = None, map = None):
	if not hwnd:
		hwnd=win32gui.GetDesktopWindow()

	if map == 'abc6':
		l,t,r,b=win32gui.GetWindowRect(hwnd)
		h = 87
		w = 137
		mon = {'top': t + 85, 'left': l + 10, 'width': 137, 'height': 87}
		pos_start = (10,85)
	else:
		l,t,r,b=win32gui.GetWindowRect(hwnd)
		h=b-t
		w=r-l
		pos_start = (0,0)

	win32gui.SetForegroundWindow(hwnd)
	time.sleep(.2) #lame way to allow screen to draw before taking shot

	purple = np.array(COLORS['purple'], dtype = "uint8")
	yellow_inner = np.array(COLORS['yellow_inner'], dtype = "uint8")
	yellow_outer = np.array(COLORS['yellow_outer'], dtype = "uint8")

	sct = mss()
	while(1):
		img = np.array(sct.grab(mon))

		mask1 = cv2.inRange(img, purple, purple)
		x,y = np.where(mask1 == 255)
		if (x.size != 0):
			Status.rune_flag = True
			Status.rune_coord = set(zip(x,y))
			#center coordinate of rune
			Status.rune_center = (int(np.mean(x)), int(np.mean(y)))
		else:
			Status.rune_flag = 0

		mask2 = cv2.inRange(img, yellow_inner, yellow_inner)

		mask3 = cv2.inRange(img, yellow_outer, yellow_outer)
		x,y = np.where(mask3 == 255)
		if (x.size != 0):
			Status.character_coord = set(zip(x,y))
			#center coordinate of character
			Status.character_center = (int(np.mean(x)), int(np.mean(y)))

		# print("Rune Center: ", Status.rune_center)
		# print("Character Center: ", Status.character_center)

		final_mask = cv2.bitwise_or(mask1,mask2)
		final_mask = cv2.bitwise_or(final_mask,mask3)
		result = cv2.bitwise_and(img, img, mask = final_mask)

		cv2.imshow('minimap + mask', np.hstack([img, result]))
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break

