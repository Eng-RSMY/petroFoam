# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from bc_ui import Ui_bcUI
import os

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


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


class bcUI(QtGui.QScrollArea, Ui_bcUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
prototypes = {}
prototypes['wall'] = ['Wall', 'Custom']
prototypes['empty'] = ['Empty']
prototypes['patch'] = ['Pressure Inlet', 'Pressure Outlet', 'Velocity Inlet', 'Mass Flow Inlet', 'Outflow', 'Custom']
prototypes['cyclic'] = ['Cyclic']
prototypes['cyclicAMI'] = ['Cyclic AMI']
prototypes['wedge'] = ['Wedge']
prototypes['symmetry'] = ['Symmetry']

types = {}
types['wall'] = {}
types['wall']['U'] = ['fixedValue', 'zeroGradient', 'slip']
types['wall']['p'] = ['fixedValue', 'zeroGradient', 'fixedFluxPressure', 'fixedValue', 'uniformFixedValue']
types['wall']['p_rgh'] = ['fixedValue', 'zeroGradient', 'fixedFluxPressure', 'uniformFixedValue']
types['wall']['alpha'] = ['fixedValue', 'zeroGradient', 'uniformFixedValue', 'fixedGradient']
types['wall']['k'] = []
types['wall']['epsilon'] = []
types['wall']['omega'] = []
types['wall']['nut'] = []
types['wall']['nuTilda'] = []

types['empty'] = {}
types['empty']['U'] = ['empty']
types['empty']['p'] = ['empty']
types['empty']['p_rgh'] = ['empty']
types['empty']['alpha'] = ['empty']
types['empty']['k'] = ['empty']
types['empty']['epsilon'] = ['empty']
types['empty']['omega'] = ['empty']
types['empty']['nut'] = ['empty']
types['empty']['nuTilda'] = ['empty']

types['symmetry'] = {}
types['symmetry']['U'] = ['symmetry']
types['symmetry']['p'] = ['symmetry']
types['symmetry']['p_rgh'] = ['symmetry']
types['symmetry']['alpha'] = ['symmetry']
types['symmetry']['k'] = ['symmetry']
types['symmetry']['epsilon'] = ['symmetry']
types['symmetry']['omega'] = ['symmetry']
types['symmetry']['nut'] = ['symmetry']
types['symmetry']['nuTilda'] = ['symmetry']

types['wedge'] = {}
types['wedge']['U'] = ['wedge']
types['wedge']['p'] = ['wedge']
types['wedge']['p_rgh'] = ['wedge']
types['wedge']['alpha'] = ['wedge']
types['wedge']['k'] = ['wedge']
types['wedge']['epsilon'] = ['wedge']
types['wedge']['omega'] = ['wedge']
types['wedge']['nut'] = ['wedge']
types['wedge']['nuTilda'] = ['wedge']

types['patch'] = {}
types['patch']['U'] = ['fixedValue', 'zeroGradient', 'slip', 'flowRateInletVelocity', 'uniformFixedValue']
types['patch']['p'] = ['fixedValue', 'zeroGradient', 'totalPressure']
types['patch']['p_rgh'] = ['fixedValue', 'zeroGradient', 'totalPressure']
types['patch']['alpha'] = ['fixedValue', 'zeroGradient', 'inletOutlet', 'fixedGradient']
types['patch']['k'] = []
types['patch']['epsilon'] = []
types['patch']['omega'] = []
types['patch']['nut'] = []
types['patch']['nuTilda'] = []

class bcWidget(bcUI):

    def __init__(self,folder):
        self.currentFolder = folder
        bcUI.__init__(self)
        
        self.icones = {}
        self.icones['wall'] = QtGui.QIcon()
        self.icones['wall'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/wall16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['empty'] = QtGui.QIcon()
        self.icones['empty'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/empty16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['patch'] = QtGui.QIcon()
        self.icones['patch'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/patch16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['cyclic'] = QtGui.QIcon()
        self.icones['cyclic'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/cyclic16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['cyclicAMI'] = QtGui.QIcon()
        self.icones['cyclicAMI'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/cyclicAMI16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['wedge'] = QtGui.QIcon()
        self.icones['wedge'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/wedge16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['symmetry'] = QtGui.QIcon()
        self.icones['symmetry'].addPixmap(QtGui.QPixmap(_fromUtf8("images/fromHelyx/symmetry16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        
        self.boundaries = BoundaryDict(self.currentFolder)
        
        #veo los campos que tengo en el directorio inicial
        self.timedir = 0
        logname = '%s/dirFeatures.log' % self.currentFolder
        command = 'dirFeaturesFoam -case %s > %s' % (self.currentFolder,logname)
        os.system(command)
        log = open(logname, 'r')
        for linea in log:
            if "Current Time" in linea:
                currtime = linea.split('=')[1].strip()
                self.timedir = '%s/%s'%(self.currentFolder,currtime)
                
        #Levanto todos los campos que tengo en el directorio, suponiendo que el solution modeling hizo correctamente su trabajo
        command = 'rm %s/*~ %s/*.old'%(self.timedir,self.timedir)
        os.system(command)
        self.fields = [ f for f in os.listdir(self.timedir) if f not in ['T0', 'T1', 'T2', 'T3', 'T4', 'nonOrth', 'skew'] ]
                
        for ipatch in self.boundaries.patches():
            Item = QtGui.QListWidgetItem()
            Item.setIcon(self.icones[self.boundaries[ipatch]['type']])
            Item.setText(_translate("bcWidget", ipatch, None))
            self.listWidget.addItem(Item)
            
        for ifield in self.fields:
            self.tabWidget.addTab(QtGui.QWidget(), ifield)
            self.tabWidget.setTabText(self.tabWidget.count(),ifield)
            
    def changeSelection(self):
        ipatch = self.listWidget.currentItem().text()
        self.comboBox.clear()
        self.comboBox.addItems(prototypes[self.boundaries[ipatch]['type']])
        
        ii = 0
        for ifield in self.fields:
            filename = '%s/%s'%(self.timedir,ifield)
            parsedData = ParsedParameterFile(filename,createZipped=False)
            thisPatch = parsedData['boundaryField'][ipatch]
            
            #debo poner un combobox con las opciones por field, ademas agregar debajo entrada para valores segun corresponda
            newComboBox = QtGui.QComboBox()
            newComboBox.addItems(types[self.boundaries[ipatch]['type']][ifield])
            #self.tabWidget.widget(ii).addWidget(newComboBox)
            print types[self.boundaries[ipatch]['type']][ifield]
                     
            ii = ii+1
            
        return
        
    def changePrototype(self):
        return
        
    def saveBCs(self):
        return