# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 07:49:25 2022

@author: Lance
"""
from IPython.display import display

from sklearn import metrics
from sklearn.model_selection import GridSearchCV

class HyperparameterHelper():

    def __init__(self, categoricalHelper):
        """
        Constructor.

        Parameters
        ----------
        categoricalHelper : categoricalHelper
            categoricalHelper (model) used in the grid search.

        Returns
        -------
        None.
        """
        self.categoricalHelper    = categoricalHelper
        self.gridSearch           = None


    def CreateGridSearchModel(self, parameters, scoringFunction, **kwargs):
        """
        Creates a cross validation grid search model.

        Parameters
        ----------
        parameters : dictionary
            Grid search parameters.
        scoringFunction : function
            Method use to calculate a score for the model.
        **kwargs : keyword arguments
            These arguments are passed on to the GridSearchCV.

        Returns
        -------
        None.

        """
        # Make sure there is data to operate on.
        if len(self.categoricalHelper.xTrainingData) == 0:
            raise Exception("The data has not been split.")

        # Type of scoring used to compare parameter combinations.
        scorer = metrics.make_scorer(scoringFunction)

        # Run the grid search.
        self.gridSearch = GridSearchCV(self.categoricalHelper.model, parameters, scoring=scorer, **kwargs)
        self.gridSearch = self.gridSearch.fit(self.categoricalHelper.xTrainingData, self.categoricalHelper.yTrainingData)

        # Set the model (categoricalHelper) to the best combination of parameters.
        self.categoricalHelper.model = self.gridSearch.best_estimator_

        # Fit the best algorithm to the data.
        self.categoricalHelper.model.fit(self.categoricalHelper.xTrainingData, self.categoricalHelper.yTrainingData)


    def DisplayChosenParameters(self):
        """
        Prints the model performance scores.

        Parameters
        ----------
        useMarkDown : bool
            If true, markdown output is enabled.

        Returns
        -------
        None.
        """
        self.categoricalHelper.dataHelper.consoleHelper.PrintBold("Chosen Model Parameters")
        display(self.gridSearch.best_params_)