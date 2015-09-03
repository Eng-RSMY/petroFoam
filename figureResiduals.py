# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from figureResiduals_ui import figureResidualsUI
from myNavigationToolbar import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
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
            
            
class figureResidualsWidget(QtGui.QWidget):

    def __init__(self, scrollAreaWidgetContents):         
        QtGui.QWidget.__init__(self)
        self.setParent(scrollAreaWidgetContents)
        fig = Figure((3.0, 2.0), dpi=100)
        canvas = FigureCanvas(fig)
        canvas.setParent(self)
        toolbar = myNavigationToolbar(canvas, self)
        axes = fig.add_subplot(111)
        axes.autoscale(True)
        axes.set_yscale('log')
        axes.set_title('Residuals')
        axes.set_xlabel('Time [s]')
        axes.set_ylabel('|R|')

         # place plot components in a layout
        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(canvas)
        plotLayout.addWidget(toolbar)
        self.setLayout(plotLayout)

        # prevent the canvas to shrink beyond a point
        #original size looks like a good minimum size
        canvas.setMinimumSize(canvas.size())

    def plot(self, data):
        axes.clear()
        line0 = axes.plot(self.dataPlot['residuals.dat'][:,0],self.dataPlot['residuals.dat'][:,1],'r', label="U")
        line1 = axes.plot(self.dataPlot['residuals.dat'][:,0],self.dataPlot['residuals.dat'][:,2],'b', label="p")
        miny = numpy.amin(self.dataPlot['residuals.dat'][:,1:3])
        maxy = miny*1e3
        axes.set_ylim(miny,maxy)
        axes.set_yscale('log')

        axes.set_title('Residuals')
        axes.set_xlabel('Time [s]')
        axes.set_ylabel('|R|')
        axes.legend(loc=1, fontsize = 'small')

        canvas.draw()