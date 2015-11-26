# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from tracers_ui import tracersUI
import os
import utils
import copy

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


dicc = {}
dicc['type'] = 'scalarTransport';
dicc['functionObjectLibs'] = ("libutilityFunctionObjects.so")
dicc['DT'] = '1e-10'
dicc['resetOnStartUp'] = 'false';
dicc['autoSchemes'] = 'true';
dicc['patchName'] = 'inlet'
dicc['fvOptions'] = {}
dicc['fvOptions']['S'] = {}
dicc['fvOptions']['S']['type'] = 'scalarExplicitSetValue'
dicc['fvOptions']['S']['active'] = 'true'
dicc['fvOptions']['S']['selectionMode'] = 'cellSet'
dicc['fvOptions']['S']['cellSet'] = 'inletcells'
dicc['fvOptions']['S']['timeStart'] = '0'
dicc['fvOptions']['S']['duration'] = '1e6'
dicc['fvOptions']['S']['scalarExplicitSetValueCoeffs'] = {}
dicc['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate'] = {}
dicc['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate']['T0'] = 1

class tracers(tracersUI):

    def __init__(self, currentFolder):
        tracersUI.__init__(self)
        self.currentFolder = currentFolder
        [self.timedir,fields,self.currtime] = utils.currentFields(str(self.currentFolder))
        
        self.tracersData = []
        self.patches = []
        self.emptys = []
                
        self.loadCaseData()
        self.refreshTable()

    def loadCaseData(self):
        filename = '%s/system/controlDict'%self.currentFolder
        self.parsedData = ParsedParameterFile(filename,createZipped=False)
        
        if 'functions' in self.parsedData.getValueDict().keys():
            for key in self.parsedData['functions'].keys():
                print 'Analyzing %s' % key
                if self.parsedData['functions'][key]['type'] == 'scalarTransport':
                    tracer = {}
                    tracer['name'] = key
                    tracer['patchName'] = self.parsedData['functions'][key]['patchName']
                    tracer['startTime'] = self.parsedData['functions'][key]['fvOptions']['S']['timeStart']
                    self.tracersData.append(tracer)
                        
        if self.patches==[]:
            filename = '%s/U'%(self.timedir)
            print filename
            UData = ParsedParameterFile(filename,createZipped=False)
            self.patches = UData['boundaryField'].keys()
            for ipatch in self.patches:
                if UData['boundaryField'][ipatch]['type']=='empty':
                    self.emptys.append(ipatch)
        

    def refreshTable(self):
        for ii in range(self.tableWidget.rowCount()-1,-1,-1):
            self.tableWidget.removeRow(ii)
        
        for i in range(len(self.tracersData)):
            self.tableWidget.insertRow(i)
            item1 = QtGui.QTableWidgetItem()
            item2 = QtGui.QTableWidgetItem()
            wdg1 = QtGui.QLineEdit()
            wdg2 = QtGui.QComboBox()
            wdg2.addItems(list(set(self.patches)-set(self.emptys)))
            
            wdg1.setText(str(self.tracersData[i]['startTime']))
            wdg2.setCurrentIndex(wdg2.findText(self.tracersData[i]['patchName']))
                
            self.tableWidget.setItem(i,0,item1)
            self.tableWidget.setCellWidget(i,0,wdg1) 
            self.tableWidget.setItem(i,1,item2)
            self.tableWidget.setCellWidget(i,1,wdg2)


    def newTracer(self):
        i = self.tableWidget.rowCount()
        self.tableWidget.insertRow(i)
        item1 = QtGui.QTableWidgetItem()
        item2 = QtGui.QTableWidgetItem()
        wdg1 = QtGui.QLineEdit()
        wdg2 = QtGui.QComboBox()
        wdg2.addItems(list(set(self.patches)-set(self.emptys)))
        wdg1.setText('0')
        self.tableWidget.setItem(i,0,item1)
        self.tableWidget.setCellWidget(i,0,wdg1) 
        self.tableWidget.setItem(i,1,item2)
        self.tableWidget.setCellWidget(i,1,wdg2)
                

    def removeTracer(self):
        ii = self.tableWidget.currentRow()
        self.tableWidget.removeRow(ii)
        return
        
    def saveCaseData(self):

        for dd in self.tracersData:
            print 'Eliminando %s'%dd['name']
            del self.parsedData['functions'][dd['name']]
        
        if 'functions' not in self.parsedData.getValueDict().keys():
            self.parsedData['functions'] = {}
            
        for i in range(self.tableWidget.rowCount()):
            newkey = 'T%s'%str(i)
            tracer = copy.deepcopy(dicc)
            tracer['fvOptions']['S']['timeStart'] = self.tableWidget.cellWidget(i,0).text()
            tracer['patchName'] = self.tableWidget.cellWidget(i,1).currentText()
            del tracer['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate']['T0']
            tracer['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate'][newkey] = '1'            
            self.parsedData['functions'][newkey] = tracer
        
        self.parsedData.writeFile()
        
#        zg = {}
#        zg['type'] = 'zeroGradient'
#
#        for i in range(0,5):
#            filename = '%s/T%s'%(self.timedir,str(i))
#            parsedData = ParsedParameterFile(filename,createZipped=False)
#
#            startTime = self.tableWidget.cellWidget(i,0).text()
#            patchname = self.tableWidget.cellWidget(i,1).currentText()
#            
#            oldcb = parsedData['boundaryField'][patchname].copy()
#            if oldcb['type']=='uniformFixedValue':
#                parsedData['boundaryField'][patchname]['uniformValue'][1][2][0] = str(startTime)
#                parsedData['boundaryField'][patchname]['uniformValue'][1][1][0] = str(float(startTime)-0.01)
#            else:
#                #reemplazo el patch viejo 
#                for ipatch in parsedData['boundaryField']:
#                    if parsedData['boundaryField'][ipatch]['type'] == 'uniformFixedValue':
#                        parsedData['boundaryField'][ipatch] = zg.copy()
#                parsedData['boundaryField'][patchname] = oldcb
#                parsedData['boundaryField'][patchname]['type'] = 'uniformFixedValue'
#                parsedData['boundaryField'][patchname]['uniformValue'] = ('table', [[0, 0.0], [1e6-0.01, 0.0], [1e6, 1.0], [1e6, 1.0]])
#                parsedData['boundaryField'][patchname]['uniformValue'][1][2][0] = str(startTime)
#                parsedData['boundaryField'][patchname]['uniformValue'][1][1][0] = str(float(startTime)-0.01)
#            parsedData.writeFile()
        
        return