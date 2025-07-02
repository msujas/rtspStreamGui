import cv2
from PyQt6 import QtCore
import numpy as np
import time
from datetime import datetime

def applyGain(array,gain):
	gainExtent=40
	maxGain = 2
	adjustedGain = gain/(gainExtent/maxGain)
	newarray = array*adjustedGain
	newarray = np.where(newarray > 255, 255, newarray).astype(np.uint8)
	return newarray

def aspectAdjust(monx,mony,apsect):
	if monx/mony <apsect: #adjusting the monitor x or y values based on the aspect ratio
		mony = int(monx/apsect)
	elif monx/mony > apsect:
		monx = int(mony*apsect)
	return monx, mony

class Worker(QtCore.QObject):
	def __init__(self,address:str, monitorx: int, monitory: int, gain: float,  screenwidth: int, frameSkip:int,
			  screenheight: int, crosssize: int, crossOffsetH: int, crossOffsetW: int, crossCheck: bool, linePosition: int, 
	imageTime: int, imageDir: str, record: bool = False, recordTime: int = 1, lineCheck: bool = True, useGain:bool = True):
		super(Worker,self).__init__()
		self.address = address
		self.monitorx = monitorx
		self.monitory = monitory
		self.frameSkip = frameSkip
		self.gain = gain
		self.screenwidth = screenwidth
		self.screenheight = screenheight
		self.crosssize = crosssize
		self.crossOffsetH = crossOffsetH
		self.crossOffsetW = crossOffsetW
		self.crossCheck = crossCheck
		self.running = True
		self.snapshot = False
		self.imageTime = imageTime
		self.imageSeries = False
		self.imageDir = imageDir
		self.record = record
		self.recordTime = recordTime
		self.linePosition = linePosition
		self.lineCheck = lineCheck
		self.useGain = useGain

	def run(self):
		import cv2
		tries = 0
		tries_max = 200
		sleep_time_secs = 5
		#self.gstAdress =  f"rtspsrc location={self.address} ! rtph265depay ! h265parse ! videoconvert ! appsink"
		video = cv2.VideoCapture(self.address)
		ret, array = video.read()
		#player = MediaPlayer(self.address)
		
		if ret == False:
			print('stream not found')
			return


		pixelFormats =	{'Mono8':1, 'Mono10':1, 'Mono10p':1, 'Mono10Packed':1, 'Mono12':1, 'Mono12p':1,
		'Mono12Packed':1, 'Mono16':1, 'BayerRG8':1, 'BayerRG10':1, 'BayerRG10p':1, 'BayerRG10Packed':1,
		'BayerRG12':1, 'BayerRG12p':1, 'BayerRG12Packed':1, 'BayerRG16':1, 'RGB8':3, 'BGR8':3, 'YCbCr8':3,
		'YCbCr8_CbYCr':3, 'YUV422_8':3, 'YUV422_8_UYVY':3, 'YCbCr411_8':3, 'YUV411_8_UYYVYY':3}

		self.height = array.shape[0]
		self.width = array.shape[1]
		self.aspect = self.width/self.height
		print(self.height,self.width)
		crossThickness = 4
		lineSize = 300
		lineThickness = 3


		self.monitorx,self.monitory = aspectAdjust(self.monitorx,self.monitory,self.aspect)

		curr_frame_time = 0
		prev_frame_time = 0

		cycletimes = np.array([])

		print(f'monitorx {self.monitorx}, monitory {self.monitory}')
		windowName = f'{self.address} (press stop to close)'
		cv2.namedWindow(windowName)
		cv2.moveWindow(windowName,self.screenwidth-self.monitorx - 20,self.screenheight - self.monitory-100)
		
		num_channels= 3#array.shape[2]
		if num_channels == 3:
			crossElement = np.array([0,0,255], dtype = np.uint8)
		elif num_channels == 1:
			crossElement = np.array([255],dtype = np.uint8)

		self.imageCountDown = 0

		skipCount = -1
		frameCount = 0
		t0 = time.time()
		fpsCheckCount = 0
		totalFPS = 0
		while self.running:
			# Used to display FPS on stream
			curr_frame_time = time.time()

			#array = np.random.randint(0,255,size=(500,800,3),dtype = np.uint8)

			ret = video.grab()

			#ret, array = video.read()
			skipCount +=1
			if skipCount > 9:
				skipCount = 0
			
			if skipCount < self.frameSkip: #skipping some frames to allow catch up
				continue 
			
			#skipCount = 0
			ret, array = video.retrieve()

			#frame, val = player.get_frame()
			'''
			if frame is None:
				time.sleep(0.01)
				continue
			img, t = frame
			
			array = np.asarray(list(img.to_bytearray()[0])).reshape(self.height,self.width,3).astype(np.uint8)
			array = array[:,:,::-1] #swap from rgb to bgr
			'''
			
			"""
			Create a reshaped NumPy array to display using OpenCV
			"""
			#npndarray = np.ndarray(buffer=array, dtype=np.uint8, shape=(item.height, item.width, num_channels)) # buffer_bytes_per_pixel))
			#npndarray = np.where(cross == True, crossElement, npndarray)

			if self.crossCheck:
				array[self.crossOffsetH + int(self.height/2-(crossThickness-1)/2+1): self.crossOffsetH + int(self.height/2+(crossThickness-1)/2),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+ int(self.width/2+self.crosssize/2)] = crossElement #middle horizontal

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2 - crossThickness/2 +1): self.crossOffsetW+int(self.width/2 + crossThickness/2)] = crossElement #middle vertical

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+int(self.width/2-self.crosssize/2 + 1 + crossThickness)] = crossElement #left vertical

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2+self.crosssize/2-crossThickness):  self.crossOffsetW+int(self.width/2+self.crosssize/2)] = crossElement #right vertical

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2-self.crosssize/2 + crossThickness+1),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+int(self.width/2+self.crosssize/2)] = crossElement #lower horizontal

				array[self.crossOffsetH + int(self.height/2+self.crosssize/2-crossThickness):  self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+int(self.width/2+self.crosssize/2)] = crossElement #upper horizontal
			if self.lineCheck:
				array[self.linePosition:self.linePosition+lineThickness,self.crossOffsetW+ int(self.width/2-lineSize/2 + 1):self.crossOffsetW+ int(self.width/2+lineSize/2)] = crossElement
			#fps = str(1/(curr_frame_time - prev_frame_time))
			resize = cv2.resize(array,(self.monitorx,self.monitory))
			if self.useGain:
				resize = applyGain(resize,self.gain)
			#cv2.putText(resize, fps,textpos, cv2.FONT_HERSHEY_SIMPLEX, textsize, (100, 255, 0), 3, cv2.LINE_AA)
			if self.snapshot:
				dt = datetime.fromtimestamp(time.time())
				filename = f'{self.imageDir}/{dt.day:02d}_{dt.month:02d}_{dt.year}_{dt.hour:02d}{dt.minute:02d}{dt.second:02d}.png'
				cv2.imwrite(filename, resize)
				self.snapshot = False
			if self.imageSeries:
				currentTime = time.time()
				if currentTime - self.imageCountDown >= self.imageTime:
					dt = datetime.fromtimestamp(time.time())
					filename = f'{self.imageDir}/{dt.day:02d}_{dt.month:02d}_{dt.year}_{dt.hour:02d}{dt.minute:02d}{dt.second:02d}.png'
					cv2.imwrite(filename, resize)
					self.imageCountDown = time.time()

			cv2.imshow(windowName,resize)
			
			frameCount += 1
			if frameCount == 100: #checking the fps every 100 frames
				frameCount = 0
				t100 = time.time()
				
				fps = 100/(t100-t0)
				t0 = time.time()
				if fpsCheckCount == 0:
					totalFPS = fps
				else:
					totalFPS = (totalFPS*fpsCheckCount + fps)/(fpsCheckCount+1)
				fpsCheckCount += 1
			prev_frame_time = curr_frame_time


			"""
			Break if esc key is pressed
			"""

			key = cv2.waitKey(1)
			if key == 27:
				break
		
		cv2.destroyAllWindows()
		video.release()
		#del video
		#system.destroy_device()
		#print(1/np.average(buffertimes))
		#cycletimes = cycletimes[1:]
		#print(f'fps = {1/np.average(cycletimes)}, standard deviation = {np.std(1/cycletimes)}')
		print(f'fps: {totalFPS}')
		#self.terminate()
		return

	def stop(self):
		self.running = False
		print('stopping process')
		#self.terminate()