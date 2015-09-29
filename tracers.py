# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from tracers_ui import tracersUI
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

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


class tracers(tracersUI):

    def __init__(self, currentFolder, parallel=False):
        tracersUI.__init__(self)
        self.currentFolder = currentFolder
        self.tracersData = [{},{},{},{},{}]
        self.patches = []
        self.emptys = []
        
        self.loadCaseData()
        self.refreshTable()

    def loadCaseData(self):
        logname = '%s/dirFeatures.log' % self.currentFolder
        command = 'dirFeaturesFoam -case %s > %s' % (self.currentFolder,logname)
        os.system(command)
        log = open(logname, 'r')
        for linea in log:
            if "Current Time" in linea:
                currtime = linea.split('=')[1].strip()
        #FIXME PARALLEL
        self.timedir = '%s/%s'%(self.currentFolder,currtime)
        noexists = []
        for i in range(0,5):
            filename = '%s/T%s'%(self.timedir,str(i))
            if not os.path.exists(filename):
                noexists.append(filename)                
            else:
                parsedData = ParsedParameterFile(filename,createZipped=False)
                self.patches = parsedData['boundaryField'].keys()
                for ipatch in parsedData['boundaryField'].keys():
                    if parsedData['boundaryField'][ipatch]['type']=='uniformFixedValue':
                        self.tracersData[i]['patchName'] = ipatch
                        self.tracersData[i]['startTime'] = parsedData['boundaryField'][ipatch]['uniformValue'][1][2][0]
                    elif parsedData['boundaryField'][ipatch]['type']=='empty':
                        self.emptys.append(ipatch)
                        
        if self.patches==[]:
            filename = '%s/U'%(self.timedir,str(i))
            parsedData = ParsedParameterFile(filename,createZipped=False)
            self.patches = parsedData['boundaryField'].keys()
            for ipatch in self.patches:
                if parsedData['boundaryField'][ipatch]['type']=='empty':
                    self.emptys.append(ipatch)
        
        if len(noexists):
            w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "There not exists tracer fields, do you wat to create them?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            ret = w.exec_()
            if(QtGui.QMessageBox.Yes == ret):
                for ii in noexists:   
                    self.createTracersFields(ii)
            else:
                self.close()
      
    def refreshTable(self):
        for i in range(0,5):
            item1 = QtGui.QTableWidgetItem()
            item2 = QtGui.QTableWidgetItem()
            wdg1 = QtGui.QLineEdit()
            wdg2 = QtGui.QComboBox()
            wdg2.addItems(self.patches)
            
            if len(self.tracersData[i]):
                wdg1.setText(str(self.tracersData[i]['startTime']))
                wdg2.setCurrentIndex(wdg2.findText(self.tracersData[i]['patchName']))
            else:
                wdg1.setText(str(1e6))
                wdg2.setCurrentIndex(wdg2.findText('inlet'))
                
            self.tableWidget.setItem(i,0,item1)
            self.tableWidget.setCellWidget(i,0,wdg1) 
            self.tableWidget.setItem(i,1,item2)
            self.tableWidget.setCellWidget(i,1,wdg2)

    def saveCaseData(self):
        zg = {}
        zg['type'] = 'zeroGradient'

        for i in range(0,5):
            filename = '%s/T%s'%(self.timedir,str(i))
            parsedData = ParsedParameterFile(filename,createZipped=False)

            startTime = self.tableWidget.cellWidget(i,0).text()
            patchname = self.tableWidget.cellWidget(i,1).currentText()
            
            oldcb = parsedData['boundaryField'][patchname].copy()
            if oldcb['type']=='uniformFixedValue':
                parsedData['boundaryField'][patchname]['uniformValue'][1][2][0] = str(startTime)
                parsedData['boundaryField'][patchname]['uniformValue'][1][1][0] = str(float(startTime)-0.01)
            else:
                #reemplazo el patch viejo 
                for ipatch in parsedData['boundaryField']:
                    if parsedData['boundaryField'][ipatch]['type'] == 'uniformFixedValue':
                        parsedData['boundaryField'][ipatch] = zg.copy()
                parsedData['boundaryField'][patchname] = oldcb
                parsedData['boundaryField'][patchname]['type'] = 'uniformFixedValue'
                parsedData['boundaryField'][patchname]['uniformValue'] = ('table', [[0, 0.0], [1e6-0.01, 0.0], [1e6, 1.0], [1e6, 1.0]])
                parsedData['boundaryField'][patchname]['uniformValue'][1][2][0] = str(startTime)
                parsedData['boundaryField'][patchname]['uniformValue'][1][1][0] = str(float(startTime)-0.01)
            parsedData.writeFile()
        return 
        
    def createTracersFields(self,filename):
        zg = {}
        zg['type'] = 'zeroGradient'
        
        em = {}
        em['type'] = 'empty'
        
        filenamesrc = 'templates/tracerTemplate'
        parsedTemplate = ParsedParameterFile(filenamesrc,createZipped=False)

        for ipatch in self.patches:
            if ipatch not in self.emptys:
                parsedTemplate['boundaryField'][ipatch]= zg
            else:
                parsedTemplate['boundaryField'][ipatch] = em
        parsedTemplate.writeFileAs(filename)                

            
#    def saveUserLibrary(self):
#        filename = 'caseDicts/materialProperties.incompressible'
#        parsedData = ParsedParameterFile(filename,createZipped=False)
#        parsedData['userLibrary'] = self.userLibrary
#        parsedData.writeFile()
#        
#        return
#
#    def changeSelectionDefault(self):
#        if not self.list_default.selectedItems():
#            print 'No hay selected'
#            return
#        key = self.list_default.selectedItems()[0].text()
#        for item in self.list_user.selectedItems():
#            item.setSelected(False)
#        
#        self.updateParameters(self.defaults[key])   
#        
#        self.OnOff(False)
#        return
#    
#    def changeSelectionUser(self):
#        if not self.list_user.selectedItems():
#            return
#        key = self.list_user.selectedItems()[0].text()
#        for item in self.list_default.selectedItems():
#            item.setSelected(False)
#        self.updateParameters(self.userLibrary[key])
#        self.OnOff(True)
#        return
#        
#    def updateParameters(self,data):
#        for key in emptys.keys():
#            if key=='name':
#                self.__getattribute__(key).setText(str(data[key]))
#            elif key in self.__dict__.keys():
#                self.__getattribute__(key).setText(str(data[key][-1]))
#    
#    def OnOff(self,V):
#        keys = emptys.keys()
#        for key in keys:
#            self.__getattribute__(key).setEnabled(V)
#        self.button_remove.setEnabled(V)
#        self.button_save.setEnabled(V)
#        
#    def new(self):
#        self.updateParameters(emptys)
#        self.OnOff(True)
#        for item in self.list_default.selectedItems():
#            item.setSelected(False)
#        for item in self.list_user.selectedItems():
#            item.setSelected(False)
#        self.button_remove.setEnabled(False)
#        return
#        
#    def copy(self):
#        data = self.getSelectedData()
#        if data:
#            self.updateParameters(data)
#            texto = self.name.text() + "_copy"
#            self.name.setText(texto)
#            self.OnOff(True)    
#        
#        return
#        
#    def getSelectedData(self):
#        ditem = self.list_default.selectedItems()
#        data = False
#        if len(ditem):
#            data = self.defaults[ditem[0].text()]
#        else:
#            uitem = self.list_user.selectedItems()
#            if len(uitem):
#                data = dict(self.userLibrary[uitem[0].text()])
#        return data
#        
#    def remove(self):
#        uitem = self.list_user.selectedItems()
#        if len(uitem):
#            w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "Are you sure to remove?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
#            ret = w.exec_()
#            if(QtGui.QMessageBox.Yes == ret):
#                del self.userLibrary[uitem[0].text()]
#                self.saveUserLibrary()
#                self.loadUserLibrary()
#                print 'ojo que no cambia la seleccion luego de eliminar'                
#                self.list_default.setFocus()
#                self.list_default.item(0).setSelected(True)
#                self.changeSelectionDefault()
#                
#        return
#        
#        
#    def addMaterial(self):
#        name = self.name.text()
#        self.userLibrary[name] = self.defaults['air'].copy()
#        keys = emptys.keys()
#        for key in keys:
#            if key=='name':
#                self.userLibrary[name][key] = self.__getattribute__(key).text()
#            else:
#                self.userLibrary[name][key][-1] = self.__getattribute__(key).text()
#        self.saveUserLibrary()
#        self.loadUserLibrary()  