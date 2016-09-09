# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EIT_Measurement_Automation_UI.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from scipy import interpolate
import numpy as np
import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
import sys
import pyautogui
import os
import time

'''
Browse buttons, calibrate windows, and begin measurements buttons are functional.
A check for calibration is made before "begin measurements" is able to run.
Make a check so that the user must enter a "save measured data with prefix"
before begin measurements is taken.
1.Begin functionality for process data button.  Remember: we're currently
processing that data for one(1) portion of measurements, not the entire thing,
so this makes the algorithm much easier.  However, also write the code to
process everything
2.Begin functionality for Generate Image button.  In other words, interface
the python code with the matlab code to allow interpolated images to be
rendered through the python app.  Will i need matlab installed?

ORGANIZE AND COMMENT CODE!!!

UPDATE:
In the calibrated skin imp function, make it so that before begin measurements
is called, we change the file name that we're storing to "Calibrated skin
Impedance" , then after that's over, change the file name we're storing to back
to the user's input.

-- Added checkbox.  Make a check function for process data button.
If checked - fill in calculated skin impedance value, if not checked, make a separate
file for the measured values.

--   Make sure all exception handling is done.
Left off after adding functionality for exclusive single point/entire image
check boxes. Now, we need to add the functionality to process the entire image.
Also, we need to add a pop-up window for when the user wants to generate an "entire image".
In this pop-up window get the number of rows and columns of the image. Will possibly need
a global list whose indices  are the alphabet.'''



arduinoXPos, arduinoYPos, sweepX, sweepY, saveDataX, saveDataY, calibrated = 0, 0, 0, 0, 0, 0, False

listOfPairs = [ [0,1], [1,2], [2,3],
                [4,5], [5,6], [6,7],
                [8,9], [9,'a'], ['a','b'],
                ['c','d'],['d','e'],['e','f'] ]

listOfColumns = ["A", "B", "C", "D", "E", "F", "G", "H", "I",
                 "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
                 "T","U","V","W","X","Y","Z"]
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Form2(QtGui.QDialog):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.rows = 0
        self.columns = 0
        self.setupUi(self)
        

        
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(230, 127)
        self.centralwidget = QtGui.QWidget(Form)
        
        self.rows_lbl = QtGui.QLabel(self.centralwidget)
        self.rows_lbl.setGeometry(QtCore.QRect(10,4,100,30))
        
        self.columns_lbl = QtGui.QLabel(self.centralwidget)
        self.columns_lbl.setGeometry(QtCore.QRect(10,64,100,30))
        
        self.rows_txt = QtGui.QLineEdit(self.centralwidget)
        self.rows_txt.setGeometry(QtCore.QRect(10,30,100,30))
        
        self.columns_txt = QtGui.QLineEdit(self.centralwidget)
        self.columns_txt.setGeometry(QtCore.QRect(10,90,100,30))      

        self.complete_btn = QtGui.QPushButton(self.centralwidget)
        self.complete_btn.setGeometry(QtCore.QRect(120,90,100,30))

        self.connect(self.complete_btn,QtCore.SIGNAL("clicked()"),self.close)
        
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.rows_lbl.setText(_translate("Form", "Rows:",None))
        self.columns_lbl.setText(_translate("Form","Columns:",None))
        self.complete_btn.setText(_translate("Form","Continue", None))

    def returnButtonPressed(self):
        self.rows = str(self.rows_txt.text())
        self.columns = str(self.columns_txt.text())
        self.close
        print("complete")

        

class Ui_MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setFixedSize(820,330)
        self.centralwidget = QtGui.QWidget(MainWindow)
        #self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        ################            CHECK BOX                    #################3
        self.calibrateSkinCheckBox = QtGui.QCheckBox(self.centralwidget)
        self.calibrateSkinCheckBox.setGeometry(QtCore.QRect(150,150, 30,30))
        #self.calibrateSkinCheckBox.setObjectName(_fromUtf8("calibrateSkinCheckBox"))
        ################             BUTTONS                     ##################
        self.calibratedSkinImp_btn = QtGui.QPushButton(self.centralwidget)
        self.calibratedSkinImp_btn.setGeometry(QtCore.QRect(630,35,131,31))
       # self.calibratedSkinImp_btn.setObjectName(_fromUtf8("calibratedSkinImp_btn"))

        self.buttonGroup = QtGui.QButtonGroup()
        self.pointImage_cBox = QtGui.QCheckBox(self.centralwidget)
        self.entireImage_cBox = QtGui.QCheckBox(self.centralwidget)
        self.buttonGroup.addButton(self.pointImage_cBox,1)
        self.buttonGroup.addButton(self.entireImage_cBox,2)

        self.pointImage_cBox.setGeometry(QtCore.QRect(400,150,30,30))
        self.entireImage_cBox.setGeometry(QtCore.QRect(400,180,30,30))
        
        " 'Calibrate Windows' BUTTON"
        self.calibrateWindows_btn = QtGui.QPushButton(self.centralwidget)
        self.calibrateWindows_btn.setGeometry(QtCore.QRect(10, 250, 181, 34))
      #  self.calibrateWindows_btn.setObjectName(_fromUtf8("calibrateWindows_btn"))

        " 'Begin Measurements' BUTTON "
        self.beginMeasurements_btn = QtGui.QPushButton(self.centralwidget)
        self.beginMeasurements_btn.setGeometry(QtCore.QRect(610, 260, 181, 34))
       # self.beginMeasurements_btn.setObjectName(_fromUtf8("beginMeasurements_btn"))

        " 'Process Data' BUTTON "
        self.processData_btn = QtGui.QPushButton(self.centralwidget)
        self.processData_btn.setGeometry(QtCore.QRect(20, 150, 121, 34))
        #self.processData_btn.setObjectName(_fromUtf8("processData_btn"))

        " 'Generate Image' BUTTON "
        self.generateImage_btn = QtGui.QPushButton(self.centralwidget)
        self.generateImage_btn.setGeometry(QtCore.QRect(630, 150, 131, 34))
        #self.generateImage_btn.setObjectName(_fromUtf8("generateImage_btn"))

        " 'Process from' BROWSE BUTTON "
        self.processBrowse_btn = QtGui.QPushButton(self.centralwidget)
        self.processBrowse_btn.setGeometry(QtCore.QRect(250, 100, 112, 30))
       # self.processBrowse_btn.setObjectName(_fromUtf8("processBrowse_btn"))

        " 'Generate image from file' BROWSE BUTTON"
        self.imageBrowse_btn = QtGui.QPushButton(self.centralwidget)
        self.imageBrowse_btn.setGeometry(QtCore.QRect(631, 100, 131, 30))
        #self.imageBrowse_btn.setObjectName(_fromUtf8("imageBrowse_btn"))

        ################             TEXT BOXES                     ##################
        " 'Saved processed data as' TEXTBOX "
        self.saveProcessedAs_txt = QtGui.QLineEdit(self.centralwidget)
        self.saveProcessedAs_txt.setGeometry(QtCore.QRect(20, 40, 211, 27))
        #self.saveProcessedAs_txt.setObjectName(_fromUtf8("saveProcessedAs_txt"))

        " 'Process from' TEXTBOX "
        self.processFromDir_txt = QtGui.QLineEdit(self.centralwidget)
        self.processFromDir_txt.setGeometry(QtCore.QRect(20, 100, 211, 27))
       # self.processFromDir_txt.setObjectName(_fromUtf8("processFromDir_txt"))

        " 'Calibrated skin Impedance' TEXTBOX "
        self.calibratedSkinImp_txt = QtGui.QLineEdit(self.centralwidget)
        self.calibratedSkinImp_txt.setGeometry(QtCore.QRect(390, 40, 221, 27))
        #self.calibratedSkinImp_txt.setText(_fromUtf8(""))
        #self.calibratedSkinImp_txt.setObjectName(_fromUtf8("calibratedSkinImp_txt"))

        " 'Save measured data with prefix' TEXTBOX"
        self.saveMeasuredAs_txt = QtGui.QLineEdit(self.centralwidget)
        self.saveMeasuredAs_txt.setGeometry(QtCore.QRect(300, 260, 301, 27))
      #  self.saveMeasuredAs_txt.setObjectName(_fromUtf8("saveMeasuredAs_txt"))

        " 'Generate Image from file' TEXTBOX"
        self.generateImgDir_txt = QtGui.QLineEdit(self.centralwidget)
        self.generateImgDir_txt.setGeometry(QtCore.QRect(390, 100, 221, 27))
     #   self.generateImgDir_txt.setObjectName(_fromUtf8("generateImgDir_txt"))
        
        ################             LABELS                     ##################
        self.pointImage_lbl = QtGui.QLabel(self.centralwidget)
        self.pointImage_lbl.setGeometry(QtCore.QRect(430,150,100,30))

        self.entireImage_lbl = QtGui.QLabel(self.centralwidget)
        self.entireImage_lbl.setGeometry(QtCore.QRect(430,180,100,30))
                            
         
        self.savedProcessedAs_lbl = QtGui.QLabel(self.centralwidget)
        self.savedProcessedAs_lbl.setGeometry(QtCore.QRect(20, 10, 181, 31))
      #  self.savedProcessedAs_lbl.setObjectName(_fromUtf8("savedProcessedAs_lbl"))

        self.processCheckBox_lbl = QtGui.QLabel(self.centralwidget)
        self.processCheckBox_lbl.setGeometry(QtCore.QRect(180,150,181,31))
        #self.processCheckBox_lbl.setObjectName(_fromUtf8("processCheckBox_lbl"))
        
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 80, 101, 21))
       # self.label_2.setObjectName(_fromUtf8("label_2"))


        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(400, 20, 201, 16))
        #self.label_3.setObjectName(_fromUtf8("label_3"))

        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(400, 80, 191, 21))
     #   self.label_4.setObjectName(_fromUtf8("label_4"))


        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(310, 230, 251, 21))
     #   self.label_5.setObjectName(_fromUtf8("label_5"))

        ############################################################################

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 819, 31))
       # self.menubar.setObjectName(_fromUtf8("menubar"))

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        #self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.processCheckBox_lbl.setText(_translate("MainWindow", "(Skin calibration)",None))
        MainWindow.setWindowTitle(_translate("MainWindow", "EIT Measurement Automation", None))
        self.calibratedSkinImp_btn.setText(_translate("MainWindow", "Calculate", None))
        self.calibrateWindows_btn.setText(_translate("MainWindow", "Calibrate Windows", None))
        self.savedProcessedAs_lbl.setText(_translate("MainWindow", "Save processed data as:", None))
        self.beginMeasurements_btn.setText(_translate("MainWindow", "Begin Measurements", None))
        self.label_2.setText(_translate("MainWindow", "Process from:", None))
        self.processBrowse_btn.setText(_translate("MainWindow", "Browse", None))
        self.processData_btn.setText(_translate("MainWindow", "Process Data", None))
        self.generateImage_btn.setText(_translate("MainWindow", "Generate Image", None))
        self.label_3.setText(_translate("MainWindow", "Caibrated skin impedance:", None))
        self.label_4.setText(_translate("MainWindow", "Generate image from file:", None))
        self.imageBrowse_btn.setText(_translate("MainWindow", "Browse", None))
        self.label_5.setText(_translate("MainWindow", "Save measured data with prefix:", None))
        self.pointImage_lbl.setText(_translate("MainWindow", "Single point",None))
        self.entireImage_lbl.setText(_translate("MainWindow", "Entire Image",None))

        self.processData_btn.clicked.connect(self.processData)
        self.calibratedSkinImp_btn.clicked.connect(self.measureCalibratedSkinImp)
        self.processBrowse_btn.clicked.connect(self.processBrowseClicked)
        self.imageBrowse_btn.clicked.connect(self.imageBrowseClicked)
        self.calibrateWindows_btn.clicked.connect(self.calibrateWindowsClicked)
        self.beginMeasurements_btn.clicked.connect(self.beginMeasurementsClicked)
        self.generateImage_btn.clicked.connect(self.generateImage)

    def processPointImageData(self,savedFileName, path):
        currentColumn = 0
            
        with open(savedFileName, 'w') as newFile:
            for dir_entry in os.listdir(path):
                print(path + dir_entry)
                dir_entry_path = os.path.join(path,dir_entry)
                if os.path.isfile(dir_entry_path):
                    with open(dir_entry_path, 'r') as impedanceFile:
                        impedance = impedanceFile.readline()
                        impedance = impedanceFile.readline()
                        tempListOfCSV = impedance.split(",")
                        impedance = tempListOfCSV[1]
                        if currentColumn < 2:
                            newFile.write(impedance + ",")
                            currentColumn += 1
                        elif currentColumn == 2:
                            newFile.write(impedance + "\n")
                            currentColumn = 0
            '''Normalization of outliers , essentially saying if we have
    an extremely high outlier, substitute it with a not as high value (20000)
    Generally, anything above 30k tends to be extremely above 30k, so it's save
    to assume anything above 30k is an extremely high outlier'''

            'Return to beginning of file'
        lines = []
        with open(savedFileName, 'r') as newFile:
            for fileLine in newFile:
                
                line = str(fileLine)
                impedancesOfRow = line.split(",")
                for column in range(3):
                    #print(impedancesOfRow[column] + '\n')
                    if int(impedancesOfRow[column]) > 30000:
                        print (impedancesOfRow[column])
                        if column == 2:
                            fileLine = fileLine.replace(impedancesOfRow[column], str(15000) + '\n')
                        else:
                            fileLine = fileLine.replace(impedancesOfRow[column], str(15000))
                lines.append(fileLine)
        with open(savedFileName, 'w') as newFile:
            for line in lines:
                newFile.write(line)
                                          
                            
    def processEntireImageData(self,savedFileName,path):
        currentColumn = 0
        currentRow = 0
        currentArrayPos = 0
        rows,columns = self.getDataInfo()
        listOfData = [[]]
        
        with open(savedFileName, 'w') as newFile:
            for dir_entry in os.listdir(path):
                
                print(path + dir_entry)
                print("Current column: " + str(currentColumn))
                dir_entry_path = os.path.join(path,dir_entry)
                if os.path.isfile(dir_entry_path):
                    with open(dir_entry_path, 'r') as impedanceFile:
                        impedance = impedanceFile.readline()
                        impedance = impedanceFile.readline()
                        tempListOfCSV = impedance.split(",")
                        impedance = tempListOfCSV[1]


                        ##This check isn't correct
                        if currentColumn < (columns*3)-1:
                            listOfData[currentRow].append(str(impedance))
                            #newFile.write(impedance + ",")
                            currentColumn += 1
                            
                        elif currentColumn == (columns*3)-1:
                            listOfData[currentRow].append(str(impedance))
                            currentColumn +=1
                            
                            if currentColumn >= (columns*3):
                                currentColumn = 0
                                currentRow +=1
                                
            for row in range(len(listOfData)):
                for column in range(len(listOfData[row])):
                    if column == len(listOfData[row]):
                        newFile.write(impedance)
                    else:
                        newFile.write(impedance + "\n")
                                
        
        
    def processData(self, path = ""):
        try:
            if self.calibrateSkinCheckBox.isChecked():
                if str(self.saveProcessedAs_txt.text()) == "":
                    savedFileName = "Processed Calibrated Skin Impedance.txt"
                else:
                    savedFileName = str(self.saveProcessedAs_txt.text())
            else:
                
                if str(self.saveProcessedAs_txt.text()) == "":
                    
                    raise IOError('You must enter a name to save the processed data as.')
                    
                
                savedFileName = str(self.saveProcessedAs_txt.text()) + ".txt"
            

            if not self.pointImage_cBox.isChecked() and not self.entireImage_cBox.isChecked():
                QtGui.QMessageBox.warning(self,"Warning","Must select to either process the data for a single point array measurement or an entire phantom")
                return
            
        #QtGui.QMessageBox.about(self,"Warning", "You must calibrate the screen before beginning measurements")
        
            
            if not path:
                path = str(self.processFromDir_txt.text())
                
            if self.pointImage_cBox.isChecked():
                self.processPointImageData(savedFileName,path)
            else:
                self.processEntireImageData(savedFileName,path)
                                           
            
        
        #except IOError:
         #   QtGui.QMessageBox.warning(self,"Error", "You must enter a name under 'Save processed data as' if you want to process data that is not for skin calibration processing.")
          #  return
        except WindowsError:
            QtGui.QMessageBox.warning(self,"Invalid File Path", "Could not find the path specified: '" + path + "'")
            return
        except IndexError:
            QtGui.QMessageBox.warning(self,"Invalid File Data", "An error has occured while trying to process a file:\n ")
            return
        
        QtGui.QMessageBox.about(self,"Success", "Processing data successful")
        
        if self.calibrateSkinCheckBox.isChecked():
            self.calculateCalibratedSkinImp()
            
    def measureCalibratedSkinImp(self):
        '''UPDATE HERE"
'''
        global calibrated
        if calibrated:
            self.takeMeasurements("Calibrated_Skin_Impedance")
            QtGui.QMessageBox.about(self,"Complete", "Select the folder in which you've saved the skin measurements")
            self.calibrateSkinCheckBox.setCheckState(QtCore.Qt.Checked)
            
            path = str(QtGui.QFileDialog.getExistingDirectory(self,"Select Directory"))
            self.processData(path)
           #### 
            self.calculateCalibratedSkinImp()
            
            
        else:
            QtGui.QMessageBox.warning(self,"Warning", "You must calibrate the screen before beginning measurements")


    def calculateCalibratedSkinImp(self):
        path = os.path.join(os.getcwd(),"Processed Calibrated Skin Impedance.txt")
        data = np,genfromtxt(path, delimiter = ',')
        self.calibratedSkinImp_txt.setText( str( np.mean( data ) ) )

    def getDataInfo(self):
        getInfo = Form2()
        getInfo.exec_()
        rows = int(getInfo.rows_txt.text())  
        columns = int(getInfo.columns_txt.text()) 
        return (rows,columns)
    
    def generateImage(self):

        if not self.pointImage_cBox.isChecked() and not self.entireImage_cBox.isChecked():
            QtGui.QMessageBox.warning(self,"Warning","Must select to either generate the image for a single point array measurement or an entire phantom")
            return
        try: 
            imgDir = str(self.generateImgDir_txt.text())
            print(imgDir)
            print('didnt get the data')
            data = np.genfromtxt( imgDir, delimiter = ',' )
            data = data.transpose()
            print('got the data')
            "Interpolate the data 5 times"
            #maybe do a few more interpolations if we're doing a single point image
            for i in range ( 5 ):
                columns = len( data[ 0 ] )
                rows = len( data )
                columnsRange = np.linspace( 1, columns, columns )
                rowsRange = np.linspace( 1, rows, rows )

                interpolation = interpolate.interp2d( columnsRange, rowsRange, data, kind = 'linear' )
                ##mimicking the new size of an interpolated data set in matlab ( n -> 2n-1 )
                newColumnsRange = np.linspace( 1, columns, 2*columns - 1)
                newRowsRange = np.linspace( 1, rows, 2*rows - 1)
                data = interpolation( newColumnsRange, newRowsRange )
                
            impedanceStdev = np.std( data )
            minImpedance = float( self.calibratedSkinImp_txt.text() ) - impedanceStdev
            maxImpedance = float( self.calibratedSkinImp_txt.text() ) + impedanceStdev
            
            fig, ax = plt.subplots()
            cax = ax.imshow( data, interpolation = 'nearest', cmap = cm.RdYlBu, vmin = minImpedance, vmax = maxImpedance )
            cbar = fig.colorbar( cax )
            plt.show()   
            
        except matlab.engine.MatlabExecutionError:
            if self.pointImage_cBox.isChecked():
                QtGui.QMessageBox.warning(self,"Warning","Invalid path for generating image")
            else:
                QtGui.QMessageBox.warning(self,"Warning","Invalid row or column input")
            return 
        except ValueError:
            QtGui.QMessageBox.warning(self,"Warning","Invalid row or column input")
            return
        except IndexError:
            QtGui.QMessageBox.warning(self,"Warning","Invalid row or column input")
            return
            
        except ValueError:
            QtGui.QMessageBox.warning(self,"Warning","Invalid skin calibration impedance value.")
            return


    def takeMeasurements(self, savedFileName):
        global arduinoXPos, arduinoYPos, sweepX, sweepY, saveDataX, saveDataY, listOfPairs, calibrated

        if calibrated:
            for subList in listOfPairs:
                pyautogui.moveTo(arduinoXPos, arduinoYPos)
                pyautogui.click()
                pyautogui.moveTo(1,1,0.5)
                pyautogui.typewrite('a' + str(subList[0]) + '\n')
                pyautogui.typewrite('b' + str(subList[1]) + '\n')
                pyautogui.moveTo(sweepX,sweepY)
                pyautogui.click()
                'This "move to" is to wait for the sweep to finish'
                pyautogui.moveTo(1,1,1.2)
                pyautogui.typewrite('\n')
                pyautogui.moveTo(saveDataX,saveDataY)
                pyautogui.click()
                pyautogui.moveTo(1,1,1)
                pyautogui.typewrite(savedFileName + 'a' + str(subList[0]) + 'b' + str(subList[1]) + '\n')
        else:
            QtGui.QMessageBox.about(self,"Warning", "You must calibrate the screen before beginning measurements")

    def beginMeasurementsClicked(self):
        self.takeMeasurements(str(self.saveMeasuredAs_txt.text()))
       

    def calibrateWindowsClicked(self):
        global arduinoXPos, arduinoYPos, sweepX, sweepY, saveDataX, saveDataY, calibrated
        calibrated = True
        
        QtGui.QMessageBox.about(self,"Calibration", "Place the cursor on the arduino text box position and press enter.")
        arduinoXPos, arduinoYPos = pyautogui.position()

        QtGui.QMessageBox.about(self,"Calibration", "Place the cursor on the Eval Software 'Start Sweep' position and press enter.")
        sweepX, sweepY = pyautogui.position()

        QtGui.QMessageBox.about(self,"Calibration", "Place the cursor on the Eval Software 'Download Impedance Data' position and press enter.")
        saveDataX, saveDataY = pyautogui.position()

        QtGui.QMessageBox.about(self,"Success!", "Calibration successful!")
        
    def processBrowseClicked(self):
        self.processFromDir_txt.setText(QtGui.QFileDialog.getExistingDirectory(self,"Select Directory"))

    def imageBrowseClicked(self):
        self.generateImgDir_txt.setText(QtGui.QFileDialog.getOpenFileName(self))

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Ui_MainWindow()
    ex.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()

