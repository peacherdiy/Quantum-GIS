# -*- coding: utf-8 -*-

"""
***************************************************************************
    dropanalysis.py
    ---------------------
    Date                 : October 2012
    Copyright            : (C) 2012 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


__author__ = 'Alexander Bruy'
__date__ = 'October 2012'
__copyright__ = '(C) 2012, Alexander Bruy'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from PyQt4.QtGui import *

from sextante.core.GeoAlgorithm import GeoAlgorithm
from sextante.core.SextanteLog import SextanteLog
from sextante.core.SextanteUtils import SextanteUtils
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

from sextante.parameters.ParameterRaster import ParameterRaster
from sextante.parameters.ParameterVector import ParameterVector
from sextante.parameters.ParameterNumber import ParameterNumber
from sextante.parameters.ParameterSelection import ParameterSelection

from sextante.outputs.OutputFile import OutputFile

from sextante.taudem.TauDEMUtils import TauDEMUtils

class DropAnalysis(GeoAlgorithm):
    PIT_FILLED_GRID = "PIT_FILLED_GRID"
    D8_CONTRIB_AREA_GRID = "D8_CONTRIB_AREA_GRID"
    D8_FLOW_DIR_GRID = "D8_FLOW_DIR_GRID"
    ACCUM_STREAM_SOURCE_GRID = "ACCUM_STREAM_SOURCE_GRID"
    OUTLETS_SHAPE = "OUTLETS_SHAPE"
    MIN_TRESHOLD = "MIN_TRESHOLD"
    MAX_THRESHOLD = "MAX_THRESHOLD"
    TRESHOLD_NUM = "TRESHOLD_NUM"
    STEP_TYPE = "STEP_TYPE"

    DROP_ANALYSIS_FILE = "DROP_ANALYSIS_FILE"

    STEPS = ["Logarithmic", "Linear"]

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/../images/taudem.png")

    def defineCharacteristics(self):
        self.name = "Stream Drop Analysis"
        self.cmdName = "dropanalysis"
        self.group = "Stream Network Analysis tools"

        self.addParameter(ParameterRaster(self.D8_CONTRIB_AREA_GRID, "D8 Contributing Area Grid", False))
        self.addParameter(ParameterRaster(self.D8_FLOW_DIR_GRID, "D8 Flow Direction Grid", False))
        self.addParameter(ParameterRaster(self.PIT_FILLED_GRID, "Pit Filled Elevation Grid", False))
        self.addParameter(ParameterRaster(self.ACCUM_STREAM_SOURCE_GRID, "Contributing Area Grid", False))
        self.addParameter(ParameterVector(self.OUTLETS_SHAPE, "Outlets Shapefile", ParameterVector.VECTOR_TYPE_POINT, False))
        self.addParameter(ParameterNumber(self.MIN_TRESHOLD, "Minimum Threshold", 0, None, 5))
        self.addParameter(ParameterNumber(self.MAX_THRESHOLD, "Maximum Threshold", 0, None, 500))
        self.addParameter(ParameterNumber(self.TRESHOLD_NUM, "Number of Threshold Values", 0, None, 10))
        self.addParameter(ParameterSelection(self.STEP_TYPE, "Spacing for Threshold Values", self.STEPS, 0))
        self.addOutput(OutputFile(self.DROP_ANALYSIS_FILE, "D-Infinity Drop to Stream Grid"))

    def processAlgorithm(self, progress):
        commands.append(os.path.join(TauDEMUtils.mpiexecPath(), "mpiexec"))

        processNum = SextanteConfig.getSetting(TauDEMUtils.MPI_PROCESSES)
        if processNum <= 0:
          raise GeoAlgorithmExecutionException("Wrong number of MPI processes used.\nPlease set correct number before running TauDEM algorithms.")

        commands.append("-n")
        commands.append(str(processNum))
        commands.append(os.path.join(TauDEMUtils.taudemPath(), self.cmdName))
        commands.append("-ad8")
        commands.append(self.getParameterValue(self.D8_CONTRIB_AREA_GRID))
        commands.append("-p")
        commands.append(self.getParameterValue(self.D8_FLOW_DIR_GRID))
        commands.append("-fel")
        commands.append(self.getParameterValue(self.PIT_FILLED_GRID))
        commands.append("-ssa")
        commands.append(self.getParameterValue(self.ACCUM_STREAM_SOURCE_GRID))
        commands.append("-o")
        commands.append(self.getParameterValue(self.OUTLETS_SHAPE))
        commands.append("-par")
        commands.append(str(self.getParameterValue(self.MIN_TRESHOLD)))
        commands.append(str(self.getParameterValue(self.MAX_THRESHOLD)))
        commands.append(str(self.getParameterValue(self.TRESHOLD_NUM)))
        commands.append(str(self.getParameterValue(self.STEPS)))
        commands.append("-drp")
        commands.append(self.getOutputValue(self.DROP_ANALYSIS_FILE))

        loglines = []
        loglines.append("TauDEM execution command")
        for line in commands:
            loglines.append(line)
        SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)

        TauDEMUtils.executeTauDEM(commands, progress)

    def helpFile(self):
        return os.path.join(os.path.dirname(__file__), "help", self.cmdName + ".html")
