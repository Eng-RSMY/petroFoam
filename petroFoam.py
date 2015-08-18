from PyQt4 import QtGui, QtCore
from petroFoam_ui import petroFoamUI
from popUpNew import *
import os
from math import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure


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

class petroFoam(petroFoamUI):
    def __init__(self):
        petroFoamUI.__init__(self)
        self.currentFolder = 'NONE'
        
        #self.plotsScrollArea
        #self.scrollAreaWidgetContents

        qscrollLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        qscrollLayout.setGeometry(QtCore.QRect(0, 0, 500, 300))
        
        qfigWidgets = [];
        for i in xrange(5):
          qfigWidgets.append(QtGui.QWidget(self.scrollAreaWidgetContents))
        
          fig = Figure((3.0, 2.0), dpi=100)
          canvas = FigureCanvas(fig)
          canvas.setParent(qfigWidgets[i])
          toolbar = NavigationToolbar(canvas, qfigWidgets[i])
          axes = fig.add_subplot(111)
          axes.plot([i+1,2,3,4])
        
          # create a simple widget to extend the navigation toolbar
          anotherWidget = QtGui.QPushButton()
          # add the new widget to the existing navigation toolbar
          toolbar.addWidget(anotherWidget)
          #actionDelete = QtGui.QAction(self)
          #icon7 = QtGui.QIcon()
          #icon7.addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/new16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
          #actionDelete.setIcon(icon7)
          #actionDelete.setObjectName(_fromUtf8("actionNew"))
          #QtCore.QObject.connect(actionDelete, QtCore.SIGNAL(_fromUtf8("activated()")), petroFoam.removeFigure)        
          #toolbar.insertWidget(actionDelete,anotherWidget)
          
        
          # place plot components in a layout
          plotLayout = QtGui.QVBoxLayout()
          plotLayout.addWidget(canvas)
          plotLayout.addWidget(toolbar)
          qfigWidgets[i].setLayout(plotLayout)
        
          # prevent the canvas to shrink beyond a point
          # original size looks like a good minimum size
          canvas.setMinimumSize(canvas.size())
        
          qscrollLayout.addWidget(qfigWidgets[i],i/2,i%2)
          
        self.scrollAreaWidgetContents.setLayout(qscrollLayout)
        
        removeItem = 2
        qscrollLayout.removeWidget(qfigWidgets[removeItem])
        qfigWidgets[removeItem].deleteLater()
        for i in xrange(removeItem+1,5):
            qfigWidgets[i-1] = qfigWidgets[i]
            qscrollLayout.addWidget(qfigWidgets[i-1],(i-1)/2,(i-1)%2)
            
    	
    def updateMeshPanel(self):
        QtGui.QMessageBox.about(self, "ERROR", "Primero se debe calcular!")

    def importMesh(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Mesh to Import', './', 'Mesh Files (*.msh)');
        print fileName

    def openCase(self):
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder', './');

    def saveAsCase(self):
        oldFolder = self.currentFolder        
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './');
        command = 'cp -r %s %s' % (oldFolder, self.currentFolder);
        os.system(command)

    def newCase(self):
        w = popUpNew()
        result = w.exec_()
        if result:
            data = w.getData()
            print 'a grabar en %s/%s'%(data[1],data[0])
        #self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './');
        #command = 'cp -r template_icoFoam %s' % self.currentFolder;
        #print command
        #os.system(command)
	
    def saveCase(self):
        if self.currentFolder=='NONE':
            self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './');
        print('Se guarda como %s',self.currentFolder)

    def openTerminal(self):
        os.system('gnome-terminal &')
        #os.system('$TERM . &')

    def openBrowse(self):
        os.system('nautilus . &')

    def closeEvent(self, evnt):
        print "se intenta cerrar"
        #evnt.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
    def removeFigure(self):
        print "removiendo"
        
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = petroFoam()
    window.show()
    sys.exit(app.exec_())
