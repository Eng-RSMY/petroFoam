from PyQt4 import QtGui, QtCore
from petroFoam_ui import petroFoamUI
from popUpNew import *
from popUpNewFigure import *
from myNavigationToolbar import *
import os
from math import *
import time
import threading
import numpy
import pickle

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pylab

from utils import command_window

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
        self.currentFolder = '.'
        
        #clase que chequea actualizaciones de directorios y archivos
        self.fs_watcher = QtCore.QFileSystemWatcher() 
        self.fs_watcher.fileChanged.connect(self.file_changed)
        
        self.pending_files = []
        self.update_watcher()
        
        #self.controlDict['startTime'] = 0
        self.solvername = 'icoFoam'
        
        self.lastPos = {}
        self.typeFile = {}
        self.dataPlot = {}
        
        self.qscrollLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.qscrollLayout.setGeometry(QtCore.QRect(0, 0, 500, 300))
        self.qfigWidgets = [];
        self.nPlots = 0
        
        self.qfigWidgets.append(QtGui.QPushButton(self.scrollAreaWidgetContents))
        self.qfigWidgets[self.nPlots].setText(_fromUtf8("New Figure"))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/monitoringFunction16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.qfigWidgets[self.nPlots].setIcon(icon3)
        self.qfigWidgets[self.nPlots].setObjectName(_fromUtf8("newFigureButton"))
        self.qscrollLayout.addWidget(self.qfigWidgets[self.nPlots],self.nPlots/2,self.nPlots%2)
        QtCore.QObject.connect(self.qfigWidgets[self.nPlots], QtCore.SIGNAL(_fromUtf8("pressed()")), self.addNewFigure)
                  
        self.scrollAreaWidgetContents.setLayout(self.qscrollLayout)
        
        QtCore.QObject.connect(self.tabWidget_2, QtCore.SIGNAL("tabCloseRequested(int)"), self.closeLogTab)
        
    	
    def updateMeshPanel(self):
        QtGui.QMessageBox.about(self, "ERROR", "Primero se debe calcular!")

    def importMesh(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Mesh to Import', './', 'Mesh Files (*.msh)');
        print fileName

    def openCase(self):
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder', './');
        self.load_config()

    def saveAsCase(self):
        oldFolder = self.currentFolder        
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './');
        command = 'cp -r %s %s' % (oldFolder, self.currentFolder);
        os.system(command)
        self.save_config()

    def newCase(self):
        w = popUpNew()
        result = w.exec_()
        if result:
            data = w.getData()
            print 'a grabar en %s'%os.path.join(data[1],data[0])
            self.currentFolder = os.path.join(data[1],data[0]);
            command = 'cp -r template_icoFoam %s' % self.currentFolder;
            os.system(command)
	
    def saveCase(self):
        if self.currentFolder=='.':
            self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './');
        print('Se guarda como %s',self.currentFolder)
        self.save_config()

    def openTerminal(self):
        os.system('gnome-terminal --working-directory=%s &'%self.currentFolder)
        #os.system('$TERM . &')

    def openBrowse(self):
        os.system('nautilus %s &'%self.currentFolder)

    def closeEvent(self, evnt):
        print "se intenta cerrar"
        #evnt.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
    def removeFigure(self, figW):
        removeItem = 0
        for i in xrange(self.nPlots):
            if figW==self.qfigWidgets[i]:
                removeItem = i
                break
            
        self.qscrollLayout.removeWidget(self.qfigWidgets[removeItem])
        self.qfigWidgets[removeItem].deleteLater()
        for i in xrange(removeItem+1,self.nPlots+1): #voy hasta +1 porque tengo el boton
            self.qfigWidgets[i-1] = self.qfigWidgets[i]
            self.qscrollLayout.addWidget(self.qfigWidgets[i-1],(i-1)/2,(i-1)%2)
        self.nPlots = self.nPlots-1
        
        
    def createMesh(self):
        command = 'touch %s/createMesh.log'%self.currentFolder
        os.system(command)
        self.newLogTab('Create Mesh','%s/createMesh.log'%self.currentFolder)
        command = 'blockMesh -case %s > %s/createMesh.log &'%(self.currentFolder,self.currentFolder)
        os.system(command)
        #command = 'foamClearPolyMesh -case %s'%self.currentFolder
        #os.system(command)
        
    def checkMesh(self):
        command = 'touch %s/checkMesh.log'%self.currentFolder
        os.system(command)
        self.newLogTab('Check Mesh','%s/checkMesh.log'%self.currentFolder)
        command = 'checkMesh -case %s > %s/checkMesh.log &'%(self.currentFolder,self.currentFolder)
        os.system(command)
                
    def runCase(self):
        
        filename = '%s/run.log'%self.currentFolder
        command = 'touch %s'%filename
        os.system(command)
        self.newLogTab('Run','%s/run.log'%self.currentFolder)
        command = '%s -case %s > %s &'%(self.solvername,self.currentFolder,filename)
        os.system(command)
        
        
    def addNewFigure(self):
        w = popUpNewFigure()
        result = w.exec_()
        if result:
            data = w.getData()
            if(data=='Residuals'):
                i = self.nPlots
                self.qfigWidgets.insert(i, QtGui.QWidget(self.scrollAreaWidgetContents))
                fig = Figure((3.0, 2.0), dpi=100)
                canvas = FigureCanvas(fig)
                canvas.setParent(self.qfigWidgets[i])
                toolbar = myNavigationToolbar(canvas, self.qfigWidgets[i])
                axes = fig.add_subplot(111)
                axes.autoscale(True)
                
                 # place plot components in a layout
                plotLayout = QtGui.QVBoxLayout()
                plotLayout.addWidget(canvas)
                plotLayout.addWidget(toolbar)
                self.qfigWidgets[i].setLayout(plotLayout)
                
                # prevent the canvas to shrink beyond a point
                #original size looks like a good minimum size
                canvas.setMinimumSize(canvas.size())
                #quito el boton
                #self.qscrollLayout.removeWidget(self.qfigWidgets[i+1])
                #agrego el nuevo plot                
                self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)                
                #vuelvo a ubicar el boton
                self.qscrollLayout.addWidget(self.qfigWidgets[i+1],(i+1)/2,(i+1)%2)
                self.nPlots = self.nPlots+1
        
                #Agrego un watcher al residual
                #Como no se aun en que paso de tiempo voy a empezar, tengo que tener cuidado aca
                filename = 'postProcessing/residuals/0/residuals.dat'
                self.pending_files.append(filename)
                self.qfigWidgets[i].setObjectName('residuals.dat')
                self.lastPos['residuals.dat'] = 2
                self.dataPlot['residuals.dat'] = []
                
                
    def newLogTab(self,name,filename):
        new_tab = QtGui.QWidget()
        new_tab.setObjectName(filename)
        new_gridLayout = QtGui.QGridLayout(new_tab)
        new_gridLayout.setObjectName(_fromUtf8("new_gridLayout"))
        new_pushButton = QtGui.QPushButton(new_tab)
        new_pushButton.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/fileSave16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        new_pushButton.setIcon(icon3)
        new_pushButton.setObjectName(_fromUtf8("pushButton"))
        new_gridLayout.addWidget(new_pushButton, 0, 1, 1, 1)
        new_textEdit = QtGui.QTextEdit(new_tab)
        palette = QtGui.QPalette()
        command_window(palette)
        new_textEdit.setPalette(palette)
        new_textEdit.setUndoRedoEnabled(False)
        new_textEdit.setReadOnly(True)
        new_textEdit.setObjectName(_fromUtf8("textEdit"))
        new_gridLayout.addWidget(new_textEdit, 1, 0, 1, 4)
        new_pushButton_2 = QtGui.QPushButton(new_tab)
        new_pushButton_2.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/browseFile16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        new_pushButton_2.setIcon(icon4)
        new_pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        new_gridLayout.addWidget(new_pushButton_2, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        new_gridLayout.addItem(spacerItem2, 0, 3, 1, 1)
        new_pushButton_3 = QtGui.QPushButton(new_tab)
        new_pushButton_3.setEnabled(False)
        new_pushButton_3.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/stop16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        new_pushButton_3.setIcon(icon5)
        new_pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        new_gridLayout.addWidget(new_pushButton_3, 0, 0, 1, 1)
        
        if  self.lastPos.has_key(filename):
            for i in range(self.tabWidget_2.count()):
                if self.tabWidget_2.widget(i).objectName()==filename:
                    self.closeLogTab(i)
                    break
        
        self.tabWidget_2.addTab(new_tab, name)
        self.fs_watcher.addPath(filename)
        self.lastPos[filename] = 0
        self.typeFile[filename] = 'log'
    
        
    def closeLogTab(self,i):
        filename = self.tabWidget_2.widget(i).objectName()
        del self.lastPos[filename]
        del self.typeFile[filename]
        self.fs_watcher.removePath(filename)
        command = 'rm %s'%filename        
        self.tabWidget_2.removeTab(i)
        
    def file_changed(self,path):

        if self.typeFile[path]=='log': 
        
            toModify = self.findChild(QtGui.QWidget,path)
            textEdit = toModify.findChild(QtGui.QTextEdit,_fromUtf8("textEdit"))
            N = self.lastPos[path]
            ini = time.time()
            with open(path, 'r') as yourFile:
                yourFile.seek(N)
                newTexto = yourFile.read()    
            
            if(len(newTexto)<=1):
                return
                
            textEdit.append(newTexto)
            self.lastPos[path] = N + len(newTexto)
            print 'Agregar %s lleva %f segundos'%(path,time.time()-ini)   
            
        if self.typeFile[path]=='plot':
            if 'residuals.dat' in path:
                canvas = self.findChild(QtGui.QWidget,'residuals.dat').findChild(FigureCanvas)
                axes = canvas.figure.gca()
                N = self.lastPos['residuals.dat']
                
                data = pylab.loadtxt(path,skiprows=N)
                if len(data)>0:
                    ini = time.time()
                    if self.dataPlot['residuals.dat'] == []:
                        self.dataPlot['residuals.dat'] = data
                    else:
                        self.dataPlot['residuals.dat'] = numpy.vstack((self.dataPlot['residuals.dat'],data))
    
                    if data.ndim==1:
                        self.lastPos['residuals.dat'] = N + 1
                    else:
                        self.lastPos['residuals.dat'] = N + data.shape[0]
                        
                    self.dataPlot['residuals.dat'] = self.dataPlot['residuals.dat'][-100:,:]
                    axes.clear()
                    axes.plot(self.dataPlot['residuals.dat'][:,0],self.dataPlot['residuals.dat'][:,1],'r')
                    axes.plot(self.dataPlot['residuals.dat'][:,0],self.dataPlot['residuals.dat'][:,2],'b')
                    canvas.draw()
                    print 'Plotear %s lleva %f segundos'%(path,time.time()-ini)                    
          
            
    def update_watcher(self):
        print "Actualizando el watcher"
        i = 0
        while i<len(self.pending_files):
            filename = '%s/%s'%(self.currentFolder,self.pending_files[i])
            if os.path.isfile(filename):
                self.fs_watcher.addPath(filename)
                self.pending_files.pop(i)
                #una vez que se cual es la grafica
                self.typeFile[filename] = 'plot' 
                self.file_changed(filename)
            else:
                i = i+1
        threading.Timer(5.0, self.update_watcher).start()
                
    def save_config(self):
        filename = '%s/petroFoam.config'%self.currentFolder
        config = {}
        #aca hay que cargar todas las selecciones de combobox,etc
        config['nPlots'] = self.nPlots
        output = open(filename, 'wb')
        pickle.dump(config, output)
        output.close()
        
        
    def load_config(self):
        filename = '%s/petroFoam.config'%self.currentFolder
        if os.path.isfile(filename):
            pkl_file = open(filename, 'rb')        
            config = pickle.load(pkl_file)
            pkl_file.close()
            self.nPlots = config['nPlots']        
            print 'Se levanto desde config nPlots=%i'%self.nPlots
        
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = petroFoam()
    window.show()
    sys.exit(app.exec_())
