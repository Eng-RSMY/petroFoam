# Pasarlo al setup.py
# https://pypi.python.org/pypi/pyqt-distutils/
# https://gist.github.com/geeksunny/3174947
pyrcc4 -o resources_rc.py resources.qrc
pyuic4 -w petroFoam.ui -o petroFoam_ui.py
pyuic4 -w popUpNew.ui -o popUpNew_ui.py
pyuic4 -w popUpNewFigure.ui -o popUpNewFigure_ui.py
pyuic4 -w figureResiduals.ui -o figureResiduals_ui.py
pyuic4 -w figureTracers.ui -o figureTracers_ui.py
pyuic4 -w figureSampledLine.ui -o figureSampledLine_ui.py
pyuic4 runTimeControls.ui -o runTimeControls_ui.py
pyuic4 numericalSchemes.ui -o numericalSchemes_ui.py
pyuic4 solverSettings.ui -o solverSettings_ui.py
#pyuic4 solutionModeling.ui -o solutionModeling_ui.py
pyuic4 solutionModelingNew.ui -o solutionModeling_ui.py
pyuic4 materials.ui -o materials_ui.py
pyuic4 -w materialsABM.ui -o materialsABM_ui.py
pyuic4 mesh.ui -o mesh_ui.py
pyuic4 -w tracers.ui -o tracers_ui.py
pyuic4 run.ui -o run_ui.py
pyuic4 postpro.ui -o postpro_ui.py
pyuic4 -w bc.ui -o bc_ui.py
pyuic4 initialConditions.ui -o initialConditions_ui.py
pyuic4 -w reset.ui -o reset_ui.py
pyuic4 -w bcPatch.ui -o bcPatch_ui.py
