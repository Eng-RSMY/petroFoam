from PyQt4 import QtGui, QtCore
from petroFoam_ui import petroFoamUI
from popUpNew import *
from popUpNewFigure import *
from figureResiduals import *
from figureSampledLine import *
from myNavigationToolbar import *
from temporalNavigationToolbar import *
from runTimeControls import *
from solutionModeling import *
from logTab import *
import os
from math import *
import time
import threading
import numpy
import pickle

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pylab

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
        self.fs_watcher.directoryChanged.connect(self.directory_changed)
        
        self.pending_files = []
        self.pending_dirs = []
        self.update_watcher()
        #pylab.ion()
        
        self.controlDict = {}
        self.controlDict['startTime'] = 0
        self.solvername = 'icoFoam'
        self.firstPlot = 1
        
        self.lastPos = {}
        self.typeFile = {}
        self.dataPlot = {}
        self.dirList = {}
        self.dirType = {}
        
        self.qscrollLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.qscrollLayout.setGeometry(QtCore.QRect(0, 0, 500, 300))
        self.qfigWidgets = [];
        self.nPlots = 0
        self.typeFigure = ['Residuals', 'Probes', 'Sampled Line', 'General Snapshot']        
        
        self.qfigWidgets.append(QtGui.QComboBox(self.scrollAreaWidgetContents))
        self.qfigWidgets[self.nPlots].setObjectName(_fromUtf8("newFigureComboBox"))
        self.qfigWidgets[self.nPlots].addItem(_fromUtf8("Select New Figure"))
        self.qfigWidgets[self.nPlots].insertSeparator(1)
        self.qfigWidgets[self.nPlots].addItems(_fromUtf8(self.typeFigure))
        self.qscrollLayout.addWidget(self.qfigWidgets[self.nPlots],self.nPlots/2,self.nPlots%2)
        QtCore.QObject.connect(self.qfigWidgets[self.nPlots], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.addNewFigure)

        self.scrollAreaWidgetContents.setLayout(self.qscrollLayout)
        
        QtCore.QObject.connect(self.tabWidget_2, QtCore.SIGNAL("tabCloseRequested(int)"), self.closeLogTab)
        
        #apago todas las opciones hasta que se abra algun caso
        self.OnOff(False)
        
    def updateMeshPanel(self):
        QtGui.QMessageBox.about(self, "ERROR", "Primero se debe calcular!")

    def importMesh(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Mesh to Import', './', 'Mesh Files (*.msh)');
        print fileName

    def openCase(self):
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder', './');
        self.load_config()
        self.OnOff(True)

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
            self.OnOff(True)
	
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

    def openParaview(self):
        os.system('paraFoam -case %s &'%self.currentFolder)

    def closeEvent(self, evnt):
        print "se intenta cerrar"
        self.timer.cancel()
        #evnt.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
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
        
#        if os.path.isdir('%s/postProcessing'%self.currentFolder):
#            comm = 'mv %s/postProcessing %s/postProcessingOld'%(self.currentFolder,self.currentFolder)
#            os.system(comm)
        filename = '%s/run.log'%self.currentFolder
        command = 'touch %s'%filename
        os.system(command)
        self.newLogTab('Run','%s/run.log'%self.currentFolder)
        command = '%s -case %s > %s &'%(self.solvername,self.currentFolder,filename)
        os.system(command)
        
    def addNewFigure(self, index):
        if index<2:
            return
        index = index - 2
        if self.typeFigure[index] == 'Residuals':
            w = figureResiduals()
            result = w.exec_()
            if result:
                data = w.getData()
                addFigure = True
                filename = 'postProcessing/%s/%s/residuals.dat'%(str(data['name']),str(self.controlDict['startTime']))                
                if(os.path.isfile('%s/%s'%(self.currentFolder,filename))):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output file already exists, do yo want to remove it? (If not, you must choose another log name)", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm %s/%s'%(self.currentFolder,filename)
                        os.system(command)
                    else:
                        addFigure = False
                
                if addFigure:
                    i = self.nPlots
                    self.qfigWidgets.insert(i, QtGui.QWidget(self.scrollAreaWidgetContents))
                    fig = Figure((3.0, 2.0), dpi=100)
                    canvas = FigureCanvas(fig)
                    canvas.setParent(self.qfigWidgets[i])
                    toolbar = myNavigationToolbar(canvas, self.qfigWidgets[i])
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
            
                    self.pending_files.append(filename)
                    self.qfigWidgets[i].setObjectName('residuals.dat')
                    self.lastPos['residuals.dat'] = 2
                    self.dataPlot['residuals.dat'] = []
 
               
        if self.typeFigure[index] == 'Sampled Line':
            w = figureSampledLine()
            result = w.exec_()
            if result:
                data = w.getData()
                
                addFigure = True
                dirname = 'postProcessing/%s'%data['name']
                if(os.path.isdir('%s/%s'%(self.currentFolder,dirname))):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output directory '%s' already exists, do yo want to remove it?"%'%s/%s'%(self.currentFolder,dirname), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm -r %s/%s'%(self.currentFolder,dirname)
                        os.system(command)
                    else:
                        addFigure = False
                
                if addFigure:
                
                    i = self.nPlots
                    self.qfigWidgets.insert(i, QtGui.QWidget(self.scrollAreaWidgetContents))
                    fig = Figure((3.0, 2.0), dpi=100)
                    canvas = FigureCanvas(fig)
                    canvas.setParent(self.qfigWidgets[i])
                    toolbar = myNavigationToolbar(canvas, self.qfigWidgets[i])
                    temporal_toolbar = temporalNavigationToolbar(canvas, self.qfigWidgets[i])
                    axes = fig.add_subplot(111)
                    axes.autoscale(True)
                    axes.set_yscale('log')
                    axes.set_title(data['name'])
                    #axes.set_xlabel('Time [s]')
                    #axes.set_ylabel('|R|')
                    
                     # place plot components in a layout
                    plotLayout = QtGui.QVBoxLayout()
                    plotLayout.addWidget(temporal_toolbar)
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
                    
                    if data['autorefreshing']:
                        self.pending_dirs.append(dirname)
                    
                    self.qfigWidgets[i].setObjectName(data['name'])
                    self.dirList[data['name']] = []
                    self.dirType[data['name']] = 'Sampled Line'
                    self.lastPos[data['name']] = -1

        if self.typeFigure[index] == 'General Snapshot':
                fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Paraview State', self.currentFolder, 'Paraview state (*.pvsm)');
                    
                if fileName:
                    data_name = os.path.basename(fileName)
                    data_name = data_name[:-5]
                    newdir = '%s/snapshots/%s'%(self.currentFolder,data_name)
                    addFigure = True
                    if os.path.isdir('%s'%newdir):
                        w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output directory '%s' already exists, do yo want to remove it?"%(newdir), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                        ret = w.exec_()
                        if(QtGui.QMessageBox.Yes == ret):
                            command = 'rm -r %s'%newdir
                            os.system(command)
                        else:
                            addFigure = False
                    
                    if addFigure:

                        i = self.nPlots
                        self.qfigWidgets.insert(i, QtGui.QWidget(self.scrollAreaWidgetContents))
                        canvas = FigureCanvas(Figure((3.0, 2.0), dpi=100))
                        canvas.setParent(self.qfigWidgets[i])
                        toolbar = myNavigationToolbar(canvas, self.qfigWidgets[i])
                        toolbar.disableButtons()
                        temporal_toolbar = temporalNavigationToolbar(canvas, self.qfigWidgets[i])
                        
                        mainImage = QtGui.QLabel(self.qfigWidgets[i])
                        mainImage.setText(_fromUtf8(""))
                        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/emptyFigure.png")))
                        mainImage.setObjectName(_fromUtf8("mainImage"))
                        
                        plotLayout = QtGui.QVBoxLayout()
                        plotLayout.addWidget(temporal_toolbar)
                        plotLayout.addWidget(mainImage)  
                        plotLayout.addWidget(toolbar)
                        
                        self.qfigWidgets[i].setLayout(plotLayout)
                        
                        self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)                
                        self.qscrollLayout.addWidget(self.qfigWidgets[i+1],(i+1)/2,(i+1)%2)
                        self.nPlots = self.nPlots+1
                        
                        command = 'mkdir -p %s'%(newdir)
                        os.system(command)
                        #hago una copia del pvsm para tenerlo siempre accesible
                        command = 'cp %s %s/%s.pvsm'%(fileName,self.currentFolder,data_name)
                        os.system(command)
                        self.qfigWidgets[i].setObjectName(data_name)
                        self.dirList[data_name] = []
                        self.dirType[data_name] = 'General Snapshot'
                        self.lastPos[data_name] = -1
                        #no lo agrego al watcher porque va a ser manual
                        #self.fs_watcher.addPath('%s'%newdir)
                        
                else:
                    print 'nothing selected'
                
        self.qfigWidgets[self.nPlots].setCurrentIndex(0)  
        
    def newLogTab(self,name,filename):
        
        new_tab = logTab(filename)
        
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
        self.fs_watcher.removePath(path)
        
        if self.typeFile[path]=='log': 
            toModify = self.findChild(QtGui.QWidget,path)
            textEdit = toModify.findChild(QtGui.QTextEdit,_fromUtf8("textEdit"))
            N = self.lastPos[path]
            ini = time.time()
            with open(path, 'r') as yourFile:
                yourFile.seek(N)
                newTexto = yourFile.read()    
            
            if(len(newTexto)>1):
                textEdit.append(newTexto)
                self.lastPos[path] = N + len(newTexto)
            
        if self.typeFile[path]=='plot':
        
            if 'residuals.dat' in path:
                canvas = self.findChild(QtGui.QWidget,'residuals.dat').findChild(FigureCanvas)
                axes = canvas.figure.gca()
                N = self.lastPos['residuals.dat']
                
                data = pylab.loadtxt(path,skiprows=N)
                if len(data)>0:
                    ini = time.time()
                    oldPos = self.lastPos['residuals.dat']
                    if self.dataPlot['residuals.dat'] == []:
                        self.dataPlot['residuals.dat'] = data
                    else:
                        self.dataPlot['residuals.dat'] = numpy.vstack((self.dataPlot['residuals.dat'],data))
    
                    if data.ndim==1:
                        self.lastPos['residuals.dat'] = N + 1
                    else:
                        self.lastPos['residuals.dat'] = N + data.shape[0]
                        
                    print 'Nuevos leidos %i'%(self.lastPos['residuals.dat']-oldPos)                    
          
                    if(self.dataPlot['residuals.dat'].ndim>1):    
                        self.dataPlot['residuals.dat'] = self.dataPlot['residuals.dat'][-100:,:]
                    
                    #para no tener que tener todos los datos en memoria
#                    line = gca().get_lines()[n]
#                    xd = line.get_xdata()
#                    yd = line.get_ydata()

                    if 1:
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
                    else:
                    #plotear mas rapido: el problema es que no refresca bien las leyendas de los ejes
                        if self.firstPlot:
                            axes.plot(self.dataPlot['residuals.dat'][:,0],self.dataPlot['residuals.dat'][:,1],'r')
                            axes.plot(self.dataPlot['residuals.dat'][:,0],self.dataPlot['residuals.dat'][:,2],'b')
                            canvas.draw()
                            self.firstPlot = 0
                        
                        line0 = axes.get_lines()[0]
                        line1 = axes.get_lines()[1]
                        
                        line0.set_xdata(self.dataPlot['residuals.dat'][:,0])
                        line0.set_ydata(self.dataPlot['residuals.dat'][:,1])
                        line1.set_xdata(self.dataPlot['residuals.dat'][:,0])
                        line1.set_ydata(self.dataPlot['residuals.dat'][:,2])
                        
                        minx = numpy.amin(self.dataPlot['residuals.dat'][:,0])
                        miny = numpy.amin(self.dataPlot['residuals.dat'][:,1:3])
                        maxx = numpy.amax(self.dataPlot['residuals.dat'][:,0])
                        maxy = numpy.amax(self.dataPlot['residuals.dat'][:,1:3])
    
                        axes.set_xlim(minx,maxx)
                        axes.set_ylim(miny,miny*10e3)
                        
                        axes.draw_artist(axes.patch)
                        axes.draw_artist(line0)
                        axes.draw_artist(line1)
                        axes.draw_artist(axes.xaxis)
                        axes.draw_artist(axes.yaxis)
    
                        canvas.update()
                        canvas.flush_events()
                                            
                    print 'Plotear %s lleva %f segundos con un tamanio %i'%(path,time.time()-ini,len(self.dataPlot['residuals.dat'][:,0]))                    
        self.fs_watcher.addPath(path)
        
    def directory_changed(self,path):
        self.fs_watcher.removePath(path)
        print 'en directory changed de %s'%path
        #busco a cual se corresponde
        keys = []
        
        if 'postProcessing' in path:
            for key in self.dirType.keys():
                if 'postProcessing/%s'%key in path:
                    keys.append(key)
                    break
        else:
            for key in self.dirType.keys():
                if 'snapshots/%s'%key in path:
                    keys.append(key)
                    break

        if keys==[]:
            self.fs_watcher.addPath(path)
            return

        print keys

        for ii in keys:
            newdirs = list(set(os.listdir(path))-set(self.dirList[ii]))
            newdirs.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime)
            self.dirList[ii].extend(newdirs)
            self.lastPos[ii] = len(self.dirList[ii])-1
            
            if self.lastPos[ii]>0:
                self.doPlot(self.findChild(QtGui.QWidget,ii))

        self.fs_watcher.addPath(path)
    
        
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
        i = 0
        while i<len(self.pending_dirs):
            dirname = '%s/%s'%(self.currentFolder,self.pending_dirs[i])
            if os.path.isdir(dirname):
                print 'Agrego %s'%dirname
                self.fs_watcher.addPath(dirname)
                self.pending_dirs.pop(i)
                #una vez que se cual es la grafica
                self.directory_changed(dirname)
            else:
                i = i+1

        self.timer = threading.Timer(5.0, self.update_watcher)
        self.timer.start()
                
    def save_config(self):
        filename = '%s/petroFoam.config'%self.currentFolder
        config = {}
        #aca hay que cargar todas las selecciones de combobox,etc
        config['nPlots'] = self.nPlots
        config['figW'] = self.qfigWidgets
        config['dirList'] = self.dirList
        config['dirType'] = self.dirType
        config['dataPlot'] = self.dataPlot
        config['typeFile'] = self.typeFile
        config['lastPos'] = self.lastPos
        output = open(filename, 'wb')
        pickle.dump(config, output)
        output.close()
        
        
    def load_config(self):
        filename = '%s/petroFoam.config'%self.currentFolder
        if os.path.isfile(filename):
            pkl_file = open(filename, 'rb')        
            config = pickle.load(pkl_file)
            pkl_file.close()
            #preguntar si existe cada campo!!!!!
            self.nPlots = config['nPlots']
            self.qfigWidgets = config['figW']
            self.dirList = config['dirList']
            self.dirType = config['dirType']
            self.dataPlot = config['dataPlot'] 
            self.typeFile = config['typeFile']             
            print 'Se levanto desde config nPlots=%i'%self.nPlots
            for i in range(self.nPlots):
                self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)
            
            
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
        
    def temporalFigure_update(self,figW,action):
        print 'hacer %s en %s'%(action,figW.objectName())
        if self.lastPos[figW.objectName()]==-1 and action != 'refresh':
            return
        if action == 'first':
            self.lastPos[figW.objectName()] = 0
            self.doPlot(figW)
        elif action == 'previous':
            if self.lastPos[figW.objectName()]>0:
                self.lastPos[figW.objectName()] = self.lastPos[figW.objectName()]-1
                self.doPlot(figW)
        elif action == 'next':
            if self.lastPos[figW.objectName()]<len(self.dirList[figW.objectName()])-1:
                self.lastPos[figW.objectName()] = self.lastPos[figW.objectName()]+1
                self.doPlot(figW)
        elif action == 'last':
            self.lastPos[figW.objectName()] = len(self.dirList[figW.objectName()])-1
            self.doPlot(figW)
        elif action == 'play':
            self.lastPos[figW.objectName()] = 0
            button = figW.findChild(temporalNavigationToolbar)._actions['play']
            while self.lastPos[figW.objectName()]<=len(self.dirList[figW.objectName()])-1 and button.isChecked(): 
                self.doPlot(figW)
                self.lastPos[figW.objectName()] = self.lastPos[figW.objectName()]+1
                QtGui.QApplication.processEvents()
                if self.dirType[figW.objectName()]=='General Snapshot':
                    time.sleep(0.1)
                    
            if self.lastPos[figW.objectName()]==len(self.dirList[figW.objectName()]):
                self.lastPos[figW.objectName()] = self.lastPos[figW.objectName()] - 1
                button.setChecked(False)
        elif action == 'refresh':
            ii = figW.objectName()
            
            if self.dirType[ii]=='Sampled Line':           
                path = '%s/postProcessing/%s'%(self.currentFolder,ii)
            elif  self.dirType[ii]=='General Snapshot':
                path = '%s/snapshots/%s'%(self.currentFolder,ii)
                
            newdirs = list(set(os.listdir(path))-set(self.dirList[ii]))
            newdirs.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime)
            self.dirList[ii].extend(newdirs)
            self.lastPos[ii] = len(self.dirList[ii])-1
            
            print self.dirList[ii]
            
            if self.lastPos[ii]>0:
                self.doPlot(self.findChild(QtGui.QWidget,ii))

            None
            
    def doPlot(self,figW):
        ii = figW.objectName()
        print 'por hace plot de %s type: %s'%(ii,self.dirType[ii])
        
        if self.dirType[ii]=='Sampled Line':
            canvas = figW.findChild(FigureCanvas)
            timeLegend = figW.findChild(QtGui.QLineEdit)
            axes = canvas.figure.gca()

            filename = '%s/postProcessing/%s/%s/data_U.xy'%(self.currentFolder,ii,self.dirList[ii][self.lastPos[ii]])
            data = pylab.loadtxt(filename)
            if len(data)>0:
                
                axes.clear()                    
                line0 = axes.plot(data[:,0],data[:,1],'r', label="Ux")
                
                timeLegend.setText(self.dirList[ii][self.lastPos[ii]])
                
                axes.set_title(ii)
                axes.set_xlabel('Time [s]')
                axes.set_ylabel('|R|')
                axes.legend(loc=2, fontsize = 'small')

                canvas.draw()
                
        if  self.dirType[ii]=='General Snapshot':
            desired = '%s/snapshots/%s/%s/%s.png'%(self.currentFolder,ii,self.dirList[ii][self.lastPos[ii]],ii)
            print desired
            if os.path.isfile(desired)==False:
                command = 'pvpython /usr/local/bin/pyFoamPVSnapshot.py --time=%s --state-file=%s/%s.pvsm  --file-prefix="snapshot" --no-casename --no-timename %s'%(self.dirList[ii][self.lastPos[ii]],self.currentFolder,ii,self.currentFolder)
                os.system(command)
                while os.path.isfile('snapshot_00000.png')==False:
                    None
                command = 'mv snapshot_00000.png %s/snapshots/%s/%s/%s.png'%(self.currentFolder,ii,self.dirList[ii][self.lastPos[ii]],ii)
                os.system(command)
            mainImage = figW.findChild(QtGui.QLabel,'mainImage')
            mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(desired)))
            
            timeLegend = figW.findChild(QtGui.QLineEdit)
            timeLegend.setText(self.dirList[ii][self.lastPos[ii]])
            
            
    def updateCaseSetup(self,QTreeWidgetItem):
                
        menu = QTreeWidgetItem.text(0)
        if menu=='Solution Modeling':
            #para el solution modeling no tengo un diccionario
            widget = solutionModeling()
        elif menu=='Run Time Controls':
            widget = runTimeControls(self.currentFolder)
            
        
        self.gridLayout_3.addWidget(widget, 0, 1, 1, 1)
        return
            
    def OnOff(self,V):
        self.splitter.setEnabled(V)
        self.actionSave.setEnabled(V)
        self.actionSave_As.setEnabled(V)
        self.actionTerminal.setEnabled(V)
        self.actionBrowse.setEnabled(V)
        self.actionRun.setEnabled(V)
        self.actionParaview.setEnabled(V)

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = petroFoam()
    window.show()
    sys.exit(app.exec_())
