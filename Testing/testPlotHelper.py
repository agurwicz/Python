"""
Created on December 27, 2021
@author: Lance A. Endres
"""
import pandas                                                   as pd
import matplotlib.pyplot                                        as plt
import seaborn                                                  as sns

import os

import DataSetLoading
from   lendres.plotting.PlotHelper                              import PlotHelper
from   lendres.plotting.AxesHelper                              import AxesHelper

import unittest


# By default this should be True.  It can be toggled to false if you want to see the
# output for the file saving tests (they won't be deleted).  Be advised, if you set this
# to True, you should perform file clean up operations afterwards.  You can manually delete
# the files, or set this back to True and rerun the tests.
deleteOutput = True


class TestPlotHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        inputFile = "insurance.csv"
        inputFile = DataSetLoading.GetFileInDataDirectory(inputFile)
        cls.data  = pd.read_csv(inputFile)


    def testArtistiPlot(self):
        PlotHelper.NewArtisticFigure()
        plt.show()


    def testPlotStyleFormats(self):
        self.CreateBasicPlot("Format with Defaults")

        # Test using the file extension or not using the file extension.
        self.CreateBasicPlot("Format without Grid Lines with Extension", parameterFile="gridless.mplstyle")
        self.CreateBasicPlot("Format without Grid Lines without Extension", parameterFile="gridless")

        styleFiles = PlotHelper.GetListOfPlotStyles()
        for styleFile in styleFiles:
            self.CreateBasicPlot("Format with "+styleFile, parameterFile=styleFile)


    def testCompareSeabornToSeaborn(self):
        """
        Compare the real Seaborn style to the "seaborn.mplstyle" version.
        """
        sns.set(color_codes=True)
        #print(plt.rcParams)
        axis = plt.gca()
        sns.histplot(self.data["bmi"], kde=True, ax=axis)
        AxesHelper.Label(axis, title="Test Plot", xLabels="Values", yLabels="Count", titleSuffix="Format with Seaborn")
        plt.show()

        self.CreateBasicPlot("Format with Seaborn Using Parameter File", parameterFile="seaborn.mplstyle", scale=0.6)


    def testFormatScales(self):
        self.CreateBasicPlot("Format by Scale", scale=2.0)
        #self.CreateBasicPlot("Format by Width and Height")


    def testSavePlotBeforeShowMethod1(self):
        self.CreateBasicPlot("Save Figure")

        # Test with current figure.
        fileName = "Test Plot.png"
        PlotHelper.SavePlot(fileName)

        fullPath = self.GetFullPath(fileName)
        self.assertTrue(os.path.exists(fullPath))


    def testNumberFormatException(self):
        # Should not cause an exception.
        PlotHelper.GetColorCycle(numberFormat="RGB")
        PlotHelper.GetColorCycle(lineColorCycle="seaborn", numberFormat="hex")

        # Test the exception.
        self.assertRaises(Exception, PlotHelper.GetColorCycle, numberFormat="invalid")


    def CreateBasicPlot(self, titleSuffix, scale=1.0, **kwargs):
        PlotHelper.scale = scale
        PlotHelper.Format(**kwargs)

        axis = plt.gca()
        sns.histplot(self.data["bmi"], kde=True, ax=axis, label="Data")
        AxesHelper.Label(axis, title="Test Plot", xLabels="Values", yLabels="Count", titleSuffix=titleSuffix)

        plt.gca().legend()

        plt.show()
        figure = plt.gcf()

        return figure


    def GetFullPath(self, fileName):
        return os.path.join(PlotHelper.GetDefaultOutputDirectory(), fileName)


    @classmethod
    def tearDownClass(cls):
        # It's not known what test function will be last, so make sure we clean
        # up any files and directories created.
        if deleteOutput:
            PlotHelper.DeleteOutputDirectory()


if __name__ == "__main__":
    unittest.main()