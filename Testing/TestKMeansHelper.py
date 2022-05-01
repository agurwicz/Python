"""
Created on April 27, 2022
@author: Lance
"""
import DataSetLoading
from lendres.KMeansHelper           import KMeansHelper
import numpy                        as np

from sklearn.preprocessing          import StandardScaler
from scipy.stats                    import zscore
from sklearn.datasets               import make_blobs

import unittest

class TestKMeansHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dataHelper, cls.dependentVariable = DataSetLoading.GetTechnicalSupportData()


        X, y = make_blobs(n_samples=500,
                          n_features=2,
                          centers=4,
                          cluster_std=1,
                          center_box=(-10.0, 10.0),
                          shuffle=True,
                          random_state=1
                         )
        cls.xData = X


    def setUp(self):
        """
        Set up function that runs before each test.  Creates a new copy of the data and uses
        it to create a new regression helper.
        """
        self.dataHelper         = TestKMeansHelper.dataHelper.Copy(deep=True)
        self.kMeansHelper       = KMeansHelper(self.dataHelper)

        scaler                  = StandardScaler()
        self.scaledData         = scaler.fit_transform(self.dataHelper.data.iloc[:,1:])


    def testElbowPlot(self):
        self.kMeansHelper.CreateElbowPlot(self.scaledData, range(2, 10))
        self.kMeansHelper.CreateElbowPlot2(self.scaledData, (2, 10))


    def testSilhouetteGraphicalAnalysis(self):
        self.kMeansHelper.CreateTwoColumnSilhouetteVisualizationPlots(TestKMeansHelper.xData, range(3, 6))

        scaledData = self.dataHelper.data.iloc[:,2:5].apply(zscore).to_numpy()
        self.kMeansHelper.CreateTwoColumnSilhouetteVisualizationPlots(scaledData, range(3, 6))


    def testCreateSilhouetteAnalysisPlots(self):
        self.kMeansHelper.CreateSilhouetteAnalysisPlots(TestKMeansHelper.xData, range(3, 6))


    def testSilhouetteScores(self):
        print()
        self.kMeansHelper.DisplaySilhouetteAnalysScores(TestKMeansHelper.xData, range(2, 10))


    def testBoxPlots(self):
        self.kMeansHelper.DisplaySilhouetteAnalysScores(self.scaledData, range(2, 10))
        self.kMeansHelper.LabelData(np.arange(1, 8), 9)

        data = self.dataHelper.data.copy(deep=True)
        data.drop("PROBLEM_TYPE", axis=1, inplace=True)
        data.drop(self.kMeansHelper.labelColumn, axis=1, inplace=True)
        self.kMeansHelper.CreateBoxPlotForClusters(data, self.dataHelper.data[self.kMeansHelper.labelColumn], 9)


if __name__ == "__main__":
    unittest.main()