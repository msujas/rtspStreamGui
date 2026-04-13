# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.9.2

from PyQt6 import QtCore, QtGui, QtWidgets
from .rtspWorker import Worker, aspectAdjust
import cv2
from pathlib import Path
import os, sys


def stringToBool(string):
	return string == 'True'

type _parlist = list[ParAttributes]

class ParAttributes():
	def __init__(self, param):
		self.param = param
	def name(self):
		return self.param.objectName()
	def parValue(self):
		match type(self.param):
			case QtWidgets.QSpinBox | QtWidgets.QDoubleSpinBox: return self.param.value()
			case QtWidgets.QComboBox: return self.param.currentText()
			case QtWidgets.QLineEdit: return self.param.text()
			case QtWidgets.QCheckBox: return self.param.isChecked()
			case _: raise TypeError(f"{self.param}, type: {type(self.param)} not in listed types")
	def setValueFromText(self,strvalue:str):
		match type(self.param):
			case QtWidgets.QSpinBox: return self.param.setValue(int(strvalue))
			case QtWidgets.QDoubleSpinBox: return self.param.setValue(float(strvalue))
			case QtWidgets.QLineEdit: return self.param.setText(strvalue)
			case QtWidgets.QCheckBox: return self.param.setChecked(stringToBool(strvalue))
			case QtWidgets.QComboBox: return self.param.setCurrentText(strvalue)
			case _: raise TypeError(f'{self.param}, type: {type(self.param)} not in listed types')

class ParList():
	def __init__(self, alist:list=None):
		if not alist:
			self.list:_parlist = []
		elif not isinstance(alist,list):
			raise TypeError("alist must be list type")
		else:
			self.list:_parlist = [ParAttributes(item) for item in alist]
		
	def append(self, widget):
		self.list.append(ParAttributes(widget))
	def __contains__(self, item):
		return item in self.list or self.nameInList(item)
	def __getitem__(self, key):
		return self.list[key]
	def getWidgetFromName(self,name:str) -> ParAttributes:
		return [par for par in self.list if name == par.name()][0]
	def nameInList(self,name:str):
		return len([par for par in self.list if name == par.name()]) > 0


class Ui_MainWindow(QtWidgets.QMainWindow):
	def setupUi(self):
		super().setObjectName("rtsp GUI")
		super().setWindowTitle( "rtsp GUI")

		self.screen = QtWidgets.QApplication.primaryScreen().size()
		self.screenwidth = self.screen.width()
		self.screenheight = self.screen.height()
		iconfile = f'{os.path.dirname(os.path.realpath(__file__))}/image/icon.ico'
		icon = QtGui.QIcon(iconfile)
		super().setWindowIcon(icon)
		homepath = str(Path.home())
		endpath = 'Documents/rtspGuiSnapShots'
		self.snapshotDir = f'{homepath}/{endpath}/'
		if not os.path.exists(self.snapshotDir):
			os.makedirs(self.snapshotDir)
		scaling = (self.screenwidth/1920)**0.5 #scaling box and font sizes for different screen resolutions
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
		self.monitorxBox.setValue(1000)
		self.monitorxBox.setObjectName("monitorxBox")
		self.monitorxBox.setFont(boxfont)
		self.gridlayout.addWidget(self.monitorxBox, 5,0)

		self.monitorxLabel = QtWidgets.QLabel()
		self.monitorxLabel.setObjectName("monitorxLabel")
		self.monitorxLabel.setFont(labelfont)
		self.monitorxLabel.setText("x image size on screen")
		self.monitorxLabel.adjustSize()
		self.gridlayout.addWidget(self.monitorxLabel, 4,0)


		self.aspectInfoLabel = QtWidgets.QLabel()
		self.aspectInfoLabel.setFont(smallLabelfont)
		self.aspectInfoLabel.setObjectName("aspectInfoLabel")
		self.aspectInfoLabel.setText("aspect ratio of image on screen will be scaled automatically")
		self.aspectInfoLabel.adjustSize()
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
		self.gainLabel.setText("Gain (set Gain\nAuto to \'Off\')")
		self.gainLabel.adjustSize()
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
		self.runButton.setText("Let\'s gooooo!")
		self.gridlayout.addWidget(self.runButton,14,0,1,2)

		self.stopButton = QtWidgets.QPushButton()
		self.stopButton.setObjectName("stopButton")
		self.stopButton.setFont(font)
		self.stopButton.adjustSize()
		self.stopButton.setEnabled(False)
		self.stopButton.setText("Stop")
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

		self.linegrid = QtWidgets.QGridLayout()

		self.linePositionLabel = QtWidgets.QLabel()
		self.linePositionLabel.setObjectName('linePositionLabel')
		self.linePositionLabel.setText('line y position')
		self.linePositionLabel.setFont(labelfont)
		self.linePositionLabel.adjustSize()
		self.linegrid.addWidget(self.linePositionLabel,0,0)

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
		self.linegrid.addWidget(self.linePositionBox,1,0)

		self.lineCheckBox =  QtWidgets.QCheckBox() #select whether or not to display the cross
		self.lineCheckBox.setObjectName('lineCheckBox')
		self.lineCheckBox.setText('display line?')
		self.lineCheckBox.setFont(labelfont)
		self.lineCheckBox.setChecked(True)
		self.lineCheckBox.adjustSize()
		self.lineCheckBox.stateChanged.connect(self.lineCheckChange)
		self.lineCheckBox.stateChanged.connect(self.updateConfigLog)
		self.linegrid.addWidget(self.lineCheckBox,0,2)

		self.linexLabel = QtWidgets.QLabel()
		self.linexLabel.setObjectName('linexLabel')
		self.linexLabel.setText('line x position (from center)')
		self.linexLabel.setFont(labelfont)
		self.linexLabel.adjustSize()
		self.linegrid.addWidget(self.linexLabel,0,1)	

		self.linexposbox = QtWidgets.QSpinBox()
		self.linexposbox.setObjectName('linexposbox')
		self.linexposbox.setMaximum(3000)
		self.linexposbox.setMinimum(-3000)
		self.linexposbox.setEnabled(False)
		self.linexposbox.setKeyboardTracking(False)
		self.linegrid.addWidget(self.linexposbox, 1,1)
		self.linexposbox.valueChanged.connect(self.linexposchange)

		self.fixXbox = QtWidgets.QCheckBox()	
		self.fixXbox.setObjectName('fixXbox')
		self.fixXbox.setChecked(True)
		self.fixXbox.setText('fix line x to cross?')
		self.linegrid.addWidget(self.fixXbox, 1,2)
		self.fixXbox.stateChanged.connect(self.linexcheckchange)

		self.lineanglebox = QtWidgets.QDoubleSpinBox()
		self.lineanglebox.setObjectName("lineanglebox")
		self.lineanglebox.setValue(0)
		self.lineanglebox.setDecimals(1)
		self.lineanglebox.setSingleStep(0.1)
		self.lineanglebox.setMinimum(-89.9)
		self.lineanglebox.setMaximum(90)
		self.lineanglebox.setKeyboardTracking(False)
		self.linegrid.addWidget(self.lineanglebox, 3,0)

		self.lineanglelabel= QtWidgets.QLabel()
		self.lineanglelabel.setText('line angle')
		self.linegrid.addWidget(self.lineanglelabel, 2,0)

		self.linethicknessbox = QtWidgets.QSpinBox()
		self.linethicknessbox.setObjectName('linethicknessbox')
		self.linethicknessbox.setValue(3)
		self.linethicknessbox.setMinimum(1)
		self.linethicknessbox.setKeyboardTracking(False)
		self.linegrid.addWidget(self.linethicknessbox,3,1)
		self.linethicknessbox.valueChanged.connect(self.linethicknesschange)
		
		self.linethicknesslabel = QtWidgets.QLabel()
		self.linethicknesslabel.setText('line thickness')
		self.linethicknesslabel.setObjectName('linethicknesslabel')
		self.linegrid.addWidget(self.linethicknesslabel,2,1)

		self.linelengthbox = QtWidgets.QSpinBox()
		self.linelengthbox.setObjectName('linelengthbox')
		self.linelengthbox.setMaximum(1000)
		self.linelengthbox.setMinimum(1)
		self.linelengthbox.setValue(300)
		self.linelengthbox.setKeyboardTracking(False)
		self.linelengthbox.valueChanged.connect(self.linelengthchange)
		self.linegrid.addWidget(self.linelengthbox,3,2)

		self.linelengthlabel = QtWidgets.QLabel()
		self.linelengthlabel.setObjectName('linelengthlabel')
		self.linelengthlabel.setText('line length')
		self.linegrid.addWidget(self.linelengthlabel,2,2)

		self.gridlayout.addLayout(self.linegrid,22,0,1,2)


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
		QtCore.QMetaObject.connectSlotsByName(self)

		self.running = False

		self.updateParamList()
		self.settingsLog = f'{homepath}/rtspGuiConfig/rtspGUIconfiguration.log'
		self.addressLog = f'{homepath}/rtspGuiConfig/rtspAddresses.log'
		self.linexposbox.setValue(self.crossOffsetWBox.value())
		self.readConfigLog()
		self.readAddressLog()
		
		self.monitorxBox.setKeyboardTracking(False)


		self.gainBox.setKeyboardTracking(False)
		self.crossSizeBox.setKeyboardTracking(False)
		self.crossOffsetHBox.setKeyboardTracking(False)
		self.crossOffsetWBox.setKeyboardTracking(False)
		self.monitorxBox.valueChanged.connect(self.updateConfigLog)
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
		self.lockCrossPositionBox.stateChanged.connect(self.crossDisplayCheck)
		self.lockCrossPositionBox.stateChanged.connect(self.updateConfigLog)
		self.openDirectoryButton.clicked.connect(self.folderDialogue)
		self.rtspAddressesBox.currentTextChanged.connect(self.changeAddress)
		self.removeAddressButton.clicked.connect(self.removeAddress)
		self.lineanglebox.valueChanged.connect(self.lineanglechange)
			
	def start_worker(self):
		self.updateConfigLog()
		self.updateAddressLog()
		self.running = True
		self.stopButton.setEnabled(True)
		self.snapShotButton.setEnabled(True)
		self.imageSeriesButton.setEnabled(True)
		self.addAddress()

		rtspAdress = self.rtspAddressBox.text()
		monitorx = self.monitorxBox.value()
	
		frameSkip = self.frameSkipBox.value()
		gain = self.gainBox.value()		
		useGain = self.gainCheck.isChecked()
		
		crosssize = self.crossSizeBox.value()		
		crossOffsetH = self.crossOffsetHBox.value()		
		crossOffsetW = self.crossOffsetWBox.value()
		crossCheck = self.crossCheckBox.isChecked()
		imageTime = self.imageSeriesTime.value()

		self.worker = Worker(address= rtspAdress, monitorx = monitorx, gain = gain, screenwidth = self.screenwidth, 
		screenheight=self.screenheight, frameSkip = frameSkip,
		crosssize = crosssize,crossOffsetH = crossOffsetH, crossOffsetW = crossOffsetW, crossCheck = crossCheck, imageTime = imageTime, 
		imageDir = self.snapshotDir,lineCheck=self.lineCheckBox.isChecked(), linePosition=self.linePositionBox.value(), useGain = useGain,
		lineangle=self.lineanglebox.value(), linethickness=self.linethicknessbox.value(), linelength=self.linelengthbox.value(),
		linexoffset=self.linexposbox.value())

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
		self.updateConfigLog()
		self.running = False

	def updateParamList(self):
		self.params = ParList([self.rtspAddressBox,self.crossOffsetHBox, self.crossOffsetWBox,self.monitorxBox,self.gainBox,self.crossSizeBox,
				self.directoryBox,self.linePositionBox,self.lineCheckBox,self.frameSkipBox,self.gainCheck,self.linexposbox, self.fixXbox,
				self.lineanglebox])
	
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
		if not os.path.exists(self.addressLog):
			return
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
		if self.fixXbox.isChecked():
			self.linexposbox.setValue(self.crossOffsetWBox.value())
		if self.running:
			self.worker.crossOffsetW = self.crossOffsetWBox.value()
	
	def linePositionChange(self):
		if self.running:
			self.worker.linePosition = self.linePositionBox.value()
	def linexposchange(self):
		if self.running:
			self.worker.linexoffset = self.linexposbox.value()
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

	def linexcheckchange(self):
		self.linexposbox.setEnabled(not self.fixXbox.isChecked())
		if self.fixXbox.isChecked():
			self.linexposbox.setValue(self.crossOffsetWBox.value())

	def crossCheckChange(self):
		if self.running:
			self.worker.crossCheck = self.crossCheckBox.isChecked()
		
	def changeMonitorx(self):
		monx = self.monitorxBox.value()
		if self.running:
			aspect = self.worker.aspect
			mony = aspectAdjust(monx,aspect)
			self.worker.monitorx = monx
			self.worker.monitory = mony

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
		logUpdate = ''
		if not os.path.exists(os.path.dirname(self.settingsLog)):
			os.makedirs(os.path.dirname(self.settingsLog))
		for par in self.params:
			logUpdate += f'{par.name()};{par.parValue()}\n'
		f = open(self.settingsLog,'w')
		f.write(logUpdate)
		f.close()
	def readConfigLog(self):
		if not os.path.exists(self.settingsLog):
			return
		f = open(self.settingsLog,'r')
		lines = f.readlines()
		f.close()
		for line in lines:
			parname = line.split(';')[0]
			parvalue = line.split(';')[1].replace('\n','')
			if parname not in self.params:
				print(f'{parname} not in parameter list')
				continue
			par = self.params.getWidgetFromName(parname)
			par.setValueFromText(parvalue)
	def closeEvent(self, a0):
		if self.running:
			self.stop_worker()
		#self.updateConfigLog()
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

