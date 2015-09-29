# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from figureSampledLine_ui import figureSampledLineUI
import os

from myNavigationToolbar import *
from temporalNavigationToolbar import *
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

class figureSampledLine(figureSampledLineUI):

    def __init__(self):
        figureSampledLineUI.__init__(self)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.p1_x.setValidator(QtGui.QDoubleValidator())
        self.p1_y.setValidator(QtGui.QDoubleValidator())
        self.p1_z.setValidator(QtGui.QDoubleValidator())
        self.p2_x.setValidator(QtGui.QDoubleValidator())
        self.p2_y.setValidator(QtGui.QDoubleValidator())
        self.p2_z.setValidator(QtGui.QDoubleValidator())
        
    def getData(self):
        data = {}
        data['nsteps'] = self.spinBox.value()        
        data['field'] = self.comboBox.currentText()
        data['p1x'] = self.p1_x.text()
        data['p1y'] = self.p1_y.text()
        data['p1z'] = self.p1_z.text()
        data['p2x'] = self.p2_x.text()
        data['p2y'] = self.p2_y.text()
        data['p2z'] = self.p2_z.text()
        data['nop'] = self.nop.value()
        data['name'] = self.name.text()
        data['autorefreshing'] = self.autorefreshing.currentText()
        
        return data
        
    def setData(self,data):
        
        self.spinBox.setValue(data['nsteps']) if 'nsteps' in data.keys() else None
        self.nop.setValue(data['nop']) if 'nop' in data.keys() else None
        self.name.setText(data['name']) if 'name' in data.keys() else None
        
        #self.comboBox.setCurrentText(data['field']) if 'field' in data.keys()  else None
        #self.comboBox.setCurrentText(data['autorefreshing']) if 'autorefreshing' in data.keys() else None
        
        self.p1_x.setText(data['p1x']) if 'p1x' in data.keys() else None
        self.p1_y.setText(data['p1y']) if 'p1y' in data.keys() else None
        self.p1_z.setText(data['p1z']) if 'p1z' in data.keys() else None
        self.p2_x.setText(data['p2x']) if 'p2x' in data.keys() else None
        self.p2_y.setText(data['p2y']) if 'p2y' in data.keys() else None
        self.p2_z.setText(data['p2z']) if 'p2z' in data.keys() else None
        
        return data
        
    def ckeckAccept(self):

        allow = True

        if allow:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
            
class figureSampledLineWidget(QtGui.QWidget):

    def __init__(self, scrollAreaWidgetContents, dataname):         
        QtGui.QWidget.__init__(self)
        self.setParent(scrollAreaWidgetContents)
        fig = Figure((3.0, 2.0), dpi=100)
        canvas = FigureCanvas(fig)
        canvas.setParent(self)
        toolbar = myNavigationToolbar(canvas, self)
        temporal_toolbar = temporalNavigationToolbar(canvas, self)
        axes = fig.add_subplot(111)
        axes.autoscale(True)
        axes.set_yscale('log')
        axes.set_title(dataname)
        
         # place plot components in a layout
        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(temporal_toolbar)
        plotLayout.addWidget(canvas)
        plotLayout.addWidget(toolbar)
        self.setLayout(plotLayout)

        canvas.setMinimumSize(canvas.size())