from PyQt4 import QtGui, QtCore
from petroFoam_ui import petroFoamUI
from popUpNew import *
from popUpNewFigure import *
from figureResiduals import *
from figureGeneralSnapshot import *
from figureSampledLine import *
from runTimeControls import *
from materials import *
from solutionModeling import *
from mesh import *
from run import *
from bc import *
from initialConditions import *
from postpro import *
from logTab import *
import os
from math import *
import time
import threading
import pickle

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
        
        self.solvername = 'icoFoam'
        self.firstPlot = 1

        self.typeFile = {}
        self.lastPos = {}

        self.qscrollLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.qscrollLayout.setGeometry(QtCore.QRect(0, 0, 500, 300))
        self.qfigWidgets = [];
        self.nPlots = 0
        self.typeFigure = ['Residuals', 'Probes', 'Sampled Line', 'General Snapshot']
        self.colors = ['r', 'b', 'k', 'g', 'y', 'c']

        self.addNewFigureButton()
        
        QtCore.QObject.connect(self.qfigWidgets[self.nPlots], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.addNewFigure)

        self.scrollAreaWidgetContents.setLayout(self.qscrollLayout)

        QtCore.QObject.connect(self.tabWidget_2, QtCore.SIGNAL("tabCloseRequested(int)"), self.closeLogTab)

        self.meshW = meshWidget()
        self.meshW.setParent(self)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.tab_mesh)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout_3.addWidget(self.meshW)
        
        self.runW = runWidget(self.currentFolder)
        self.runW.setParent(self)
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tab_run)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.horizontalLayout_4.addWidget(self.runW)
        
        self.postproW = postproWidget()
        self.postproW.setParent(self)
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.tab_postpro)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.horizontalLayout_5.addWidget(self.postproW)
        
        #apago todas las opciones hasta que se abra algun caso
        self.OnOff(False)

    def updateMeshPanel(self):
        QtGui.QMessageBox.about(self, "ERROR", "Primero se debe calcular!")

    def openCase(self):
        self.currentFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Open Folder', './');
        if self.currentFolder:
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
            command = 'cp -r templates/template_icoFoam %s' % self.currentFolder;
            os.system(command)
            self.OnOff(True)
            self.meshW.setCurrentFolder(self.currentFolder)
            self.runW.setCurrentFolder(self.currentFolder)
            self.postproW.setCurrentFolder(self.currentFolder)

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
        os.system('paraFoam -builtin -case %s &'%self.currentFolder)
        
    def closeEvent(self, evnt):
        print "se intenta cerrar"
        self.timer.cancel()
        #evnt.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    
    def runCase(self):
        self.runW.runCase()

    def addNewFigure(self, index):
        if index<2:
            return
        index = index - 2
        addFigure = False
        
        print self.typeFigure[index]
        if self.typeFigure[index] == 'Residuals':
            w = figureResiduals(self.currentFolder)
            result = w.exec_()
            filename = ''
            if result:
                data = w.getData()
                [bas1,bas2,currtime] = currentFields(self.currentFolder)
                addFigure = True
                filename = 'postProcessing/%s/%s/residuals.dat'%(str(data['name']),currtime)
                if(os.path.isfile('%s/%s'%(self.currentFolder,filename))):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output file already exists, do yo want to remove it? (If not, you must choose another log name)", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm %s/%s'%(self.currentFolder,filename)
                        os.system(command)
                    else:
                        addFigure = False
            if addFigure:
                ww = figureResidualsWidget(self.scrollAreaWidgetContents, data['name'])
                self.pending_files.append(filename)

        if self.typeFigure[index] == 'Sampled Line':
            w = figureSampledLine(self.currentFolder)
            result = w.exec_()
            if result:
                data = w.getData()
                print data
                dirname = 'postProcessing/%s'%data['name']
                addFigure = True
                if(os.path.isdir('%s/%s'%(self.currentFolder,dirname))):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output directory '%s' already exists, do yo want to remove it?"%'%s/%s'%(self.currentFolder,dirname), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm -r %s/%s'%(self.currentFolder,dirname)
                        os.system(command)
                    else:
                        addFigure = False                
                if data['autorefreshing']=='Yes' and addFigure:
                    self.pending_dirs.append(dirname)
            
            if addFigure:
                ww = figureSampledLineWidget(self.scrollAreaWidgetContents, data['name'])
                        
        if self.typeFigure[index] == 'General Snapshot':
            fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Paraview State', self.currentFolder, 'Paraview state (*.pvsm)');
            newdir = ''
            data_name = ''
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
                ww = figureGeneralSnapshotWidget(self.scrollAreaWidgetContents)     
                command = 'mkdir -p %s'%(newdir)
                os.system(command)
                #hago una copia del pvsm para tenerlo siempre accesible
                command = 'cp %s %s/%s.pvsm'%(fileName,self.currentFolder,data_name)
                os.system(command)
            else:
                print 'nothing selected'

        if addFigure:
            i = self.nPlots
            self.qfigWidgets.insert(i, ww)

            #agrego el nuevo plot
            self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)
            #vuelvo a ubicar el boton
            self.qscrollLayout.addWidget(self.qfigWidgets[i+1],(i+1)/2,(i+1)%2)
            self.nPlots = self.nPlots+1
            self.qfigWidgets[i].setObjectName(data['name'])

        self.qfigWidgets[self.nPlots].setCurrentIndex(0)

        
    def resetFigures(self,postpro=False,snapshots=False):
        
        [bas1,bas2,currtime] = currentFields(self.currentFolder)
        for i in range(self.nPlots):
            if isinstance(self.qfigWidgets[i],figureResidualsWidget) and postpro:  
                self.qfigWidgets[i].resetFigure()
                filename = 'postProcessing/%s/%s/residuals.dat'%(self.qfigWidgets[i].objectName(),currtime)
                self.pending_files.append(filename)
            elif isinstance(self.qfigWidgets[i],figureSampledLineWidget) and postpro:  
                self.qfigWidgets[i].resetFigure()
                dirname = 'postProcessing/%s'%self.qfigWidgets[i].objectName()
                #Solo agregar si se eligio autorefreshing             
                self.pending_dirs.append(dirname)  
            elif isinstance(self.qfigWidgets[i],figureGeneralSnapshotWidget) and snapshots:  
                self.qfigWidgets[i].resetFigure()
            else:
                None

    def newLogTab(self,name,filename):

        new_tab = logTab(filename,self.currentFolder)

        already = False
        if  self.lastPos.has_key(filename):
            for i in range(self.tabWidget_2.count()):
                if self.tabWidget_2.widget(i).objectName()==filename:
                    self.findChild(QtGui.QWidget,filename).findChild(QtGui.QTextEdit,_fromUtf8("textEdit")).clear()
                    already = True
                    break

        if not already:
            self.tabWidget_2.addTab(new_tab, name)
            self.tabWidget_2.widget(self.tabWidget_2.count()-1).setObjectName(filename)
        
        if not os.path.isfile(filename):
            command = 'touch %s'%filename
            os.system(command)
        
        if filename not in self.fs_watcher.files():
            self.fs_watcher.addPath(filename)
        
        self.lastPos[filename] = 0
        self.typeFile[filename] = 'log'


    def closeLogTab(self,i):
        filename = self.tabWidget_2.widget(i).objectName()
        del self.lastPos[filename]
        del self.typeFile[filename]
        self.fs_watcher.removePath(filename)
        command = 'rm %s'%filename
        os.system(command)
        self.tabWidget_2.removeTab(i)

    def file_changed(self,path):
        self.fs_watcher.removePath(path)
        
        if self.typeFile[path]=='log':
            toModify = self.findChild(QtGui.QWidget,path)
            textEdit = toModify.findChild(QtGui.QTextEdit,_fromUtf8("textEdit"))
            N = self.lastPos[path]
            with open(path, 'r') as yourFile:
                yourFile.seek(N)
                newTexto = yourFile.read()
            
            if(len(newTexto)>1):
                textEdit.append(newTexto)
                self.lastPos[path] = N + len(newTexto)

        if self.typeFile[path]=='plot':
            key = ''
            for qfw in self.qfigWidgets:
                ikey = qfw.objectName()
                if 'postProcessing/%s'%ikey in path:
                    key = ikey
                    break

            if key == '':
                self.fs_watcher.addPath(path)
                return

            if 'residuals.dat' in path:
                
                frWidget = self.findChild(figureResidualsWidget,key)
                frWidget.plot(path)

        self.fs_watcher.addPath(path)

    def directory_changed(self,path):
        self.fs_watcher.removePath(path)
        if not os.path.exists(path):
            return
        #busco a cual se corresponde
        keys = []

        if 'postProcessing' in path:
            for qfw in self.qfigWidgets:
                key = qfw.objectName()
                if 'postProcessing/%s'%key in path:
                    keys.append(key)
                    break
        else:
            for qfw in self.qfigWidgets:
                key = qfw.objectName()
                if 'snapshots/%s'%key in path:
                    keys.append(key)
                    break

        if keys==[]:
            self.fs_watcher.addPath(path)
            return


        for ii in keys:
            figW = self.findChild(QtGui.QWidget,ii)
            newdirs = list(set(os.listdir(path))-set(figW.dirList))
            newdirs.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime)
            if figW:
                figW.dirList.extend(newdirs)
                figW.lastPos = len(figW.dirList)-1
                if figW.lastPos>0:
                    figW.plot()

        self.fs_watcher.addPath(path)


    def update_watcher(self):
        print "Actualizando el watcher"
        i = 0
        while i<len(self.pending_files):
            filename = '%s/%s'%(self.currentFolder,self.pending_files[i])
            print 'testng %s'%filename
            if os.path.isfile(filename):
                print 'Se agrega %s'%filename
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
        
        #estos 5 deberian volar
        config['typeFile'] = self.typeFile
        config['lastPos'] = self.lastPos

        config['namePlots'] = []
        config['typePlots'] = []
        for i in range(self.nPlots):
            config['namePlots'].append(self.qfigWidgets[i].objectName())
            if isinstance(self.qfigWidgets[i],figureResidualsWidget):  
                config['typePlots'].append('Residuals')
            elif isinstance(self.qfigWidgets[i],figureSampledLineWidget):  
                config['typePlots'].append('Sampled Line')
            elif isinstance(self.qfigWidgets[i],figureGeneralSnapshotWidget):  
                config['typePlots'].append('General Snapshot')
            else:
                config['typePlots'].append(' ')
        
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
            wrongFile = 0            
            wrongFile = 1 if 'nPlots' not in config.keys() else wrongFile
            wrongFile = 1 if 'namePlots' not in config.keys() else wrongFile
            wrongFile = 1 if 'typePlots' not in config.keys() else wrongFile
            wrongFile = 1 if 'typeFile' not in config.keys() else wrongFile
                        
            if wrongFile:
                QtGui.QMessageBox.about(self, "ERROR", "Corrupted File")
                return
            
            for i in range(self.nPlots):
                self.removeFigure(self.qfigWidgets[self.nPlots-i])
            
            self.fs_watcher.removePaths(self.fs_watcher.files())
            self.fs_watcher.removePaths(self.fs_watcher.directories())
            self.pending_files = []
            self.pending_dirs = []
            
            self.nPlots = config['nPlots'] 
            namePlots = config['namePlots']
            typePlots = config['typePlots']
            self.typeFile = config['typeFile']
            
            
            for i in range(self.nPlots):
                if typePlots[i]=='Residuals':
                    ww = figureResidualsWidget(self.scrollAreaWidgetContents,namePlots[i])
                    [bas1,bas2,currtime] = currentFields(self.currentFolder)
                    filename = 'postProcessing/%s/%s/residuals.dat'%(namePlots[i],currtime)
                    self.pending_files.append(filename)                    
                elif typePlots[i]=='Sampled Line':
                    ww = figureSampledLineWidget(self.scrollAreaWidgetContents,namePlots[i])      
                    dirname = 'postProcessing/%s'%namePlots[i]
                    #Solo agregar si se eligio autorefreshing             
                    self.pending_dirs.append(dirname)                    
                elif typePlots[i]=='General Snapshot':
                    ww = figureGeneralSnapshotWidget(self.scrollAreaWidgetContents)
                ww.setObjectName(namePlots[i])
                self.qfigWidgets.insert(i,ww)
                self.qfigWidgets[i].setObjectName(namePlots[i])
                self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)
            self.qscrollLayout.addWidget(self.qfigWidgets[self.nPlots],self.nPlots/2,self.nPlots%2)
                
        self.meshW.setCurrentFolder(self.currentFolder)
        self.runW.setCurrentFolder(self.currentFolder)
        self.postproW.setCurrentFolder(self.currentFolder)
        self.meshW.loadMeshData()

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
        if figW.lastPos==-1 and action != 'refresh':
            return
        if action == 'first':
            figW.lastPos = 0
            figW.plot()
        elif action == 'previous':
            if figW.lastPos>0:
                figW.lastPos = figW.lastPos - 1
                figW.plot()
        elif action == 'next':
            if figW.lastPos<len(figW.dirList)-1:
                figW.lastPos = figW.lastPos + 1
                figW.plot()
        elif action == 'last':
            figW.lastPos = len(figW.dirList) - 1
            figW.plot()
        elif action == 'play':
            figW.lastPos = 0
            button = figW.findChild(temporalNavigationToolbar)._actions['play']
            while figW.lastPos<=len(figW.dirList)-1 and button.isChecked():
                figW.plot()
                figW.lastPos = figW.lastPos + 1
                QtGui.QApplication.processEvents()
                if isinstance(figW,figureGeneralSnapshotWidget):
                    time.sleep(0.1)

            if figW.lastPos==len(figW.dirList):
                figW.lastPos = figW.lastPos - 1
                button.setChecked(False)
        elif action == 'refresh':
            ii = figW.objectName()
            if isinstance(figW,figureSampledLineWidget):
                path = '%s/postProcessing/%s'%(self.currentFolder,ii)
            elif isinstance(figW,figureGeneralSnapshotWidget):
                path = '%s/snapshots/%s'%(self.currentFolder,ii)

            newdirs = list(set(os.listdir(path))-set(figW.dirList))
            newdirs.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime)
            figW.dirList.extend(newdirs)
            figW.lastPos = len(figW.dirList) - 1

            if figW.lastPos>0:
                figW.plot()

    def doPlot(self,figW):
        ii = figW.objectName()
        print 'por hace plot de %s type: %s'%(ii,self.dirType[ii])
       
        if isinstance(figW,figureSampledLineWidget):
                       
            figW.plot()

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
        print menu
        if menu=='Solution Modeling':
            #para el solution modeling no tengo un diccionario
            widget = solutionModeling(self.currentFolder)
        elif menu=='Run Time Controls':
            widget = runTimeControls(self.currentFolder)
        elif 'phase' in menu:
            #alguna de las fases (valido solo hasta 9 phases)        
            widget = materials(self.currentFolder,int(menu[-1])-1)
        elif menu=='Boundary Conditions':
            widget = bcWidget(self.currentFolder)
        elif menu=='Initial Conditions':
            widget = initialConditionsWidget(self.currentFolder)
        else:
            #do nothing
            return           

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

    def addNewFigureButton(self):
        self.qfigWidgets.append(QtGui.QComboBox(self.scrollAreaWidgetContents))
        self.qfigWidgets[self.nPlots].setObjectName(_fromUtf8("newFigureComboBox"))
        self.qfigWidgets[self.nPlots].addItem(_fromUtf8("Select New Figure"))
        self.qfigWidgets[self.nPlots].insertSeparator(1)
        self.qfigWidgets[self.nPlots].addItems(self.typeFigure)
        self.qscrollLayout.addWidget(self.qfigWidgets[self.nPlots],self.nPlots/2,self.nPlots%2)
        

def main():
    
    import sys
    app = QtGui.QApplication(sys.argv)
    window = petroFoam()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()