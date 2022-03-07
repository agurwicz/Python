# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 07:49:25 2022

@author: Lance
"""

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import metrics

import lendres
from lendres.ModelHelper import ModelHelper

class CategoricalRegressionHelper(ModelHelper):

    def __init__(self, dataHelper):
        """
        Constructor.

        Parameters
        ----------
        dataHelper : DataHelper
            DataHelper that has the data in a pandas.DataFrame.

        Returns
        -------
        None.
        """
        super().__init__(dataHelper)


    def ConvertCategoryToNumeric(self, column, trueValue):
        """
        Takes a column that has a categorical type with the categories represented
        as something other than integers and convertes it to integers.  Useful for
        converting text based columns into columns useful for model building.

        Assumes the column only has two category types so that it can be converted
        into a binary representation (0 or 1).

        This is normally done with the pandas.get_dummies function.  This function
        differs by allowing you to specify which value in the column is converted
        to true and which is converted to false.  In the pandas function, you do
        not have that choice.

        Parameters
        ----------
        column : string
            The column to convert.
        trueValue : string or other type comparable with the "==" operator.
            The value in the column that is consided to be the "true" or "1" value.  This
            value will be output as 1, the other value as 0.

        Returns
        -------
        newColumn : string
            Name of the new column added to the data.

        """
        # Perform a check to make sure we can continue.
        if len(self.dataHelper.data) == 0:
            raise Exception("The data has not been set.")

        # Create a new column and initialize it to all zeros.
        newColumn                          = column + "_int"
        self.dataHelper.data[newColumn]    = 0

        # Add the original column name to a list that will be used to drop columns
        # when it is time to build a model.
        self.additionalDroppedColumns.append(column)

        # Set the locations that have the "trueValue" as equal to one.
        self.dataHelper.data.loc[self.dataHelper.data[column] == trueValue, newColumn] = 1

        # Return the name of the new column that was added to the data.
        return newColumn


    def CreateFeatureImportancePlot(self, scale=1.0):
        """
        Plots importance factors as a bar plot.

        Parameters
        ----------
        scale : double
            Scaling parameter used to adjust the plot fonts, lineweights, et cetera for the output scale of the plot.

        Returns
        -------
        None.
        """
        # Must be run before creating figure or plotting data.
        lendres.Plotting.FormatPlot(scale=scale)

        # Need the values in the reverse order (smallest to largest) for the bar plot to get the largest value on
        # the top (highest index position).
        importancesDataFrame = self.GetSortedImportance(ascending=True)
        indices              = range(importancesDataFrame.shape[0])

        # Must be run before creating figure or plotting data.
        lendres.Plotting.FormatPlot(scale=scale)

        plt.barh(indices, importancesDataFrame["Importance"], color="cornflowerblue", align="center")
        plt.yticks(indices, importancesDataFrame.index, fontsize=12*scale)
        plt.gca().set(title="Feature Importances", xlabel="Relative Importance")

        plt.show()


    def GetSortedImportance(self, ascending=False):
        """
        Sorts the importance factors and returns them in a Pandas DataFrame.

        Parameters
        ----------
        ascending : bool
            Specifies if the values should be sorted as ascending or descending.

        Returns
        -------
        : pandas.DataFrame
            DataFrame of the sorted importance values.
        """
        return pd.DataFrame(self.model.feature_importances_,
                            columns=["Importance"],
                            index=self.xTrainingData.columns).sort_values(by="Importance", ascending=ascending)


    def CreateConfusionMatrixPlot(self, dataSet="training", scale=1.0):
        """
        Plots the confusion matrix for the model output.

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
        confusionMatrix : ndarray of shape (n_classes, n_classes)
            The confusion matrix for the data.
        """
        confusionMatrix = self.GetConfusionMatrix(dataSet)

        # The numpy array has to be set as an object type.  If set (or allowed to assume) a
        # type of "str" the entry is created only large enough for the initial string (a character
        # type is used).  It is not possible to append to it.
        labels = np.asarray(
            [
                ["{0:0.0f}".format(item) + "\n{0:.2%}".format(item / confusionMatrix.flatten().sum())]
                for item in confusionMatrix.flatten()
            ]
        ).astype("object").reshape(2, 2)

        # Tack on the type labels to the numerical information.
        labels[0, 0] += "\nTN"
        labels[1, 0] += "\nFN\nType 2"
        labels[0, 1] += "\nFP\nType 1"
        labels[1, 1] += "\nTP"

        # Must be run before creating figure or plotting data.
        # The standard scale for this plot will be a little higher than the normal scale.
        # Not much is shown, so we can shrink the figure size.
        lendres.Plotting.FormatPlot(scale=scale, width=5.35, height=4)

        # Create plot and set the titles.
        axis = sns.heatmap(confusionMatrix, annot=labels, annot_kws={"fontsize" : 14*scale}, fmt="")
        axis.set(title=dataSet.title()+" Data", ylabel="Actual", xlabel="Predicted")

        plt.show()

        return confusionMatrix


    def GetConfusionMatrix(self, dataSet="training"):
        """
        Gets the confusion matrix for the model output.

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
        confusionMatrix : ndarray of shape (n_classes, n_classes)
            The confusion matrix for the data.
        """
        # Initialize to nothing.
        confusionMatrix = None

        # Get the confusion matrix for the correct data set.
        if dataSet == "training":
            if len(self.yTrainingPredicted) == 0:
                self.Predict()
            confusionMatrix = metrics.confusion_matrix(self.yTrainingData, self.yTrainingPredicted)

        elif dataSet == "testing":
            if len(self.yTestingPredicted) == 0:
                self.Predict()
            confusionMatrix = metrics.confusion_matrix(self.yTestingData, self.yTestingPredicted)

        else:
            raise Exception("Invalid data set specified.")

        return confusionMatrix


    def GetModelPerformanceScores(self):
        """
        Calculate performance metrics.  Threshold for a positive result can be specified.

        Parameters
        ----------
        threshold : float
            Threshold for classifying the observation success.

        Returns
        -------
        dataFrame : DataFrame
            DataFrame that contains various performance scores for the training and test data.
        """
        # Make sure the model has been initiated and of the correct type.
        if self.model == None:
            raise Exception("The regression model has not be initiated.")

        if len(self.yTrainingPredicted) == 0:
            raise Exception("The predicted values have not been calculated.")

        # Calculate scores.
        # Accuracy.
        trainingScore   = metrics.accuracy_score(self.yTrainingData, self.yTrainingPredicted)
        testScore       = metrics.accuracy_score(self.yTestingData, self.yTestingPredicted)
        accuracyScores  = [trainingScore, testScore]

        # Recall.
        trainingScore   = metrics.recall_score(self.yTrainingData, self.yTrainingPredicted)
        testScore       = metrics.recall_score(self.yTestingData, self.yTestingPredicted)
        recallScores    = [trainingScore, testScore]

        # Precision.
        trainingScore   = metrics.precision_score(self.yTrainingData, self.yTrainingPredicted, zero_division=0)
        testScore       = metrics.precision_score(self.yTestingData, self.yTestingPredicted, zero_division=0)
        precisionScores = [trainingScore, testScore]

        # F1.
        trainingScore   = metrics.f1_score(self.yTrainingData, self.yTrainingPredicted)
        testScore       = metrics.f1_score(self.yTestingData, self.yTestingPredicted)
        f1Scores        = [trainingScore, testScore]


        # Create a DataFrame for returning the values.
        dataFrame = pd.DataFrame({"Accuracy"  : accuracyScores,
                                  "Recall"    : recallScores,
                                  "Precision" : precisionScores,
                                  "F1"        : f1Scores},
                                 index=["Training", "Testing"])

        return dataFrame