import cv2
from PyQt6 import QtCore, QtWidgets, QtGui
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
	#output = QtCore.pyqtSignal(QtGui.QPixmap)
	output = QtCore.pyqtSignal(np.ndarray)
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

		video = cv2.VideoCapture(self.address)
		ret, array = video.read()
		
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

			ret = video.grab()

			skipCount +=1
			if skipCount > 9:
				skipCount = 0
			
			if skipCount < self.frameSkip: #skipping some frames to allow catch up
				continue 
			
			ret, array = video.retrieve()

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

			resize = cv2.resize(array,(self.monitorx,self.monitory))
			if self.useGain:
				resize = applyGain(resize,self.gain)
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

			'''
			totalbytes = resize.nbytes
			bpl = int(totalbytes/resize.shape[0])
			qarray = QtGui.QImage(resize.data, resize.shape[1],resize.shape[0], bpl, QtGui.QImage.Format.Format_BGR888)
			pixmap = QtGui.QPixmap.fromImage(qarray)
			self.output.emit(pixmap)
			'''
			self.output.emit(resize)
			
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

		video.release()
		print(f'fps: {totalFPS}')

	def stop(self):
		self.running = False
		print('stopping process')


class NewWindow(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.running = True
		self.layout = QtWidgets.QVBoxLayout()
		self.frame = QtWidgets.QLabel()
		self.layout.addWidget(self.frame)
		self.setLayout(self.layout)
		

class DummyWorker(QtCore.QObject):
	output = QtCore.pyqtSignal(QtGui.QPixmap)
	def __init__(self):
		super().__init__()
		self.running = True
	def run(self):
		timeout = time.time() + 10
		while time.time() < timeout and self.running:
			array = np.random.randint(0,255,(200,200), dtype=np.uint8)
			totalbytes = array.nbytes
			bpl = int(totalbytes/array.shape[0])
			qarray = QtGui.QImage(array.data, array.shape[1], array.shape[0], bpl, QtGui.QImage.Format.Format_Grayscale8)
			pixmap = QtGui.QPixmap.fromImage(qarray)
			self.output.emit(pixmap)

	def stop(self):
		self.running = False
