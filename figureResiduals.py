# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from figureResiduals_ui import figureResidualsUI
import os

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

class figureResiduals(figureResidualsUI):

    def __init__(self):
        figureResidualsUI.__init__(self)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
    def getData(self):
        data = {}
        data['name'] = self.name.text()
        data['nsteps'] = self.spinBox.value()        
        data['fields'] = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState() == QtCore.Qt.Checked:
                data['fields'].append(self.listWidget.item(i))
        
        return data
        
    def setData(self, data):
        self.name.setText(data['name']) if 'name' in data.keys() else None
        self.spinBox.setValue(data['nsteps']) if 'nsteps' in data.keys() else None
        
        if 'fields' in data.keys():
            for i in range(self.listWidget.count()):
                if self.listWidget.item(i) in data['fields']:
                    self.listWidget.item(i).setCheckState(QtCore.Qt.Checked)
                else:
                    self.listWidget.item(i).setCheckState(QtCore.Qt.Unchecked)
                    
        return data
        
    def ckeckAccept(self, evnt):

        allow = False
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState() == QtCore.Qt.Checked:
                allow = True
                break
        if allow:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
            