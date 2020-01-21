from pynput import keyboard
from tqdm import tqdm
import keybinding as key
import time
import threading
import sys
import win32gui
import cv2
import numpy as np
from mss import mss

KISHINKEY = 'v'
ATTACK_KEY = 'y'
HAYATO_ATTACK_KEY = 's'
DANKUUSEN = 'f'
JUMP = 'd'
INFERNAL_CONCUSSION = 'c'

# RGB with last 255 just meaning True
COLORS = {'purple': [255, 102, 221, 255], 
		  'yellow_inner': [68, 221, 255, 255],
		  'yellow_outer': [34, 238, 255, 255],
		  'outer_green': [0,255,0,255],
		  'inner_green': [0,221,0,255],
		  'corner_green': [17,187,17,255]}

MAPS = {'abc6': [85,10,137,87],
		'mp': [90,15,151,53],
		's1': [105,30,180,59],
		's2': [95,60,110,77],
		's3': [95,30,140,59],
		's4': [95,60,87,78],
		's5': [95,60,96,80],
		's6': [115,45,102,59],
		'max_mp': [80,15,195,80],
		'hrm': [87,11,182,50]}

# The key combination to check to pause and unpause (CTRL + P)
COMBINATION = {keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('p')}
DIRECTIONS = {True: 'left_arrow', 
			  False: 'right_arrow', 
			  'left': 'left_arrow',
			  'right': 'right_arrow',
			  'down': 'down_arrow',
			  'up': 'up_arrow'}

# The currently active modifiers
current = set()

# Begins with the script paused
class Status:
	_exit = False
	paused = True
	buff_duration = 145
	buff_counter = 145		# Intialized to equal buff_duration to trigger cold start
	demon_counter = 0		# 30 secondish loot cycle with 5 minute reposition cycle
	reposition_counter = 63
	dir_flag = True
	script_type = None
	cold_start = True
	rune_flag = False
	mp_farm_flag = False
	rune_coord = ()
	rune_center= ()
	character_coord = ()
	character_center = ()
	npc_center = ()
	stage = 0
	map = 'abc6'

	 
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

	l,t,r,b=win32gui.GetWindowRect(hwnd)
	h=b-t
	w=r-l
	mon = {'top': t, 'left': l, 'width': 10, 'height': 10}

	#pos_start = (0,0)

	win32gui.SetForegroundWindow(hwnd)
	time.sleep(.2) #lame way to allow screen to draw before taking shot

	purple = np.array(COLORS['purple'], dtype = "uint8")
	yellow_inner = np.array(COLORS['yellow_inner'], dtype = "uint8")
	yellow_outer = np.array(COLORS['yellow_outer'], dtype = "uint8")
	outer_green = np.array(COLORS['outer_green'], dtype = "uint8")
	inner_green = np.array(COLORS['inner_green'], dtype = "uint8")
	corner_green = np.array(COLORS['corner_green'], dtype = "uint8")

	sct = mss()
	prev = '' #defaults at ab6
	while(1):

		if Status.script_type == 'h':
			Status.mp_farm_flag = True
			Status.map = 'max_mp'
		##if Status.mp_farm_flag:
		#if Status.stage == 1:
		#	Status.map = 's1'
		#elif Status.stage == 2:
		#	Status.map = 's2'
		#elif Status.stage == 3:
		#	Status.map = 's3'
		#elif Status.stage == 4:
		#	Status.map = 's4'
		#elif Status.stage == 5:
		#	Status.map = 's5'
		#elif Status.stage == 6:
		#	Status.map = 's6'
		#else:
		#	Status.map = 'mp'

		#Grabs the dimensions of the minimap if it changes
		if prev != Status.map:
			prev = Status.map
			dimensions = MAPS[Status.map] # list where [top, left, width, height] is recorded
			mon = {'top': t + dimensions[0], 'left': l + dimensions[1], 'width': dimensions[2], 'height': dimensions[3]}

		img = np.array(sct.grab(mon))

		mask1 = cv2.inRange(img, purple, purple)
		y,x = np.where(mask1 == 255)
		if (x.size != 0):
			Status.rune_flag = True
			Status.rune_coord = tuple(zip(x,y))
			#center coordinate of rune
			Status.rune_center = (int(np.mean(x)), int(np.mean(y)))
		else:
			Status.rune_flag = False
			Status.rune_center = ()
			Status.rune_coord = ()

		mask2 = cv2.inRange(img, yellow_inner, yellow_inner)
		mask3 = cv2.inRange(img, yellow_outer, yellow_outer)
		cy, cx = np.where(mask3 == 255) #changed so it reflects x and y axis. Default is len by width so y by x originally.
		#case where character center is detected
		if (cx.size != 0):
			Status.character_coord = tuple(zip(cx,cy))
			#center coordinate of character
			Status.character_center = (int(np.mean(cx)), int(np.mean(cy)))
		#case when not so used when character changes maps
		elif (cx.size == 0) and (Status.character_center != (-1,-1)):
			Status.character_center = (-1,-1)
			Status.stage = (Status.stage + 1) % 7

		#print("Character center: " + str(Status.character_center))
		#if (Status.character_center)
		
		mask4 = cv2.inRange(img, outer_green, outer_green)
		mask5 = cv2.inRange(img, corner_green, corner_green)
		mask6 = cv2.inRange(img, inner_green, inner_green)
		npcy, npcx = np.where(mask6 == 255) 
		if (npcx.size != 0):
			Status.character_coord = tuple(zip(npcx,npcy))
			#center coordinate of NPCs (used as map identifier)
			Status.npc_center = (int(np.mean(npcx)), int(np.mean(npcy)))

		final_mask = cv2.bitwise_or(mask1,mask2)
		final_mask = cv2.bitwise_or(final_mask,mask3)
		final_mask = cv2.bitwise_or(final_mask,mask4)
		final_mask = cv2.bitwise_or(final_mask,mask5)
		final_mask = cv2.bitwise_or(final_mask,mask6)
		result = cv2.bitwise_and(img, img, mask = final_mask)

		cv2.imshow('minimap + mask', np.hstack([img, result]))
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break


# Imitates a key press
def keyPress(intent, duration=0.03):
	key.KeyDown(key.VK_CODE[intent])
	time.sleep(duration)
	key.KeyUp(key.VK_CODE[intent])

def jump(dir='left',duration=0.2):
	key.KeyDown(key.VK_CODE[DIRECTIONS[dir]])
	key.KeyDown(key.VK_CODE[JUMP])
	time.sleep(duration)
	key.KeyUp(key.VK_CODE[DIRECTIONS[dir]])
	key.KeyUp(key.VK_CODE[JUMP])

# A more complex go to position function using coordinates obtained from minimap + computer vision + color masking
def goToCoordinates(coord, demon = False, fj2 = False):
	check_X = False
	check_Y = False
	prev_dis_y = -1
	check_X = Status.character_center[0] in range((coord[0]-2), (coord[0]+3)) # 4 pixel leeway
	check_Y = Status.character_center[1] in range((coord[1]-3), (coord[1]+3)) # 6 pixel leeway
	while(not(check_X and check_Y)):
		prev_dis = -1
		counter = 0
		if(not check_X): #do horizontal positioning first
			if(Status.character_center[0] < coord[0]):
				#character model is left of the target
				print("LEFT OF TARGET!!!")
				checkLX = Status.character_center[0] in range((coord[0]-2), (coord[0]+3))
				while(not(checkLX)):
					distance = coord[0]-Status.character_center[0]
					print("Left Distance: %d Previous Distance: %d" % (distance, prev_dis))
					if (distance == prev_dis) and (counter >= 25):
						print("gonnna jump left")
						jump('left')
					prev_dis = distance
					counter += 1
					if (demon):
						if distance > 62:
							demonGlide('right', 2)
						elif distance > 54:
							demonGlide('right', 1.5)
						elif distance > 42:
							demonGlide('right', 1)
						elif distance > 28:
							demonGlide('right', 0.5)
						elif distance > 21:
							demonGlide('right', 0.4, 0.1)
						elif distance > 17:
							demonGlide('right', 0.2, 0.1)
						elif distance < 0:
							break
						else:
							prev_dis = distance
							key.KeyDown(key.VK_CODE[DIRECTIONS['right']])
							while(not(Status.character_center[0] in range((coord[0]-2), (coord[0]+3)))):
								time.sleep(0.1)
								distance = coord[0]-Status.character_center[0]
								print("Left Distance in walking!: %d Previous Distance: %d" % (distance, prev_dis))
								if distance == prev_dis:
									key.KeyUp(key.VK_CODE[DIRECTIONS['right']])
									print("breaking")
									break
							key.KeyUp(key.VK_CODE[DIRECTIONS['right']])
					elif fj2:
						if distance > 33:
							doubleFlashJump('right')
						elif distance > 27:
							singleFlashJump('right')
						else:
							key.KeyDown(key.VK_CODE[DIRECTIONS['right']])
							while(not(Status.character_center[0] in range((coord[0]-2), (coord[0]+3)))):
								time.sleep(0.1)
								#distance = coord[0]-Status.character_center[0]
								#if distance == prev_dis:
								#	key.KeyUp(key.VK_CODE[DIRECTIONS['right']])
								#	break
							key.KeyUp(key.VK_CODE[DIRECTIONS['right']])
							time.sleep(0.6)
							checkLX = True
							continue
					else:
						key.KeyDown(key.VK_CODE[DIRECTIONS['right']])
						while(not(Status.character_center[0] in range((coord[0]-2), (coord[0]+3)))):
							time.sleep(0.01)
							distance = coord[0]-Status.character_center[0]
							if distance == prev_dis:
								key.KeyUp(key.VK_CODE[DIRECTIONS['right']])
								break
						key.KeyUp(key.VK_CODE[DIRECTIONS['right']])
					checkLX = Status.character_center[0] in range((coord[0]-2), (coord[0]+3))
			elif(Status.character_center[0] > coord[0]):
				#character model is right of target
				checkRX = Status.character_center[0] in range((coord[0]-2), (coord[0]+3))
				while(not(checkRX)):
					distance = Status.character_center[0] - coord[0]
					print(" Right Distance: %d Previous Distance: %d" % (distance, prev_dis))
					if (distance == prev_dis) and (counter >= 25):
						print("gonnna jump right")
						jump('right')
					prev_dis = distance
					counter += 1
					if (demon):
						if distance > 62:
							demonGlide('left', 2)
						elif distance > 54:
							demonGlide('left', 1.5)
						elif distance > 42:
							demonGlide('left', 1)
						elif distance > 28:
							demonGlide('left', 0.5)
						elif distance > 21:
							demonGlide('left', 0.4, 0.1)
						elif distance > 17:
							demonGlide('left', 0.2, 0.1)
						elif distance < 0:
							break
						else:
							key.KeyDown(key.VK_CODE[DIRECTIONS['left']])
							while(not(Status.character_center[0] in range((coord[0]-2), (coord[0]+3)))): #changed from 2 to 5
								time.sleep(0.1)
								distance = Status.character_center[0] - coord[0]
								if distance == prev_dis:
									key.KeyUp(key.VK_CODE[DIRECTIONS['left']])
									break
							key.KeyUp(key.VK_CODE[DIRECTIONS['left']])
					elif fj2:
						if distance > 33:
							doubleFlashJump('left')
						elif distance > 27:
							singleFlashJump('left')
						else:
							key.KeyDown(key.VK_CODE[DIRECTIONS['left']])
							while(not(Status.character_center[0] in range((coord[0]-2), (coord[0]+3)))):
								time.sleep(0.01)
								#distance = coord[0]-Status.character_center[0]
								#if distance == prev_dis:
								#	print("DISTANCE IS THE FUCKING SAME NOW!!!!!!")
								#	key.KeyUp(key.VK_CODE[DIRECTIONS['left']])
								#	break
							key.KeyUp(key.VK_CODE[DIRECTIONS['left']])
							time.sleep(0.6)
							checkRX = True
							continue
					else:
						key.KeyDown(key.VK_CODE[DIRECTIONS['left']])
						while(not(Status.character_center[0] in range((coord[0]-2), (coord[0]+3)))):
							time.sleep(0.1)
							distance = Status.character_center[0] - coord[0]
							if distance == prev_dis:
								key.KeyUp(key.VK_CODE[DIRECTIONS['left']])
								break
						key.KeyUp(key.VK_CODE[DIRECTIONS['left']])
						time.sleep(0.6)
						checkRX = True
						continue
					checkRX = Status.character_center[0] in range((coord[0]-2), (coord[0]+3))
		elif(not check_Y): #do vertical positioning next
			if(Status.character_center[1] > coord[1]):
				#character model is below the target
				distance = Status.character_center[1] - coord[1]
				counter += 1
				print("Distance Vertical: %d Previous Distance Vertical: %d : Counter %d" % (distance, prev_dis_y,counter))
				if (distance == prev_dis_y) and (counter >= 25):
					keyPress('up_arrow',3)
					counter = 0
				elif(demon):
					#if distance > 25:
					demonVertJump('long')
					#elif distance > 22:
					#	demonVertJump('med')
					#elif distance > 12:
					#	demonVertJump('short')
				elif(fj2):
					if distance < 28:
						jump('up')
						keyPress('left_shift')
						time.sleep(0.85)
					elif distance < 37:
						jump('up')
						keyPress('left_shift')
						keyPress('v')
						time.sleep(0.85)
					else:
						return
				prev_dis_y = distance
			elif(Status.character_center[1] < coord[1]):
				jump('down',1)

		#check position again for next iteration
		check_X = Status.character_center[0] in range((coord[0]-2), (coord[0]+3)) # 4 pixel leeway
		check_Y = Status.character_center[1] in range((coord[1]-3), (coord[1]+3)) # 4 pixel leeway

	if fj2:
		while(Status.character_center[0] != coord[0]):
			dis = Status.character_center[0] - coord[0]
			if dis < 0:
				go = 'right'
			else:
				go = 'left'
			for x in range(abs(dis)):
				keyPress(DIRECTIONS[go],0.08)
				time.sleep(0.2)


# The Demon gliding, optional param for length of glide (defaults at 2s)
def demonGlide(dir='right', duration=2, jump_dur=0.2):
	key.KeyDown(key.VK_CODE[DIRECTIONS[dir]])
	keyPress(JUMP)
	time.sleep(jump_dur)
	key.KeyDown(key.VK_CODE[JUMP])
	time.sleep(duration)
	key.KeyUp(key.VK_CODE[JUMP])
	key.KeyUp(key.VK_CODE[DIRECTIONS[dir]])

# The Demon vertical jump, optional param for height of jump (defaults as max range jump)
def demonVertJump(range='long'):
	height={'long':0.2, 'med':0.2,'short':0.4}
	keyPress(JUMP)
	time.sleep(height[range])
	keyPress('up_arrow')
	keyPress('up_arrow')

# Loot cycle instructions
def demonLootCycle():
	if(Status.map == 'abc6'):
			goToCoordinates((96,67), demon = True)
			time.sleep(0.1)
			goToCoordinates((96,48), demon = True)
			time.sleep(0.1)
			goToCoordinates((31,48), demon = True)
			time.sleep(0.1)
			goToCoordinates((31,67), demon = True)
			time.sleep(0.4)

def demonReposition(map='abc6'):
	if(map == 'abc6'):
		jump('left') # In case you're on rope for some reason
		time.sleep(1)
		demonGlide('left', 2.5)
		time.sleep(1)
		demonGlide('right',1.1)
		time.sleep(1)

def demonAttackCycle():
	if(Status.map == 'abc6'):
		for x in range(3):
			goToCoordinates((53,67), demon = True)
			for y in range(2):
				keyPress(INFERNAL_CONCUSSION)
				time.sleep(0.90)
			goToCoordinates((76,67), demon = True)
			time.sleep(0.1)
			for y in range(2):
				keyPress(INFERNAL_CONCUSSION)
				time.sleep(0.90)
			goToCoordinates((53,67), demon = True)
			keyPress(INFERNAL_CONCUSSION)
			time.sleep(3)
		goToCoordinates((53,67), demon = True)
		for y in range(4):
			keyPress(INFERNAL_CONCUSSION)
			time.sleep(0.90)
		goToCoordinates((76,67), demon = True)
		time.sleep(0.1)
		keyPress(INFERNAL_CONCUSSION)
		time.sleep(0.90)
		keyPress(INFERNAL_CONCUSSION)

def demonEntireCycle():
	tqdm.write("\nNow starting Demon Slayer Farming Mode")
	tqdm.write("Starting the script. Script will begin paused.")
	tqdm.write("Press CTRL + P to unpause/pause the script and ESC to terminate the script.")
	if(Status.map == 'abc6'):
		while(not Status._exit):
			while (Status.paused and not Status._exit):
				time.sleep(0.3)
				continue
			
			if (Status.cold_start):
				#Status.demon_counter = Status.reposition_counter
				time.sleep(3) # Gives you 3 seconds to get your hand off of CTRL + P so those don't register
				tqdm.write("Loot cycles at 30 & 60")
				Status.cold_start = False

			#TODO: gotoposition 
			if (Status.rune_flag):
				pass

			demonAttackCycle()
			demonLootCycle()
			#if(Status.demon_counter == Status.reposition_counter):
			#	if (not Status.cold_start):
			#		pbar.close()
			#	pbar = tqdm(total=Status.reposition_counter, initial=0, position=0, leave=False)
			#	demonReposition('abc6')
			#	Status.demon_counter = 0
			#	Status.cold_start = False
			#elif((Status.demon_counter % 30) == 0):
			#	demonLootCycle('abc6')
			#else:
			#	demonAttackCycle()

			#Status.demon_counter += 3
			#pbar.update(3)


# Kishin Looping done here
def kishinLoop():
	tqdm.write("\nNow starting Kanna Kishin Mode")
	tqdm.write("Starting the script. Script will begin paused.")
	tqdm.write("Press CTRL + P to unpause/pause the script and ESC to terminate the script.")
	while(not Status._exit):
		while (Status.paused and not Status._exit):
			continue

		if (Status.buff_counter == Status.buff_duration):
			if(Status.cold_start):
				time.sleep(3) # Gives you 3 seconds to get your hand off of CTRL + P so those don't register
			print("\nKishin Shoukan casted at %s" % time.strftime('%x %X %Z'))
			key.KeyDown(key.VK_CODE[KISHINKEY])
			time.sleep(0.03)
			key.KeyUp(key.VK_CODE[KISHINKEY])
			Status.buff_counter = 0
			if (not Status.cold_start):
				pbar.close()
			pbar = tqdm(total=Status.buff_duration, initial=0)
			Status.cold_start = False


		# Moves back and forth and attacks every 12 seconds
		elif( (Status.buff_counter % 12) == 0):
			key.KeyDown(key.VK_CODE[DIRECTIONS[Status.dir_flag]])
			time.sleep(0.03)
			key.KeyUp(key.VK_CODE[DIRECTIONS[Status.dir_flag]])
			key.KeyDown(key.VK_CODE[ATTACK_KEY])
			time.sleep(0.03)
			key.KeyUp(key.VK_CODE[ATTACK_KEY])
			Status.dir_flag = not Status.dir_flag

		Status.buff_counter += 1
		pbar.update(1)
		time.sleep(1)

# Adds the key to the set for combination check. Esc will just stop script
def onKeyPress(key):
	if key in COMBINATION:
		current.add(key)
		if all(k in current for k in COMBINATION):
			if(Status.paused):
				print("All modifiers active. Script is now UNPAUSED and buffer counter will reset.")
				Status.buff_counter = Status.buff_duration
				Status.demon_counter = Status.reposition_counter
				Status.switch_screen = True
			else:
				print("\nAll modifiers active. Script is now PAUSED.")
			Status.paused = not Status.paused
	elif(key == keyboard.KeyCode.from_char('k')):
		Status.script_type = 'k'
	elif(key == keyboard.KeyCode.from_char('d')):
		Status.script_type = 'd'
	elif(key == keyboard.KeyCode.from_char('h')):
		Status.script_type = 'h'
	elif(key == keyboard.KeyCode.from_char('j')):
		Status.script_type = 'j'
	elif (key == keyboard.Key.esc):
		tqdm.write("Program is terminating. Please wait...")
		Status._exit = not Status._exit

# Remove keys from set once released to prevent corrupted future checks
def onKeyRelease(key):
	try:
		current.remove(key)
	except KeyError:
		pass

def doubleFlashJump(dir = 'left'):
	key.KeyDown(key.VK_CODE[DIRECTIONS[dir]])
	keyPress(JUMP)
	time.sleep(0.2)
	keyPress(JUMP)
	time.sleep(0.1)
	keyPress(JUMP)
	key.KeyUp(key.VK_CODE[DIRECTIONS[dir]])
	time.sleep(0.8)

def singleFlashJump(dir = 'left'):
	key.KeyDown(key.VK_CODE[DIRECTIONS[dir]])
	keyPress(JUMP)
	time.sleep(0.2)
	keyPress(JUMP)
	key.KeyUp(key.VK_CODE[DIRECTIONS[dir]])
	time.sleep(0.7)

def hayatoSingleC():
	keyPress(DANKUUSEN)
	keyPress(HAYATO_ATTACK_KEY)
	time.sleep(0.85) #bare minimum is 0.8 to execute

def hayatoFullCycle():
	tqdm.write("\nNow starting Hayato Monster Park Farming Mode")
	tqdm.write("Starting the script. Script will begin paused.")
	tqdm.write("Press CTRL + P to unpause/pause the script and ESC to terminate the script.")
	Status.map = 'mp'
	time.sleep(0.03)
	Status.stage = 0
	while(1):
		if Status.stage == 0:
			keyPress('2')
			time.sleep(1)
			#singleFlashJump('right')
			#goToCoordinates((112,32), fj2 = True) old stuff
			goToCoordinates((112,42), fj2 = True)
			for x in range(3):
				keyPress(DIRECTIONS['up'])
			time.sleep(0.6)
			for x in range(5):
				keyPress(DIRECTIONS['down'])
			keyPress('spacebar')
			time.sleep(2.5)
		if Status.stage == 1:
			keyPress(DIRECTIONS['right'])
			for x in range(6):
				hayatoSingleC()
			#s1 start at (5,38) finish at (157,34)
			time.sleep(0.6)
			#singleFlashJump('left')
			#goToCoordinates((157,34), fj2 = True)
			goToCoordinates((172,59), fj2 = True)
			keyPress(DIRECTIONS['up'])
			time.sleep(2.5)
			if Status.stage == 1:
				goToCoordinates((33,63), fj2 = True)
		if Status.stage == 2:
			keyPress(DIRECTIONS['right'], 0.2)
			for x in range(3):
				hayatoSingleC()
			keyPress('left_shift')
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.5)
			keyPress(DIRECTIONS['left'],0.5)
			for x in range(2):
				hayatoSingleC()
			keyPress(JUMP,0.2)
			keyPress('v')
			hayatoSingleC()
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.85)
			#singleFlashJump('left')
			#goToCoordinates((16,22), fj2 = True)
			goToCoordinates((62,37), fj2 = True)
			keyPress(DIRECTIONS['up'])
			time.sleep(2.5)
			if Status.stage == 2:
				goToCoordinates((57,70), fj2 = True)
		if Status.stage == 3:
			keyPress(DIRECTIONS['right'], 0.2)
			for x in range(3):
				hayatoSingleC()
			keyPress('alt')
			time.sleep(1.6)
			hayatoSingleC()
			#goToCoordinates((127, 38), fj2 = True)
			goToCoordinates((142, 53), fj2 = True)
			keyPress(DIRECTIONS['up'])
			time.sleep(2.5)
			if Status.stage == 3:
				goToCoordinates((19,46), fj2 = True)
		if Status.stage == 4:
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.85)
			keyPress(DIRECTIONS['left'])
			for x in range(3):
				hayatoSingleC()
			keyPress('left_shift')
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.4)
			keyPress(DIRECTIONS['right'],0.4)
			for x in range(2):
				hayatoSingleC()
			keyPress('left_shift')
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.85)
			keyPress(DIRECTIONS['left'],0.4)
			hayatoSingleC()
			#goToCoordinates((71, 12), fj2 = True)
			goToCoordinates((116, 27), fj2 = True)
			keyPress(DIRECTIONS['up']) 
			time.sleep(2.5)
			if Status.stage == 4:
				goToCoordinates((110,72), fj2 = True)
		if Status.stage == 5:
			keyPress(DIRECTIONS['right'],0.2)
			for x in range(3):
				hayatoSingleC()
			keyPress(DIRECTIONS['left'],0.2)
			keyPress('left_shift')
			keyPress('v')
			for x in range(2):
				hayatoSingleC()
			time.sleep(0.5)
			keyPress('left_shift')
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.85)
			keyPress(DIRECTIONS['right'],0.2)
			for x in range(2):
				hayatoSingleC()
			#singleFlashJump('left')
			#goToCoordinates((66, 15), fj2 = True)
			goToCoordinates((111, 30), fj2 = True)
			keyPress(DIRECTIONS['up']) 
			time.sleep(2.5)
			if Status.stage == 5:
				goToCoordinates((60,74), fj2 = True)
				keyPress(HAYATO_ATTACK_KEY)
				time.sleep(0.85)
		if Status.stage == 6:
			keyPress(DIRECTIONS['right'],0.2)
			for x in range(3):
				hayatoSingleC()
			keyPress(DIRECTIONS['left'],0.1)
			keyPress('left_shift')
			keyPress('v')
			for x in range(3):
				hayatoSingleC()
			jump('down', 1.5)
			keyPress(DIRECTIONS['right'],0.1)
			for x in range(3):
				hayatoSingleC()
			#singleFlashJump('left')
			#goToCoordinates((87,39), fj2 = True)
			goToCoordinates((117,74), fj2 = True)
			keyPress(DIRECTIONS['up']) 
			time.sleep(2.5)
			if Status.stage == 6:
				goToCoordinates((40, 74), fj2 = True)
				keyPress(HAYATO_ATTACK_KEY)
				time.sleep(0.85)

def hayatoTicketFarm():
	Status.map = 'hrm'
	time.sleep(0.03)
	while(1):
		if( Status.character_center[0] in range(1,9)):
			keyPress(DIRECTIONS['right'],0.2)
			keyPress('left_shift')
			keyPress(HAYATO_ATTACK_KEY)
			time.sleep(0.85)
		elif( Status.character_center[0] in range(170,179)):
			keyPress(DIRECTIONS['left'],0.3)
			jump('down')
			time.sleep(0.2)
			while(not(Status.character_center[1] in range(26,38))):
				jump('down')
		hayatoSingleC()
# Uses multithreading listener to detect a specific keyboard interrupt to pause or stop loop. Structured for future optional scripting
def main():

	tqdm.write("Welcome to Raymond's little project in development: V3\n")
	tqdm.write("Press\n'k' for Kanna Kishin\n'd' for Demon Slayer Farming\n'h' for Hayato Monster Park")


	listening_thread = keyboard.Listener(on_press = onKeyPress,
										on_release = onKeyRelease)
	listening_thread.start()

	window_handle = _get_windows_bytitle("MapleStory")[0]
	t1 = threading.Thread(target=record, args=(window_handle,))
	# position of portal is (112,32) in Monster Park
	t1.start()
	time.sleep(2)

	while(not Status._exit):
		if(Status.script_type == 'k'):
			kishinLoop()
		elif(Status.script_type == 'd'):
			demonEntireCycle('abc6')
		elif(Status.script_type == 'h'):
			hayatoFullCycle()
		elif(Status.script_type == 'j'):
			hayatoTicketFarm()

	#Status.map = 'abc6'
	#while(1):
	#	demonEntireCycle()

	keyboard.Listener.stop(listening_thread)
	tqdm.write("Stopped Listening")
	t1.join()

	sys.exit(0)

if __name__ == "__main__":
	main()