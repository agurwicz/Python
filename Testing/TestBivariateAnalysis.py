"""
Created on December 27, 2021
@author: Lance
"""
import DataSetLoading

from lendres.ConsoleHelper           import ConsoleHelper
from lendres.BivariateAnalysis       import BivariateAnalysis

import unittest

#import seaborn as sns

class TestBivariateAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.insuranceDataHelper, cls.insuranceDependentVariable = DataSetLoading.GetInsuranceData(verboseLevel=ConsoleHelper.VERBOSEREQUESTED, encode=False)
        cls.cardioDataHelper,    cls.cardioDependentVariable    = DataSetLoading.GetCardioGoodFitnessData(verboseLevel=ConsoleHelper.VERBOSEREQUESTED)


    def setUp(self):
        self.insuranceDataHelper = TestBivariateAnalysis.insuranceDataHelper.Copy(deep=True)
        self.cardioDataHelper    = TestBivariateAnalysis.cardioDataHelper.Copy(deep=True)


    def testHeatMapPlots(self):
        BivariateAnalysis.CreateBivariateHeatMap(self.insuranceDataHelper.data)

        columns = ["age", "charges"]
        BivariateAnalysis.CreateBivariateHeatMap(self.insuranceDataHelper.data, columns)


    def testPairPlots(self):
        BivariateAnalysis.CreateBivariatePairPlot(self.insuranceDataHelper.data)

        BivariateAnalysis.CreateBivariatePairPlot(self.insuranceDataHelper.data, hue="sex")

        columns = ["age", "bmi"]
        BivariateAnalysis.CreateBivariatePairPlot(self.insuranceDataHelper.data, columns)
        BivariateAnalysis.CreateBivariatePairPlot(self.insuranceDataHelper.data, columns, hue="sex")

        columns = list(self.insuranceDataHelper.data.columns)
        BivariateAnalysis.CreateBivariatePairPlot(self.insuranceDataHelper.data, columns, hue="sex")


    def testPlotComparisonByCategory(self):
        BivariateAnalysis.PlotComparisonByCategory(self.insuranceDataHelper.data, "age", "charges", "sex", "Sorted by Sex")


    def testProportionalData(self):
        BivariateAnalysis.CreateComparisonPercentageBarPlot(self.cardioDataHelper.data, "Product", ["TM498", "TM798"], "Gender")


if __name__ == "__main__":
    unittest.main()