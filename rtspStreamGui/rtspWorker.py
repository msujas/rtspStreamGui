import cv2
from PyQt6 import QtCore, QtWidgets, QtGui
import numpy as np
import time
from datetime import datetime
import math

def applyGain(array,gain):
	gainExtent=40
	maxGain = 2
	adjustedGain = gain/(gainExtent/maxGain)
	newarray = array*adjustedGain
	newarray = np.where(newarray > 255, 255, newarray).astype(np.uint8)
	return newarray

def aspectAdjust(monx,mony,imageapsect):
	if monx/mony <imageapsect: #adjusting the monitor x or y values based on the aspect ratio
		mony = int(monx/imageapsect)
	elif monx/mony > imageapsect:
		monx = int(mony*imageapsect)
	return monx, mony

class Worker(QtCore.QObject):
	#output = QtCore.pyqtSignal(QtGui.QPixmap)
	output = QtCore.pyqtSignal(np.ndarray)
	streamNotFound = QtCore.pyqtSignal()
	def __init__(self,address:str, monitorx: int, monitory: int, gain: float,  screenwidth: int, frameSkip:int,
			  screenheight: int, crosssize: int, crossOffsetH: int, crossOffsetW: int, crossCheck: bool, linePosition: int, 
	imageTime: int, imageDir: str, record: bool = False, recordTime: int = 1, lineCheck: bool = True, useGain:bool = True,
	lineangle:float = 0, linethickness:int = 3, linelength:int = 300):
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
		self.lineangle = lineangle
		self.linethickness = linethickness
		self.linelength = linelength

	def run(self):
		import cv2
		tries = 0
		tries_max = 200
		sleep_time_secs = 5

		video = cv2.VideoCapture(self.address)
		ret, array = video.read()
		
		if ret == False:
			video.release()
			print('stream not found')
			self.streamNotFound.emit()
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

		self.monitorx,self.monitory = aspectAdjust(self.monitorx,self.monitory,self.aspect)

		curr_frame_time = 0
		prev_frame_time = 0

		cycletimes = np.array([])

		print(f'monitorx {self.monitorx}, monitory {self.monitory}')

		num_channels= 3#array.shape[2]
		if num_channels == 3:
			self.crossElement = np.array([0,0,255], dtype = np.uint8)
		elif num_channels == 1:
			self.crossElement = np.array([255],dtype = np.uint8)

		self.imageCountDown = 0

		skipCount = -1
		frameCount = 0
		t0 = time.time()
		fpsCheckCount = 0
		totalFPS = 0
		self.yoffset = int(self.crossOffsetH +self.height/2)
		self.xoffset = int(self.crossOffsetW + self.width/2)
		while self.running:

			ret = video.grab()

			skipCount +=1
			skipCount = skipCount%10 #resets skipCount to 0 when it reaches 10
			
			if skipCount < self.frameSkip: #skipping some frames to allow catch up
				continue 
			
			ret, array = video.retrieve()

			if self.crossCheck:
				array[self.crossOffsetH + int(self.height/2-(crossThickness-1)/2+1): self.crossOffsetH + int(self.height/2+(crossThickness-1)/2),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+ int(self.width/2+self.crosssize/2)] = self.crossElement #middle horizontal

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2 - crossThickness/2 +1): self.crossOffsetW+int(self.width/2 + crossThickness/2)] = self.crossElement #middle vertical

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+int(self.width/2-self.crosssize/2 + 1 + crossThickness)] = self.crossElement #left vertical

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2+self.crosssize/2-crossThickness):  self.crossOffsetW+int(self.width/2+self.crosssize/2)] = self.crossElement #right vertical

				array[self.crossOffsetH + int(self.height/2-self.crosssize/2 + 1):self.crossOffsetH + int(self.height/2-self.crosssize/2 + crossThickness+1),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+int(self.width/2+self.crosssize/2)] = self.crossElement #lower horizontal

				array[self.crossOffsetH + int(self.height/2+self.crosssize/2-crossThickness):  self.crossOffsetH + int(self.height/2+self.crosssize/2),
				self.crossOffsetW+ int(self.width/2-self.crosssize/2 + 1):self.crossOffsetW+int(self.width/2+self.crosssize/2)] = self.crossElement #upper horizontal
			if self.lineCheck:
				self.yoffset = int(self.crossOffsetH +self.height/2)
				self.xoffset = int(self.crossOffsetW + self.width/2)
				array = self.drawline(array,self.linePosition, self.xoffset,self.linelength, self.lineangle, self.linethickness)
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

	def drawline(self,array:np.ndarray, ycenter:int, xcenter:int, size:int, angle:float =0, thickness=3):

		angler = angle * math.pi / 180
		c = -xcenter*math.tan(angler) + ycenter
		m = np.tan(angler)

		if abs(angle) > 45:
			sign = int((angle > 0)*2-1)
			linestarty = int(ycenter -(size/2)*math.sin(angler))
			lineendy = int(ycenter + (size/2)*math.sin(angler))
			y2 = np.arange(linestarty, lineendy+1, sign,dtype = np.int16)
			x2 = np.astype((y2 - c)/m, np.int16)
			
			for n in range(thickness):
				i = int(n-(thickness-1)/2)
				array[y2,x2+i] = self.crossElement
			return array
		
		linestartx = int(xcenter - (size/2)*math.cos(angler))
		lineendx = int(xcenter + (size/2)*math.cos(angler))

		x = np.arange(linestartx, lineendx+1, dtype = np.int16)
		y = m*x + c
		y = y.astype(np.int16)
		for n in range(thickness):
			i = int(n-(thickness-1)/2)
			array[y+i,x] = self.crossElement
		return array
	
	def emitQmap(self,resize):			
		totalbytes = resize.nbytes
		bpl = int(totalbytes/resize.shape[0])
		qarray = QtGui.QImage(resize.data, resize.shape[1],resize.shape[0], bpl, QtGui.QImage.Format.Format_BGR888)
		pixmap = QtGui.QPixmap.fromImage(qarray)
		self.output.emit(pixmap)
			

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
