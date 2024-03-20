# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.9.2


from PyQt5 import QtCore, QtGui, QtWidgets

import ctypes
import numpy as np

#from ffpyplayer.player import MediaPlayer
import time
from datetime import datetime
from pathlib import Path
import os, sys


def stringToBool(string):
	if string == 'True':
		return True
	else:
		return False

class parAttributes():
	def __init__(self, param):
		self.param = param
	def name(self):
		return self.objectName()
	def parValue(self):
		if type(self.param) == QtWidgets.QSpinBox or type(self.param) == QtWidgets.QDoubleSpinBox:
			return self.param.value()
		elif type(self.param) == QtWidgets.QComboBox:
			return self.param.currentText()
		elif type(self.param) == QtWidgets.QLineEdit:
			return self.param.text()

		
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

class Worker(QtCore.QThread):
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


			"""
			Destroy the copied item to prevent memory leaks
			"""
			#BufferFactory.destroy(item)
			
			#cycletimes = np.append(cycletimes,curr_frame_time-prev_frame_time)
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



class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("rtsp GUI")

		self.screen = QtWidgets.QApplication.primaryScreen().size()
		self.screenwidth = self.screen.width()
		self.screenheight = self.screen.height()


		if self.screenheight > 2000:
			monydefault = 2000
		elif self.screenheight > 1400:
			monydefault = 1300
		else:
			monydefault = 900
		scaling = (self.screenwidth/1920)**0.5 #scaling box and font sizes for different screen resolutions
		windowsize = [int(350*scaling),int(700*scaling)]
		MainWindow.resize(*windowsize)
		MainWindow.move(0,self.screenheight - windowsize[1] - 75)
		box1pos = [int(20*scaling), int(35*scaling)]
		boxDimensions = [int(80*scaling),int(22*scaling)]
		lineBoxDimensions = [int(200*scaling),int(22*scaling)]
		boxOffset = boxDimensions[1] + int(18*scaling)
		labelxpos = 20 + boxDimensions[0] + 10
		box2x = int(20 + boxDimensions[0] + 10*scaling)
		box1x = 20
		homepath = str(Path.home())
		endpath = 'Documents/rtspGuiSnapShots'
		self.snapshotDir = f'{homepath}/{endpath}/'
		if not os.path.exists(self.snapshotDir):
			os.makedirs(self.snapshotDir)
		
		basefont = int(12*scaling)

		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")


		font = QtGui.QFont()
		font.setPointSize(basefont)
		boxfont = QtGui.QFont()
		boxfont.setPointSize(basefont-4)
		labelfont = QtGui.QFont()
		labelfont.setPointSize(basefont-4)
		smallLabelfont = QtGui.QFont()
		smallLabelfont.setPointSize(basefont-5)

		self.rtspAddressBox = QtWidgets.QLineEdit(self.centralwidget)
		self.rtspAddressBox.setGeometry(QtCore.QRect(box1x, int(0*boxOffset + box1pos[1]),*lineBoxDimensions))
		self.rtspAddressBox.setObjectName("rtspAddressBox")
		self.rtspAddressBox.setFont(boxfont)

		self.rtspAdressLabel = QtWidgets.QLabel(self.centralwidget)
		self.rtspAdressLabel.setGeometry(QtCore.QRect(box1x, int(-0.5*boxOffset + box1pos[1]), 111, 16))
		self.rtspAdressLabel.setObjectName("rtspAdressLabel")
		self.rtspAdressLabel.setFont(labelfont)
		self.rtspAdressLabel.setText('rtsp address')

		self.rtspAdressesLabel = QtWidgets.QLabel(self.centralwidget)
		self.rtspAdressesLabel.setGeometry(QtCore.QRect(box1x, int(0.6*boxOffset + box1pos[1]), 111, 16))
		self.rtspAdressesLabel.setObjectName("rtspAdressesLabel")
		self.rtspAdressesLabel.setFont(labelfont)
		self.rtspAdressesLabel.setText('stored rtsp addresses')
		self.rtspAdressesLabel.adjustSize()

		self.rtspAddressesBox = QtWidgets.QComboBox(self.centralwidget)
		self.rtspAddressesBox.setGeometry(QtCore.QRect(box1x, int(1*boxOffset + box1pos[1]),*lineBoxDimensions))
		self.rtspAddressesBox.setObjectName("rtspAddressesBox")
		self.rtspAddressesBox.setFont(boxfont)

		self.removeAddressButton = QtWidgets.QPushButton(self.centralwidget)
		self.removeAddressButton.setGeometry(QtCore.QRect(box1x+10+lineBoxDimensions[0], int(0.9*boxOffset + box1pos[1]),*boxDimensions))
		self.removeAddressButton.setObjectName("removeAddressButton")
		self.removeAddressButton.setFont(boxfont)
		self.removeAddressButton.setText('remove\naddress')
		self.removeAddressButton.adjustSize()

		self.monitorxBox = QtWidgets.QSpinBox(self.centralwidget) #select x size of image on screen (in pixels)
		self.monitorxBox.setGeometry(QtCore.QRect(box1x, 2*boxOffset + box1pos[1],*boxDimensions))
		self.monitorxBox.setMinimum(100)
		self.monitorxBox.setMaximum(3840)
		self.monitorxBox.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
		self.monitorxBox.setProperty("value", 3000)
		self.monitorxBox.setObjectName("monitorxBox")
		self.monitorxBox.setFont(boxfont)

		self.monitorxLabel = QtWidgets.QLabel(self.centralwidget)
		self.monitorxLabel.setGeometry(QtCore.QRect(10, int(1.65*boxOffset + box1pos[1]), 111, 16))
		self.monitorxLabel.setObjectName("monitorxLabel")
		self.monitorxLabel.setFont(labelfont)

		self.monitoryBox = QtWidgets.QSpinBox(self.centralwidget) #select y size of image on screen (in pixels)
		self.monitoryBox.setGeometry(QtCore.QRect(int(box2x+20*scaling), 2*boxOffset + box1pos[1],*boxDimensions))
		self.monitoryBox.setMinimum(100)
		self.monitoryBox.setMaximum(3000)
		self.monitoryBox.setSingleStep(1)
		self.monitoryBox.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
		self.monitoryBox.setProperty("value", monydefault)
		self.monitoryBox.setObjectName("monitoryBox")
		self.monitoryBox.setFont(boxfont)

		self.monitoryLabel = QtWidgets.QLabel(self.centralwidget)
		self.monitoryLabel.setGeometry(QtCore.QRect(int(box2x+20*scaling), int(1.65*boxOffset + box1pos[1]), 111, 16))
		self.monitoryLabel.setObjectName("monitoryLabel")
		self.monitoryLabel.setFont(labelfont)

		self.aspectInfoLabel = QtWidgets.QLabel(self.centralwidget)
		self.aspectInfoLabel.setGeometry(QtCore.QRect(box1x, int(2.7*boxOffset + box1pos[1]), 201, 41))
		self.aspectInfoLabel.setFont(smallLabelfont)
		self.aspectInfoLabel.setObjectName("aspectInfoLabel")

		self.frameSkipBox = QtWidgets.QSpinBox(self.centralwidget) #select gain (if gainAuto is off)
		self.frameSkipBox.setGeometry(QtCore.QRect(box1x, 5*boxOffset + box1pos[1],*boxDimensions))
		self.frameSkipBox.setMinimum(0)
		self.frameSkipBox.setMaximum(9)
		self.frameSkipBox.setValue(2)
		self.frameSkipBox.setObjectName("frameSkipBox")
		self.frameSkipBox.setFont(boxfont)
		self.frameSkipBox.valueChanged.connect(self.changeSkip)

		self.frameSkipLabel = QtWidgets.QLabel(self.centralwidget)
		self.frameSkipLabel.setGeometry(QtCore.QRect(labelxpos, int(4.8*boxOffset + box1pos[1]), 81, 31))
		self.frameSkipLabel.setObjectName("frameSkipLabel")
		self.frameSkipLabel.setFont(labelfont)	
		self.frameSkipLabel.setText('frame skip frequencey\n(higher will reduce frame rate,\nbut keep latency low)')
		self.frameSkipLabel.adjustSize()

		self.gainBox = QtWidgets.QSpinBox(self.centralwidget) #select gain (if gainAuto is off)
		self.gainBox.setGeometry(QtCore.QRect(box1x, 7*boxOffset + box1pos[1],*boxDimensions))
		self.gainBox.setMinimum(1)
		self.gainBox.setMaximum(40)
		self.gainBox.setObjectName("gainBox")
		self.gainBox.setFont(boxfont)

		self.gainCheck = QtWidgets.QCheckBox(self.centralwidget)
		self.gainCheck.setGeometry(QtCore.QRect(box1x, int(6*boxOffset + box1pos[1]),int(10*scaling),int(10*scaling)))
		self.gainCheck.setObjectName('gainCheck')
		self.gainCheck.setText('use gain? (allows brightness to be adjusted,\nbut reduces frame rate and introduces latency)')
		self.gainCheck.setFont(labelfont)
		self.gainCheck.setChecked(False)
		self.gainCheck.adjustSize()
		self.gainCheck.stateChanged.connect(self.changeGainCheck)

		self.gainLabel = QtWidgets.QLabel(self.centralwidget)
		self.gainLabel.setGeometry(QtCore.QRect(labelxpos, 7*boxOffset + box1pos[1], 81, 31))
		self.gainLabel.setObjectName("gainLabel")
		self.gainLabel.setFont(labelfont)

		self.crossSizeBox =	 QtWidgets.QSpinBox(self.centralwidget) #select the size of the cross that is overlayed on the image
		self.crossSizeBox.setGeometry(QtCore.QRect(box1x, 8*boxOffset + box1pos[1],*boxDimensions))
		self.crossSizeBox.setObjectName("crossSizeBox")
		self.crossSizeBox.setFont(boxfont)
		self.crossSizeBox.setMinimum(100)
		self.crossSizeBox.setMaximum(2500)
		self.crossSizeBox.setValue(700)
		self.crossSizeBox.setSingleStep(10)

		self.crossSizeLabel = QtWidgets.QLabel(self.centralwidget)
		self.crossSizeLabel.setGeometry(QtCore.QRect(box1x, int(7.65*boxOffset + box1pos[1]), 81, 31))
		self.crossSizeLabel.setObjectName("crossSizeLabel")
		self.crossSizeLabel.setText('cross size')
		self.crossSizeLabel.setFont(labelfont)
		self.crossSizeLabel.adjustSize()

		self.crossCheckBox =  QtWidgets.QCheckBox(self.centralwidget) #select whether or not to display the cross
		self.crossCheckBox.setGeometry(QtCore.QRect(labelxpos, 8*boxOffset + box1pos[1],int(10*scaling),int(10*scaling)))
		self.crossCheckBox.setObjectName('crossCheckBox')
		self.crossCheckBox.setText('display cross?')
		self.crossCheckBox.setFont(labelfont)
		self.crossCheckBox.setChecked(True)
		self.crossCheckBox.adjustSize()
		self.crossCheckBox.stateChanged.connect(self.crossCheckChange)

		self.crossOffsetHBox =	QtWidgets.QSpinBox(self.centralwidget) #choose center position of cross in y
		self.crossOffsetHBox.setGeometry(QtCore.QRect(box1x, 9*boxOffset + box1pos[1],*boxDimensions))
		self.crossOffsetHBox.setObjectName("crossOffsetHBox")
		self.crossOffsetHBox.setFont(boxfont)
		self.crossOffsetHBox.setMinimum(-1500)
		self.crossOffsetHBox.setMaximum(1500)
		self.crossOffsetHBox.setValue(0)

		self.crossHLabel = QtWidgets.QLabel(self.centralwidget)
		self.crossHLabel.setGeometry(QtCore.QRect(box1x, int(8.6*boxOffset + box1pos[1]), 81, 31))
		self.crossHLabel.setObjectName("crossHLabel")
		self.crossHLabel.setText('cross y offset')
		self.crossHLabel.setFont(labelfont)
		self.crossHLabel.adjustSize()

		self.crossOffsetWBox =	QtWidgets.QSpinBox(self.centralwidget) #choose center position of cross in x
		self.crossOffsetWBox.setGeometry(QtCore.QRect(30 + boxDimensions[0], 9*boxOffset + box1pos[1],*boxDimensions))
		self.crossOffsetWBox.setObjectName("crossOffsetWBox")
		self.crossOffsetWBox.setFont(boxfont)
		self.crossOffsetWBox.setMinimum(-1500)
		self.crossOffsetWBox.setMaximum(1500)
		self.crossOffsetWBox.setValue(0)

		self.crossWLabel = QtWidgets.QLabel(self.centralwidget)
		self.crossWLabel.setGeometry(QtCore.QRect(30 + boxDimensions[0], int(8.6*boxOffset + box1pos[1]), 81, 31))
		self.crossWLabel.setObjectName("crossWLabel")
		self.crossWLabel.setText('cross x offset')
		self.crossWLabel.setFont(labelfont)
		self.crossWLabel.adjustSize()

		self.lockCrossPositionBox =  QtWidgets.QCheckBox(self.centralwidget) #select whether or not to display the cross
		self.lockCrossPositionBox.setGeometry(QtCore.QRect(2*boxDimensions[0] + 40, int(8.9*boxOffset + box1pos[1]),int(10*scaling),int(10*scaling)))
		self.lockCrossPositionBox.setObjectName('lockCrossPositionBox')
		self.lockCrossPositionBox.setText('lock cross\nposition')
		self.lockCrossPositionBox.setFont(labelfont)
		self.lockCrossPositionBox.setChecked(True)
		self.lockCrossPositionBox.adjustSize()

		if self.lockCrossPositionBox.isChecked():
			self.crossOffsetWBox.setEnabled(False)
			self.crossOffsetHBox.setEnabled(False)

		self.runButton = QtWidgets.QPushButton(self.centralwidget)
		self.runButton.setGeometry(QtCore.QRect(box1x, 10*boxOffset + box1pos[1], int(130*scaling), int(40*scaling)))
		self.runButton.setFont(font)
		self.runButton.setObjectName("runButton")

		self.stopButton = QtWidgets.QPushButton(self.centralwidget)
		self.stopButton.setGeometry(QtCore.QRect(box1x + int(130*scaling) + 10, 10*boxOffset + box1pos[1], 75, 23))
		self.stopButton.setObjectName("stopButton")
		self.stopButton.setFont(font)
		self.stopButton.adjustSize()
		self.stopButton.setEnabled(False)

		self.snapShotButton = QtWidgets.QPushButton(self.centralwidget)
		self.snapShotButton.setGeometry(QtCore.QRect(box1x, int(11.2*boxOffset + box1pos[1]), int(130*scaling), int(40*scaling)))
		self.snapShotButton.setFont(labelfont)
		self.snapShotButton.setObjectName("snapShotButton")
		self.snapShotButton.setText('take single image')
		self.snapShotButton.adjustSize()
		self.snapShotButton.setEnabled(False)

		self.imageSeriesButton = QtWidgets.QPushButton(self.centralwidget)
		self.imageSeriesButton.setGeometry(QtCore.QRect(box1x, int(12*boxOffset + box1pos[1]), int(130*scaling), int(40*scaling)))
		self.imageSeriesButton.setFont(labelfont)
		self.imageSeriesButton.setObjectName("imageSeriesButton")
		self.imageSeriesButton.setText('take image series')
		self.imageSeriesButton.adjustSize()
		self.imageSeriesButton.setEnabled(False)

		self.imageSeriesTime = QtWidgets.QSpinBox(self.centralwidget)
		self.imageSeriesTime.setGeometry(QtCore.QRect(int(box2x + 10*scaling), int(12*boxOffset + box1pos[1]), int(50*scaling), boxDimensions[1]))
		self.imageSeriesTime.setFont(labelfont)
		self.imageSeriesTime.setObjectName("imageSeriesTime")
		self.imageSeriesTime.setMinimum(1)
		self.imageSeriesTime.setMaximum(3600)
		self.imageSeriesTime.setValue(1800)
		self.imageSeriesTime.setSingleStep(60)

		self.imageSeriesTimeLabel = QtWidgets.QLabel(self.centralwidget)
		self.imageSeriesTimeLabel.setGeometry(QtCore.QRect(int(box2x + 70*scaling), int(12*boxOffset + box1pos[1]), int(60*scaling), int(40*scaling)))
		self.imageSeriesTimeLabel.setFont(labelfont)
		self.imageSeriesTimeLabel.setObjectName("imageSeriesTimeLabel")
		self.imageSeriesTimeLabel.setText('series time period\n(seconds)')
		self.imageSeriesTimeLabel.adjustSize()

		self.imageSeriesStopButton = QtWidgets.QPushButton(self.centralwidget)
		self.imageSeriesStopButton.setGeometry(QtCore.QRect(box1x, int(12.8*boxOffset + box1pos[1]), int(130*scaling), int(40*scaling)))
		self.imageSeriesStopButton.setFont(labelfont)
		self.imageSeriesStopButton.setObjectName("imageSeriesStopButton")
		self.imageSeriesStopButton.setText('stop image series')
		self.imageSeriesStopButton.adjustSize()
		self.imageSeriesStopButton.setEnabled(False)

		self.directoryBox = QtWidgets.QLineEdit(self.centralwidget)
		self.directoryBox.setGeometry(QtCore.QRect(box1x, int(box1pos[1]+14*boxOffset),int(boxDimensions[0]*2),boxDimensions[1]))
		self.directoryBox.setObjectName("directoryBox")
		self.directoryBox.setFont(boxfont)
		self.directoryBox.setText(self.snapshotDir)

		self.openDirectoryButton = QtWidgets.QPushButton(self.centralwidget)
		self.openDirectoryButton.setGeometry(QtCore.QRect(int(box1x + 10*scaling + boxDimensions[0]*2), int(box1pos[1]+14*boxOffset),boxDimensions[1],boxDimensions[1]))
		self.openDirectoryButton.setObjectName("openDirectoryButton")
		self.openDirectoryButton.setFont(boxfont)
		self.openDirectoryButton.setText('...')

		self.directoryLabel = QtWidgets.QLabel(self.centralwidget)
		self.directoryLabel.setGeometry(QtCore.QRect(box1x, int(box1pos[1]+13.65*boxOffset),int(boxDimensions[0]*2),boxDimensions[1]))
		self.directoryLabel.setObjectName('directoryLabel')
		self.directoryLabel.setText('image directory')
		self.directoryLabel.setFont(labelfont)
		self.directoryLabel.adjustSize()

		self.linePositionLabel = QtWidgets.QLabel(self.centralwidget)
		self.linePositionLabel.setGeometry(QtCore.QRect(box1x, int(14.7*boxOffset + box1pos[1]),*boxDimensions))
		self.linePositionLabel.setObjectName('linePositionLabel')
		self.linePositionLabel.setText('line position')
		self.linePositionLabel.setFont(labelfont)
		self.linePositionLabel.adjustSize()

		self.linePositionBox =	 QtWidgets.QSpinBox(self.centralwidget) #select the size of the cross that is overlayed on the image
		self.linePositionBox.setGeometry(QtCore.QRect(box1x, 15*boxOffset + box1pos[1],*boxDimensions))
		self.linePositionBox.setObjectName("linePositionBox")
		self.linePositionBox.setFont(boxfont)
		self.linePositionBox.setMinimum(0)
		self.linePositionBox.setMaximum(3000)
		self.linePositionBox.setValue(600)
		self.linePositionBox.setSingleStep(1)
		self.linePositionBox.setKeyboardTracking(False)
		self.linePositionBox.valueChanged.connect(self.linePositionChange)
		self.linePositionBox.valueChanged.connect(self.updateConfigLog)

		self.lineCheckBox =  QtWidgets.QCheckBox(self.centralwidget) #select whether or not to display the cross
		self.lineCheckBox.setGeometry(QtCore.QRect(labelxpos, 15*boxOffset + box1pos[1],int(10*scaling),int(10*scaling)))
		self.lineCheckBox.setObjectName('lineCheckBox')
		self.lineCheckBox.setText('display line?')
		self.lineCheckBox.setFont(labelfont)
		self.lineCheckBox.setChecked(True)
		self.lineCheckBox.adjustSize()
		self.lineCheckBox.stateChanged.connect(self.lineCheckChange)
		self.lineCheckBox.stateChanged.connect(self.updateConfigLog)

		MainWindow.setCentralWidget(self.centralwidget)
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 234, 21))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)



		self.gainBox.setValue(20)
		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

		self.running = False

		self.updateParamDct()
		self.settingsLog = f'{homepath}/rtspGuiConfig/rtspGUIconfiguration.log'
		self.addressLog = f'{homepath}/rtspGuiConfig/rtspAddresses.log'
		if not os.path.exists(os.path.dirname(self.settingsLog)):
			os.makedirs(os.path.dirname(self.settingsLog))
		if os.path.exists(self.settingsLog):
			self.readConfigLog()
		if os.path.exists(self.addressLog):
			self.readAddressLog()

		self.monitorxBox.setKeyboardTracking(False)
		self.monitoryBox.setKeyboardTracking(False)

		self.gainBox.setKeyboardTracking(False)
		self.crossSizeBox.setKeyboardTracking(False)
		self.crossOffsetHBox.setKeyboardTracking(False)
		self.crossOffsetWBox.setKeyboardTracking(False)
		self.monitorxBox.valueChanged.connect(self.updateConfigLog)
		self.monitoryBox.valueChanged.connect(self.updateConfigLog)
		self.gainBox.valueChanged.connect(self.updateConfigLog)
		self.crossSizeBox.valueChanged.connect(self.updateConfigLog)
		self.crossOffsetHBox.valueChanged.connect(self.updateConfigLog)
		self.crossOffsetWBox.valueChanged.connect(self.updateConfigLog)
		self.runButton.clicked.connect(self.start_worker)
		self.stopButton.clicked.connect(self.stop_worker)
		self.snapShotButton.clicked.connect(self.takeSingleImage)
		self.imageSeriesButton.clicked.connect(self.takeImageSeries)
		self.imageSeriesStopButton.clicked.connect(self.stopImageSeries)
		self.gainBox.valueChanged.connect(self.changeGain)
		self.crossSizeBox.valueChanged.connect(self.crossSizeChange)
		self.crossOffsetHBox.valueChanged.connect(self.crossHChange)
		self.crossOffsetHBox.valueChanged.connect(self.updateConfigLog)
		self.crossOffsetWBox.valueChanged.connect(self.crossWChange)
		self.crossOffsetWBox.valueChanged.connect(self.updateConfigLog)
		self.monitorxBox.valueChanged.connect(self.changeMonitorx)
		self.monitoryBox.valueChanged.connect(self.changeMonitory)
		self.lockCrossPositionBox.stateChanged.connect(self.crossDisplayCheck)
		self.lockCrossPositionBox.stateChanged.connect(self.updateConfigLog)
		self.openDirectoryButton.clicked.connect(self.folderDialogue)
		self.rtspAddressesBox.currentTextChanged.connect(self.changeAddress)
		self.removeAddressButton.clicked.connect(self.removeAddress)
			


	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "rtsp GUI"))
		self.runButton.setText(_translate("MainWindow", "Let\'s gooooo!"))

		self.monitorxLabel.setText(_translate("MainWindow", "x image size on screen"))
		self.monitorxLabel.adjustSize()
		self.monitoryLabel.setText(_translate("MainWindow", "y image size on screen"))
		self.monitoryLabel.adjustSize()
		self.aspectInfoLabel.setText(_translate("MainWindow", "aspect ratio of image on screen will be\n"
"scaled automatically"))
		self.aspectInfoLabel.adjustSize()
		self.gainLabel.setText(_translate("MainWindow", "Gain (set Gain\n"
"Auto to \'Off\')"))
		self.gainLabel.adjustSize()
		self.stopButton.setText(_translate("MainWindow", "Stop"))

	def start_worker(self):
		self.updateConfigLog()
		self.running = True
		self.stopButton.setEnabled(True)
		self.snapShotButton.setEnabled(True)
		self.imageSeriesButton.setEnabled(True)
		self.addAddress()

		rtspAdress = self.rtspAddressBox.text()
		monitorx = self.monitorxBox.value()
		monitory = self.monitoryBox.value()
		frameSkip = self.frameSkipBox.value()
		gain = self.gainBox.value()		
		useGain = self.gainCheck.isChecked()
		
		crosssize = self.crossSizeBox.value()		
		crossOffsetH = self.crossOffsetHBox.value()		
		crossOffsetW = self.crossOffsetWBox.value()
		crossCheck = self.crossCheckBox.isChecked()
		imageTime = self.imageSeriesTime.value()

		self.thread = Worker(address= rtspAdress, monitorx = monitorx,monitory = monitory,
		gain = gain, screenwidth = self.screenwidth, screenheight=self.screenheight, frameSkip = frameSkip,
		crosssize = crosssize,crossOffsetH = crossOffsetH, crossOffsetW = crossOffsetW, crossCheck = crossCheck, imageTime = imageTime, 
		imageDir = self.snapshotDir,lineCheck=self.lineCheckBox.isChecked(), linePosition=self.linePositionBox.value(), useGain = useGain)

		self.thread.start()
		self.runButton.setEnabled(False)

	def stop_worker(self):
		self.thread.stop()
		self.runButton.setEnabled(True)
		self.stopButton.setEnabled(False)
		self.snapShotButton.setEnabled(False)
		self.imageSeriesButton.setEnabled(False)
		self.imageSeriesStopButton.setEnabled(False)
		self.running = False

	def updateParamDct(self):
		self.paramDct = {self.rtspAddressBox.objectName(): [self.rtspAddressBox,self.rtspAddressBox.text()],
						self.crossOffsetHBox.objectName(): [self.crossOffsetHBox,self.crossOffsetHBox.value()],
						self.crossOffsetWBox.objectName(): [self.crossOffsetWBox,self.crossOffsetWBox.value()],
						self.monitorxBox.objectName(): [self.monitorxBox,self.monitorxBox.value()],
						self.monitoryBox.objectName(): [self.monitoryBox,self.monitoryBox.value()],
						self.gainBox.objectName(): [self.gainBox,self.gainBox.value()],
						self.crossSizeBox.objectName(): [self.crossSizeBox, self.crossSizeBox.value()] ,
						self.directoryBox.objectName():[self.directoryBox,self.directoryBox.text()],
						self.linePositionBox.objectName():[self.linePositionBox,self.linePositionBox.value()],
						self.lineCheckBox.objectName():[self.lineCheckBox,self.lineCheckBox.isChecked()],
						self.frameSkipBox.objectName():[self.frameSkipBox,self.frameSkipBox.value()],
						self.gainCheck.objectName():[self.gainCheck,self.gainCheck.isChecked()]}
	
	def addAddress(self):
		currentAddress = self.rtspAddressBox.text()
		allItems = [self.rtspAddressesBox.itemText(i) for i in 
			  range(self.rtspAddressesBox.count())]
		if not currentAddress in allItems:
			self.rtspAddressesBox.addItem(self.rtspAddressBox.text())
			self.rtspAddressesBox.setCurrentIndex(self.rtspAddressesBox.count()-1)
			self.updateConfigLog()
			self.updateAddressLog()

	def changeAddress(self):
		newAddress = self.rtspAddressesBox.currentText()
		self.rtspAddressBox.setText(newAddress)
		self.updateConfigLog()
	
	def updateAddressLog(self):
		allItems = [self.rtspAddressesBox.itemText(i) for i in 
			  range(self.rtspAddressesBox.count())]
		addressesString = '\n'.join(allItems)
		f = open(self.addressLog,'w')
		f.write(addressesString)
		f.close()
	
	def readAddressLog(self):
		f = open(self.addressLog,'r')
		addressString = f.read()
		f.close()
		allAdresses = addressString.split('\n')
		for item in allAdresses:
			self.rtspAddressesBox.addItem('')
			self.rtspAddressesBox.setItemText(self.rtspAddressesBox.count()-1,item)
			if item == self.rtspAddressBox.text():
				self.rtspAddressesBox.setCurrentIndex(self.rtspAddressesBox.count()-1)
	
	def removeAddress(self):
		if self.rtspAddressesBox.count() > 0:
			self.rtspAddressesBox.removeItem(self.rtspAddressesBox.currentIndex())

	def changeGain(self):
		if self.running:
			self.thread.gain = self.gainBox.value()
	def changeGainCheck(self):
		if self.running:
			self.thread.useGain = self.gainCheck.isChecked()
	def changeSkip(self):
		if self.running:
			self.thread.frameSkip = self.frameSkipBox.value()
	def crossSizeChange(self):
		if self.running:
			self.thread.crosssize = self.crossSizeBox.value()
	def crossHChange(self):
		if self.running:
			self.thread.crossOffsetH = self.crossOffsetHBox.value()

	def crossWChange(self):
		if self.running:
			self.thread.crossOffsetW = self.crossOffsetWBox.value()
	
	def linePositionChange(self):
		if self.running:
			self.thread.linePosition = self.linePositionBox.value()
	
	def lineCheckChange(self):
		if self.running:
			self.thread.lineCheck = self.lineCheckBox.isChecked()
	
	def crossCheckChange(self):
		if self.running:
			self.thread.crossCheck = self.crossCheckBox.isChecked()
		
	def changeMonitorx(self):
		monx = self.monitorxBox.value()
		mony = self.monitoryBox.value()
		if self.running:
			aspect = self.thread.aspect
			monx,mony = aspectAdjust(monx,mony,aspect)
			self.thread.monitorx = monx
			self.thread.monitory = mony

	def changeMonitory(self):
		monx = self.monitorxBox.value()
		mony = self.monitoryBox.value()
		if self.running:
			aspect = self.thread.aspect
			monx,mony = aspectAdjust(monx,mony,aspect)
			self.thread.monitory = mony
			self.thread.monitorx = monx

	def takeSingleImage(self):
		if self.running:
			self.thread.snapshot = True

	def takeImageSeries(self):
		if self.running:
			self.thread.imageSeries = True
			self.thread.imageTime = self.imageSeriesTime.value()
			self.thread.imageCountDown = 0
			self.imageSeriesButton.setEnabled(False)
			self.imageSeriesStopButton.setEnabled(True)

	def stopImageSeries(self):
		if self.running:
			self.thread.imageSeries = False
			self.imageSeriesButton.setEnabled(True)
			self.imageSeriesStopButton.setEnabled(False)
	def crossDisplayCheck(self):
		if self.lockCrossPositionBox.isChecked():
			self.crossOffsetHBox.setEnabled(False)
			self.crossOffsetWBox.setEnabled(False)
		else:
			self.crossOffsetHBox.setEnabled(True)
			self.crossOffsetWBox.setEnabled(True)



	def folderDialogue(self):
		folder = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory",self.directoryBox.text()))
		if folder != '':
			self.directoryBox.setText(folder)
			self.snapshotDir = folder
			#f = open(logFile,'w')
			#f.write(folder)
			#f.close()
			self.updateConfigLog()
			if self.running:
				self.thread.imageDir = folder
	def updateConfigLog(self):
		self.updateParamDct()
		logUpdate = ''
		for par in self.paramDct:
			logUpdate += f'{par};{self.paramDct[par][1]}\n'
		f = open(self.settingsLog,'w')
		f.write(logUpdate)
		f.close()
	def readConfigLog(self):
		f = open(self.settingsLog,'r')
		lines = f.readlines()
		f.close()
		for line in lines:
			parname = line.split(';')[0]
			parvalue = line.split(';')[1].replace('\n','')
			if parname not in list(self.paramDct.keys()):
				continue
			if type(self.paramDct[parname][0]) == QtWidgets.QSpinBox:
				self.paramDct[parname][0].setValue(int(parvalue))
			elif type(self.paramDct[parname][0]) == QtWidgets.QDoubleSpinBox:
				self.paramDct[parname][0].setValue(float(parvalue))
			elif type(self.paramDct[parname][0]) == QtWidgets.QLineEdit:
				self.paramDct[parname][0].setText(parvalue)
			elif type(self.paramDct[parname][0]) == QtWidgets.QComboBox:
				self.paramDct[parname][0].setCurrentText(parvalue)
			elif type(self.paramDct[parname][0]) == QtWidgets.QCheckBox:
				self.paramDct[parname][0].setChecked(stringToBool(parvalue))
		self.updateParamDct()

def main():
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())
if __name__ == "__main__":
	main()

