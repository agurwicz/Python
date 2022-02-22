# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 07:49:25 2022

@author: Lance
"""
import numpy as np

import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.linear_model import LogisticRegression

import lendres
from lendres.CategoricalRegressionHelper import CategoricalRegressionHelper

class LogisticRegressionHelper(CategoricalRegressionHelper):


    def __init__(self, data):
        super().__init__(data)


    def CreateModel(self):
        """
        Creates a linear regression model.  Splits the data and creates the model.

        Parameters
        ----------
        data : pandas.DataFrame
            Data in a pandas.DataFrame
        dependentVariable : string
            Name of the column that has the dependant data.
        testSize : double
            Fraction of the data to use as test data.  Must be in the range of 0-1.

        Returns
        -------
        data : pandas.DataFrame
            Data in a pandas.DataFrame
        """

        if len(self.xTrainingData) == 0:
            raise Exception("The data has not been split.")

        self.model = LogisticRegression(solver="liblinear", random_state=1)
        self.model.fit(self.xTrainingData, self.yTrainingData.values.ravel())


    def PredictProbabilities(self):
        """
        Runs the probability prediction (model.predict_proba) on the training and test data.  The results are stored in
        the yTrainingPredicted and yTestingPredicted variables.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        # Predict probabilities.  The second column (probability of success) is retained.
        # The first column (probability of not-success) is discarded.
        self.yTrainingPredicted = self.model.predict_proba(self.xTrainingData)[:, 1]
        self.yTestingPredicted  = self.model.predict_proba(self.xTestingData)[:, 1]


    def PredictWithThreshold(self, threshold):
        """
        Runs the probability prediction (model.predict_proba) on the training and test data.  The results are stored in
        the yTrainingPredicted and yTestingPredicted variables.

        Parameters
        ----------
        threshold : float
            Threshold for classifying the observation success.

        Returns
        -------
        None.
        """
        # Predictions from the independent variables using the model.
        self.PredictProbabilities()

        self.yTrainingPredicted = self.yTrainingPredicted > threshold
        self.yTestingPredicted  = self.yTestingPredicted  > threshold

        self.yTrainingPredicted = np.round(self.yTrainingPredicted)
        self.yTestingPredicted  = np.round(self.yTestingPredicted)


    def CreateRocCurvePlot(self, dataSet="training", **kwargs):
        """
        Creates a plot of the receiver operatoring characteristic curve(s).

        Parameters
        ----------
        dataSet : string
            Which data set(s) to plot.
            training - Plots the results from the training data.
            testing  - Plots the results from the test data.
            both     - Plots the results from both the training and test data.
        **kwargs :  keyword arguments
            keyword arguments pass on to the plot formating function.

        Returns
        -------
        figure : matplotlib.pyplot.figure
            The newly created figure.
        axis : matplotlib.pyplot.axis
            The axis of the plot.
        """

        self.PredictProbabilities()

        # Must be run before creating figure or plotting data.
        # The standard scale for this plot will be a little higher than the normal scale.
        #scale *= 1.5
        lendres.Plotting.FormatPlot(**kwargs)

        # Plot the ROC curve(s).
        if dataSet == "both":
            self.PlotRocCurve("training")
            self.PlotRocCurve("testing")
        else:
            self.PlotRocCurve(dataSet)

        # Plot the diagonal line, the wrost fit possible line.
        plt.plot([0, 1], [0, 1], "r--")

        # Formatting the axis.
        axis  = plt.gca()
        title = "Logistic Regression\nReceiver Operating Characteristic"
        axis.set(title=title, ylabel="True Positive Rate", xlabel="False Positive Rate")
        axis.set(xlim=[0.0, 1.0], ylim=[0.0, 1.05])

        plt.legend(loc="lower right")
        plt.show()

        figure = plt.gcf()

        return figure, axis


    def PlotRocCurve(self, dataSet="training", scale=1.0):
        """
        Plots the receiver operatoring characteristic curve.

        Parameters
        ----------
        dataSet : string
            Which data set(s) to plot.
            training - Plots the results from the training data.
            testing  - Plots the results from the test data.
        scale : double
            Scaling parameter used to adjust the plot fonts, lineweights, et cetera for the output scale of the plot.

        Returns
        -------
        None.
        """

        # Get the confusion matrix for the correct data set.
        if dataSet == "training":
            rocScore                                          = metrics.roc_auc_score(self.yTrainingData, self.yTrainingPredicted)
            falsePositiveRates, truePositiveRates, thresholds = metrics.roc_curve(self.yTrainingData, self.yTrainingPredicted)
            color                                             = "#1f77b4"

        elif dataSet == "testing":
            rocScore                                          = metrics.roc_auc_score(self.yTestingData, self.yTestingPredicted)
            falsePositiveRates, truePositiveRates, thresholds = metrics.roc_curve(self.yTestingData, self.yTestingPredicted)
            color                                             = "#ff7f0e"

        else:
            raise Exception("Invalid data set specified.")

        plt.plot(falsePositiveRates, truePositiveRates, label=dataSet.title()+ " Data (area = %0.2f)" % rocScore, color=color)