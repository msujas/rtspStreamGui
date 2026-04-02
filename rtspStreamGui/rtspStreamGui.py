# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.9.2


from PyQt6 import QtCore, QtGui, QtWidgets
from .rtspWorker import Worker, aspectAdjust,NewWindow,  DummyWorker
import cv2
import time
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


class Ui_MainWindow(QtWidgets.QMainWindow):
	def setupUi(self):
		super().setObjectName("rtsp GUI")

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
		super().resize(*windowsize)
		super().move(0,self.screenheight - windowsize[1] - 75)
		iconfile = f'{os.path.dirname(os.path.realpath(__file__))}/image/icon.ico'
		icon = QtGui.QIcon(iconfile)
		super().setWindowIcon(icon)
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

		self.centralwidget = QtWidgets.QWidget()
		self.centralwidget.setObjectName("centralwidget")

		self.gridlayout = QtWidgets.QGridLayout()

		font = QtGui.QFont()
		font.setPointSize(basefont)
		boxfont = QtGui.QFont()
		boxfont.setPointSize(basefont-4)
		labelfont = QtGui.QFont()
		labelfont.setPointSize(basefont-4)
		smallLabelfont = QtGui.QFont()
		smallLabelfont.setPointSize(basefont-5)

		self.rtspAddressBox = QtWidgets.QLineEdit()
		self.rtspAddressBox.setObjectName("rtspAddressBox")
		self.rtspAddressBox.setFont(boxfont)
		self.gridlayout.addWidget(self.rtspAddressBox, 1,0,1,2)

		self.rtspAdressLabel = QtWidgets.QLabel()
		self.rtspAdressLabel.setObjectName("rtspAdressLabel")
		self.rtspAdressLabel.setFont(labelfont)
		self.rtspAdressLabel.setText('rtsp address')
		self.gridlayout.addWidget(self.rtspAdressLabel, 0,0)

		self.rtspAdressesLabel = QtWidgets.QLabel()
		self.rtspAdressesLabel.setObjectName("rtspAdressesLabel")
		self.rtspAdressesLabel.setFont(labelfont)
		self.rtspAdressesLabel.setText('stored rtsp addresses')
		self.rtspAdressesLabel.adjustSize()
		self.gridlayout.addWidget(self.rtspAdressesLabel, 2,0)

		self.rtspAddressesBox = QtWidgets.QComboBox()
		self.rtspAddressesBox.setObjectName("rtspAddressesBox")
		self.rtspAddressesBox.setFont(boxfont)
		self.gridlayout.addWidget(self.rtspAddressesBox, 3,0,1,2)

		self.removeAddressButton = QtWidgets.QPushButton()
		self.removeAddressButton.setObjectName("removeAddressButton")
		self.removeAddressButton.setFont(boxfont)
		self.removeAddressButton.setText('remove\naddress')
		self.removeAddressButton.adjustSize()
		self.gridlayout.addWidget(self.removeAddressButton, 3,2)

		self.monitorxBox = QtWidgets.QSpinBox() #select x size of image on screen (in pixels)
		self.monitorxBox.setMinimum(100)
		self.monitorxBox.setMaximum(3840)
		self.monitorxBox.setProperty("value", 3000)
		self.monitorxBox.setObjectName("monitorxBox")
		self.monitorxBox.setFont(boxfont)
		self.gridlayout.addWidget(self.monitorxBox, 5,0)

		self.monitorxLabel = QtWidgets.QLabel()
		self.monitorxLabel.setObjectName("monitorxLabel")
		self.monitorxLabel.setFont(labelfont)
		self.gridlayout.addWidget(self.monitorxLabel, 4,0)

		self.monitoryBox = QtWidgets.QSpinBox() #select y size of image on screen (in pixels)
		self.monitoryBox.setMinimum(100)
		self.monitoryBox.setMaximum(3000)
		self.monitoryBox.setSingleStep(1)
		self.monitoryBox.setProperty("value", monydefault)
		self.monitoryBox.setObjectName("monitoryBox")
		self.monitoryBox.setFont(boxfont)
		self.gridlayout.addWidget(self.monitoryBox,5,1)

		self.monitoryLabel = QtWidgets.QLabel()
		self.monitoryLabel.setObjectName("monitoryLabel")
		self.monitoryLabel.setFont(labelfont)
		self.gridlayout.addWidget(self.monitoryLabel,4,1)

		self.aspectInfoLabel = QtWidgets.QLabel()
		self.aspectInfoLabel.setFont(smallLabelfont)
		self.aspectInfoLabel.setObjectName("aspectInfoLabel")
		self.gridlayout.addWidget(self.aspectInfoLabel,6,0,1,2)

		self.frameSkipBox = QtWidgets.QSpinBox() #select gain (if gainAuto is off)
		self.frameSkipBox.setMinimum(0)
		self.frameSkipBox.setMaximum(9)
		self.frameSkipBox.setValue(2)
		self.frameSkipBox.setObjectName("frameSkipBox")
		self.frameSkipBox.setFont(boxfont)
		self.frameSkipBox.valueChanged.connect(self.changeSkip)
		self.gridlayout.addWidget(self.frameSkipBox,7,0)

		self.frameSkipLabel = QtWidgets.QLabel()
		self.frameSkipLabel.setObjectName("frameSkipLabel")
		self.frameSkipLabel.setFont(labelfont)	
		self.frameSkipLabel.setText('frame skip frequencey\n(higher will reduce frame rate,\nbut keep latency low)')
		self.frameSkipLabel.adjustSize()
		self.gridlayout.addWidget(self.frameSkipLabel,7,1,1,2)

		self.gainCheck = QtWidgets.QCheckBox()
		self.gainCheck.setObjectName('gainCheck')
		self.gainCheck.setText('use gain? (allows brightness to be adjusted,\nbut reduces frame rate and introduces latency)')
		self.gainCheck.setFont(labelfont)
		self.gainCheck.setChecked(False)
		self.gainCheck.adjustSize()
		self.gainCheck.stateChanged.connect(self.changeGainCheck)
		self.gridlayout.addWidget(self.gainCheck,8,0,1,2)

		self.gainBox = QtWidgets.QSpinBox() #select gain (if gainAuto is off)
		self.gainBox.setMinimum(1)
		self.gainBox.setMaximum(40)
		self.gainBox.setObjectName("gainBox")
		self.gainBox.setFont(boxfont)
		self.gridlayout.addWidget(self.gainBox,9,0)

		self.gainLabel = QtWidgets.QLabel()
		self.gainLabel.setObjectName("gainLabel")
		self.gainLabel.setFont(labelfont)
		self.gridlayout.addWidget(self.gainLabel,9,1)

		self.crossSizeLabel = QtWidgets.QLabel()
		self.crossSizeLabel.setObjectName("crossSizeLabel")
		self.crossSizeLabel.setText('cross size')
		self.crossSizeLabel.setFont(labelfont)
		self.crossSizeLabel.adjustSize()
		self.gridlayout.addWidget(self.crossSizeLabel,10,0)

		self.crossSizeBox =	 QtWidgets.QSpinBox() #select the size of the cross that is overlayed on the image
		self.crossSizeBox.setObjectName("crossSizeBox")
		self.crossSizeBox.setFont(boxfont)
		self.crossSizeBox.setMinimum(100)
		self.crossSizeBox.setMaximum(2500)
		self.crossSizeBox.setValue(700)
		self.crossSizeBox.setSingleStep(10)
		self.gridlayout.addWidget(self.crossSizeBox,11,0)

		self.crossCheckBox =  QtWidgets.QCheckBox() #select whether or not to display the cross
		self.crossCheckBox.setObjectName('crossCheckBox')
		self.crossCheckBox.setText('display cross?')
		self.crossCheckBox.setFont(labelfont)
		self.crossCheckBox.setChecked(True)
		self.crossCheckBox.adjustSize()
		self.crossCheckBox.stateChanged.connect(self.crossCheckChange)
		self.gridlayout.addWidget(self.crossCheckBox,11,1)

		self.crossHLabel = QtWidgets.QLabel()
		self.crossHLabel.setObjectName("crossHLabel")
		self.crossHLabel.setText('cross y offset')
		self.crossHLabel.setFont(labelfont)
		self.crossHLabel.adjustSize()
		self.gridlayout.addWidget(self.crossHLabel,12,0)

		self.crossWLabel = QtWidgets.QLabel()
		self.crossWLabel.setObjectName("crossWLabel")
		self.crossWLabel.setText('cross x offset')
		self.crossWLabel.setFont(labelfont)
		self.crossWLabel.adjustSize()
		self.gridlayout.addWidget(self.crossWLabel,12,1)

		self.crossOffsetHBox =	QtWidgets.QSpinBox() #choose center position of cross in y
		self.crossOffsetHBox.setObjectName("crossOffsetHBox")
		self.crossOffsetHBox.setFont(boxfont)
		self.crossOffsetHBox.setMinimum(-1500)
		self.crossOffsetHBox.setMaximum(1500)
		self.crossOffsetHBox.setValue(0)
		self.gridlayout.addWidget(self.crossOffsetHBox,13,0)

		self.crossOffsetWBox =	QtWidgets.QSpinBox() #choose center position of cross in x
		self.crossOffsetWBox.setObjectName("crossOffsetWBox")
		self.crossOffsetWBox.setFont(boxfont)
		self.crossOffsetWBox.setMinimum(-1500)
		self.crossOffsetWBox.setMaximum(1500)
		self.crossOffsetWBox.setValue(0)
		self.gridlayout.addWidget(self.crossOffsetWBox,13,1)



		self.lockCrossPositionBox =  QtWidgets.QCheckBox() #select whether or not to display the cross
		self.lockCrossPositionBox.setObjectName('lockCrossPositionBox')
		self.lockCrossPositionBox.setText('lock cross\nposition')
		self.lockCrossPositionBox.setFont(labelfont)
		self.lockCrossPositionBox.setChecked(True)
		self.lockCrossPositionBox.adjustSize()
		self.gridlayout.addWidget(self.lockCrossPositionBox,13,2)

		if self.lockCrossPositionBox.isChecked():
			self.crossOffsetWBox.setEnabled(False)
			self.crossOffsetHBox.setEnabled(False)

		self.runButton = QtWidgets.QPushButton()
		self.runButton.setFont(font)
		self.runButton.setObjectName("runButton")
		self.runButton.setMinimumHeight(int(50*scaling))
		self.gridlayout.addWidget(self.runButton,14,0,1,2)

		self.stopButton = QtWidgets.QPushButton()
		self.stopButton.setObjectName("stopButton")
		self.stopButton.setFont(font)
		self.stopButton.adjustSize()
		self.stopButton.setEnabled(False)
		self.gridlayout.addWidget(self.stopButton,14,2)

		self.snapShotButton = QtWidgets.QPushButton()
		self.snapShotButton.setFont(labelfont)
		self.snapShotButton.setObjectName("snapShotButton")
		self.snapShotButton.setText('take single image')
		self.snapShotButton.adjustSize()
		self.snapShotButton.setEnabled(False)
		self.gridlayout.addWidget(self.snapShotButton,15,0)

		self.imageSeriesButton = QtWidgets.QPushButton()
		self.imageSeriesButton.setFont(labelfont)
		self.imageSeriesButton.setObjectName("imageSeriesButton")
		self.imageSeriesButton.setText('take image series')
		self.imageSeriesButton.adjustSize()
		self.imageSeriesButton.setEnabled(False)
		self.gridlayout.addWidget(self.imageSeriesButton,16,0)

		self.imageSeriesTime = QtWidgets.QSpinBox()
		self.imageSeriesTime.setFont(labelfont)
		self.imageSeriesTime.setObjectName("imageSeriesTime")
		self.imageSeriesTime.setMinimum(1)
		self.imageSeriesTime.setMaximum(3600)
		self.imageSeriesTime.setValue(1800)
		self.imageSeriesTime.setSingleStep(60)
		self.gridlayout.addWidget(self.imageSeriesTime,16,1)

		self.imageSeriesTimeLabel = QtWidgets.QLabel()
		self.imageSeriesTimeLabel.setFont(labelfont)
		self.imageSeriesTimeLabel.setObjectName("imageSeriesTimeLabel")
		self.imageSeriesTimeLabel.setText('series time period\n(seconds)')
		self.imageSeriesTimeLabel.adjustSize()
		self.gridlayout.addWidget(self.imageSeriesTimeLabel,16,2)

		self.imageSeriesStopButton = QtWidgets.QPushButton()
		self.imageSeriesStopButton.setFont(labelfont)
		self.imageSeriesStopButton.setObjectName("imageSeriesStopButton")
		self.imageSeriesStopButton.setText('stop image series')
		self.imageSeriesStopButton.adjustSize()
		self.imageSeriesStopButton.setEnabled(False)
		self.gridlayout.addWidget(self.imageSeriesStopButton,17,0)

		self.directoryLabel = QtWidgets.QLabel()
		self.directoryLabel.setObjectName('directoryLabel')
		self.directoryLabel.setText('image directory')
		self.directoryLabel.setFont(labelfont)
		self.directoryLabel.adjustSize()
		self.gridlayout.addWidget(self.directoryLabel,18,0)

		self.directoryBox = QtWidgets.QLineEdit()
		self.directoryBox.setObjectName("directoryBox")
		self.directoryBox.setFont(boxfont)
		self.directoryBox.setText(self.snapshotDir)
		self.gridlayout.addWidget(self.directoryBox,19,0,1,2)

		self.openDirectoryButton = QtWidgets.QPushButton()
		self.openDirectoryButton.setObjectName("openDirectoryButton")
		self.openDirectoryButton.setFont(boxfont)
		self.openDirectoryButton.setText('...')
		self.openDirectoryButton.setMaximumWidth(int(30*scaling))

		self.gridlayout.addWidget(self.openDirectoryButton,19,2)



		self.linePositionLabel = QtWidgets.QLabel()
		self.linePositionLabel.setObjectName('linePositionLabel')
		self.linePositionLabel.setText('line position')
		self.linePositionLabel.setFont(labelfont)
		self.linePositionLabel.adjustSize()
		self.gridlayout.addWidget(self.linePositionLabel,20,0)

		self.linePositionBox =	 QtWidgets.QSpinBox() #select the size of the cross that is overlayed on the image
		self.linePositionBox.setObjectName("linePositionBox")
		self.linePositionBox.setFont(boxfont)
		self.linePositionBox.setMinimum(0)
		self.linePositionBox.setMaximum(3000)
		self.linePositionBox.setValue(600)
		self.linePositionBox.setSingleStep(1)
		self.linePositionBox.setKeyboardTracking(False)
		self.linePositionBox.valueChanged.connect(self.linePositionChange)
		self.linePositionBox.valueChanged.connect(self.updateConfigLog)
		self.gridlayout.addWidget(self.linePositionBox,21,0)

		self.lineCheckBox =  QtWidgets.QCheckBox() #select whether or not to display the cross
		self.lineCheckBox.setObjectName('lineCheckBox')
		self.lineCheckBox.setText('display line?')
		self.lineCheckBox.setFont(labelfont)
		self.lineCheckBox.setChecked(True)
		self.lineCheckBox.adjustSize()
		self.lineCheckBox.stateChanged.connect(self.lineCheckChange)
		self.lineCheckBox.stateChanged.connect(self.updateConfigLog)
		self.gridlayout.addWidget(self.lineCheckBox,21,1)

		self.lineanglegrid = QtWidgets.QGridLayout()

		self.lineanglebox = QtWidgets.QDoubleSpinBox()
		self.lineanglebox.setObjectName("lineanglebox")
		self.lineanglebox.setValue(0)
		self.lineanglebox.setDecimals(1)
		self.lineanglebox.setSingleStep(0.1)
		self.lineanglebox.setMinimum(-89.9)
		self.lineanglebox.setMaximum(90)
		self.lineanglebox.setKeyboardTracking(False)
		self.lineanglegrid.addWidget(self.lineanglebox, 1,0)

		self.lineanglelabel= QtWidgets.QLabel()
		self.lineanglelabel.setText('line angle')
		self.lineanglegrid.addWidget(self.lineanglelabel, 0,0)

		self.linethicknessbox = QtWidgets.QSpinBox()
		self.linethicknessbox.setObjectName('linethicknessbox')
		self.linethicknessbox.setValue(3)
		self.linethicknessbox.setMinimum(1)
		self.linethicknessbox.setKeyboardTracking(False)
		self.lineanglegrid.addWidget(self.linethicknessbox,1,1)
		self.linethicknessbox.valueChanged.connect(self.linethicknesschange)
		
		self.linethicknesslabel = QtWidgets.QLabel()
		self.linethicknesslabel.setText('line thickness')
		self.linethicknesslabel.setObjectName('linethicknesslabel')
		self.lineanglegrid.addWidget(self.linethicknesslabel,0,1)

		self.linelengthbox = QtWidgets.QSpinBox()
		self.linelengthbox.setObjectName('linelengthbox')
		self.linelengthbox.setMaximum(1000)
		self.linelengthbox.setMinimum(1)
		self.linelengthbox.setValue(300)
		self.linelengthbox.setKeyboardTracking(False)
		self.linelengthbox.valueChanged.connect(self.linelengthchange)
		self.lineanglegrid.addWidget(self.linelengthbox,1,2)

		self.linelengthlabel = QtWidgets.QLabel()
		self.linelengthlabel.setObjectName('linelengthlabel')
		self.linelengthlabel.setText('line length')
		self.lineanglegrid.addWidget(self.linelengthlabel,0,2)

		self.gridlayout.addLayout(self.lineanglegrid,22,0,1,2)


		self.centralwidget.setLayout(self.gridlayout)

		super().setCentralWidget(self.centralwidget)
		super().setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar()
		self.menubar.setGeometry(QtCore.QRect(0, 0, 234, 21))
		self.menubar.setObjectName("menubar")
		super().setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar()
		self.statusbar.setObjectName("statusbar")
		super().setStatusBar(self.statusbar)

		self.gainBox.setValue(20)
		self.retranslateUi()
		QtCore.QMetaObject.connectSlotsByName(self)

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
		self.lineanglebox.valueChanged.connect(self.lineanglechange)
			
	def retranslateUi(self):
		_translate = QtCore.QCoreApplication.translate
		super().setWindowTitle(_translate("MainWindow", "rtsp GUI"))
		self.runButton.setText(_translate("MainWindow", "Let\'s gooooo!"))

		self.monitorxLabel.setText(_translate("MainWindow", "x image size on screen"))
		self.monitorxLabel.adjustSize()
		self.monitoryLabel.setText(_translate("MainWindow", "y image size on screen"))
		self.monitoryLabel.adjustSize()
		self.aspectInfoLabel.setText(_translate("MainWindow", "aspect ratio of image on screen will be "
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

		self.worker = Worker(address= rtspAdress, monitorx = monitorx,monitory = monitory,
		gain = gain, screenwidth = self.screenwidth, screenheight=self.screenheight, frameSkip = frameSkip,
		crosssize = crosssize,crossOffsetH = crossOffsetH, crossOffsetW = crossOffsetW, crossCheck = crossCheck, imageTime = imageTime, 
		imageDir = self.snapshotDir,lineCheck=self.lineCheckBox.isChecked(), linePosition=self.linePositionBox.value(), useGain = useGain,
		lineangle=self.lineanglebox.value(), linethickness=self.linethicknessbox.value(), linelength=self.linelengthbox.value())

		self.windowName = f'{rtspAdress} (press stop to close)'
		cv2.namedWindow(self.windowName)
		#moveWindow command requires an image to know it's aspect ratio
		#cv2.moveWindow(self.windowName,self.screenwidth-monitorx - 20,self.screenheight - monitory-100)

		'''
		self.newWindow = NewWindow()
		self.newWindow.setWindowTitle(rtspAdress)
		self.newWindow.show()
		'''
		
		self.thread = QtCore.QThread()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.run)
		self.worker.output.connect(self.windowUpdate)
		self.worker.streamNotFound.connect(self.stop_worker)
		self.thread.start()
		self.runButton.setEnabled(False)
	
	def windowUpdate(self, image):
		if self.running:
			cv2.imshow(self.windowName,image)
			#self.newWindow.frame.setPixmap(image)
	

	def stop_worker(self):
		self.worker.stop()
		self.thread.quit()
		self.worker.deleteLater()
		cv2.destroyAllWindows()
		self.runButton.setEnabled(True)
		self.stopButton.setEnabled(False)
		self.snapShotButton.setEnabled(False)
		self.imageSeriesButton.setEnabled(False)
		self.imageSeriesStopButton.setEnabled(False)
		self.thread.wait()
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
			self.worker.gain = self.gainBox.value()
	def changeGainCheck(self):
		if self.running:
			self.worker.useGain = self.gainCheck.isChecked()
	def changeSkip(self):
		if self.running:
			self.worker.frameSkip = self.frameSkipBox.value()
	def crossSizeChange(self):
		if self.running:
			self.worker.crosssize = self.crossSizeBox.value()
	def crossHChange(self):
		if self.running:
			self.worker.crossOffsetH = self.crossOffsetHBox.value()

	def crossWChange(self):
		if self.running:
			self.worker.crossOffsetW = self.crossOffsetWBox.value()
	
	def linePositionChange(self):
		if self.running:
			self.worker.linePosition = self.linePositionBox.value()
	def lineanglechange(self):
		if self.running:
			self.worker.lineangle = self.lineanglebox.value()

	def linethicknesschange(self):
		if self.running:
			self.worker.linethickness = self.linethicknessbox.value()
	
	def linelengthchange(self):
		if self.running:
			self.worker.linelength = self.linelengthbox.value()

	def lineCheckChange(self):
		if self.running:
			self.worker.lineCheck = self.lineCheckBox.isChecked()
	
	def crossCheckChange(self):
		if self.running:
			self.worker.crossCheck = self.crossCheckBox.isChecked()
		
	def changeMonitorx(self):
		monx = self.monitorxBox.value()
		mony = self.monitoryBox.value()
		if self.running:
			aspect = self.worker.aspect
			monx,mony = aspectAdjust(monx,mony,aspect)
			self.worker.monitorx = monx
			self.worker.monitory = mony

	def changeMonitory(self):
		monx = self.monitorxBox.value()
		mony = self.monitoryBox.value()
		if self.running:
			aspect = self.worker.aspect
			monx,mony = aspectAdjust(monx,mony,aspect)
			self.worker.monitory = mony
			self.worker.monitorx = monx

	def takeSingleImage(self):
		if self.running:
			self.worker.snapshot = True

	def takeImageSeries(self):
		if self.running:
			self.worker.imageSeries = True
			self.worker.imageTime = self.imageSeriesTime.value()
			self.worker.imageCountDown = 0
			self.imageSeriesButton.setEnabled(False)
			self.imageSeriesStopButton.setEnabled(True)

	def stopImageSeries(self):
		if self.running:
			self.worker.imageSeries = False
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
				self.worker.imageDir = folder
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
	def closeEvent(self, a0):
		if self.running:
			self.stop_worker()
		return super().closeEvent(a0)

def main():
	app = QtWidgets.QApplication(sys.argv)
	#MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi()
	ui.show()
	sys.exit(app.exec())
if __name__ == "__main__":
	main()

