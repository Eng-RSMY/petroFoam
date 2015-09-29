# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from postpro_ui import Ui_postproUI
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

class postproUI(QtGui.QScrollArea, Ui_postproUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)
        self.setupUi(self)
        
class postproWidget(postproUI):
    
    def __init__(self):
        postproUI.__init__(self)

    def setCurrentFolder(self, currentFolder):
        self.currentFolder = currentFolder
        
    def openParaview(self):
        os.system('paraFoam -builtin -case %s &'%self.currentFolder)

    def exportData(self):
        return
    
    def calculate1(self):
        return

    def calculate2(self):
        return
        
    def calculate3(self):
        return
    