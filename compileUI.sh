pyrcc4 -o resources_rc.py resources.qrc
pyuic4 -w petroFoam.ui -o petroFoam_ui.py
pyuic4 -w popUpNew.ui -o popUpNew_ui.py
pyuic4 -w popUpNewFigure.ui -o popUpNewFigure_ui.py
pyuic4 -w figureResiduals.ui -o figureResiduals_ui.py
pyuic4 -w figureSampledLine.ui -o figureSampledLine_ui.py
pyuic4 runTimeControls.ui -o runTimeControls_ui.py
pyuic4 solutionModeling.ui -o solutionModeling_ui.py

