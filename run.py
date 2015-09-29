# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from run_ui import Ui_runUI
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

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

class runUI(QtGui.QScrollArea, Ui_runUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)
        self.setupUi(self)
        
class runWidget(runUI):
    
    def __init__(self):
        runUI.__init__(self)
        self.solvername = 'icoFoam'

    def setCurrentFolder(self, currentFolder):
        self.currentFolder = currentFolder
        
    def runCase(self):
        filename = '%s/run.log'%self.currentFolder
        command = 'touch %s'%filename
        os.system(command)
        self.window().newLogTab('Run','%s/run.log'%self.currentFolder)
        command = '%s -case %s > %s &'%(self.solvername,self.currentFolder,filename)
        os.system(command)
        
    def changeType(self):
        if self.type_serial.isChecked():
            self.num_proc.setEnabled(False)
            self.reconstruct.setEnabled(False)
            self.pushButton_decompose.setEnabled(False)
        else:
            self.num_proc.setEnabled(True)
            self.reconstruct.setEnabled(True)
            self.pushButton_decompose.setEnabled(True)

    def resetCase(self):
        return

    def decomposeCase(self):
        return