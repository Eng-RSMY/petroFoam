# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from solutionModeling_ui import Ui_solutionModelingUI
import os
from tracers import *

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


class solutionModelingUI(QtGui.QScrollArea, Ui_solutionModelingUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class solutionModeling(solutionModelingUI):

    def __init__(self, currentFolder):
        solutionModelingUI.__init__(self)
        self.currentFolder = currentFolder
        
    def getData(self):
        data = {}
        return data
        
    def setData(self, data):
        return
        
    def aplicar(self):
        return
        
    def editTracers(self):
        w = tracers(self.currentFolder)
        result = w.exec_()
        if result:
            w.saveCaseData()
        