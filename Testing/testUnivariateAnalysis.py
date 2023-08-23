"""
Created on December 27, 2021
@author: Lance A. Endres
"""
import DataSetLoading

from   lendres.plotting.PlotHelper                              import PlotHelper
from   lendres.UnivariateAnalysis                               import UnivariateAnalysis
from   lendres.plotting.PlotMaker                               import PlotMaker

import unittest


class TestUnivariateAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dataHelper, cls.dependentVariable = DataSetLoading.GetInsuranceData(encode=False)


    def setUp(self):
        self.dataHelper = TestUnivariateAnalysis.dataHelper.Copy()


    def testBoxAndHistorgramPlot(self):
        categories = ["bmi", "charges"]
        PlotHelper.ApplyPlotToEachCategory(self.dataHelper.data, categories, UnivariateAnalysis.CreateBoxAndHistogramPlot)


    def testCreateCountPlot(self):
        categories = ["children", "smoker"]
        PlotHelper.ApplyPlotToEachCategory(self.dataHelper.data, categories, PlotMaker.CreateCountFigure)


    def testCreatBoxPlot(self):
        UnivariateAnalysis.CreateBoxPlot(self.dataHelper.data, "charges")


if __name__ == "__main__":
    unittest.main()