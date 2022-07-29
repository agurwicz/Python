"""
Created on July 26, 2022
@author: Lance A. Endres
"""
import pandas                                    as pd
from   matplotlib                                import pyplot                     as plt
import seaborn                                   as sns
from   sklearn.model_selection                   import train_test_split

from   lendres.ConsoleHelper                     import ConsoleHelper
from   lendres.PlotHelper                        import PlotHelper


class DataHelperBase():


    def __init__(self, consoleHelper=None):
        """
        Constructor.

        Parameters
        ----------
        consoleHelper : ConsoleHelper
            Class the prints messages.

        Returns
        -------
        None.
        """
        # Initialize the variables.  Helpful to know if something goes wrong.
        self.xTrainingData             = []
        self.xValidationData           = []
        self.xTestingData              = []

        self.yTrainingData             = []
        self.yValidationData           = []
        self.yTestingData              = []

        self.data                      = []

        self.labelEncoders             = {}

        # Save the console helper first so it can be used while processing things.
        self.consoleHelper  = None
        if consoleHelper == None:
            self.consoleHelper = ConsoleHelper()
        else:
            self.consoleHelper = consoleHelper


    def _SplitData(self, x, y, testSize, validationSize=None, stratify=False):
        """
        Splits the data.

        Parameters
        ----------
        x : array like
            Independent data.
        y : array like
            Dependent data.
        testSize : double
            Fraction of the data to use as test data.  Must be in the range of 0-1.
        validationSize : double
            Fraction of the non-test data to use as validation data.  Must be in the range of 0-1.
        stratify : bool
            If true, the approximate ratio of value in the dependent variable is maintained.

        Returns
        -------
        None.
        """
        if len(self.data) == 0:
            raise Exception("Data has not been loaded.")

        if stratify:
            stratifyInput = y
        else:
            stratifyInput = None

        # Split the data.
        self.xTrainingData, self.xTestingData, self.yTrainingData, self.yTestingData = train_test_split(x, y, test_size=testSize, random_state=1, stratify=stratifyInput)

        if validationSize != None:
            if stratify:
                stratifyInput = self.yTrainingData
            else:
                stratifyInput = None
            self.xTrainingData, self.xValidationData, self.yTrainingData, self.yValidationData = train_test_split(self.xTrainingData, self.yTrainingData, test_size=validationSize, random_state=1, stratify=stratifyInput)


    def _GetSplitComparisons(self, originalData, format="countandpercentstring"):
        """
        Returns the value counts and percentages of the dependant variable for the
        original, training (if available), and testing (if available) data.

        Parameters
        ----------
        originalData : array like
            The source data passed from the subclass.
        format : string
            Format of the returned values.
            countandpercentstring  : returns a string that contains both the count and percent.
            numericalcount         : returns the count as a number.
            numericalpercentage    : returns the percentage as a number.

        Returns
        -------
        dataFrame : pandas.DataFrame
            DataFrame with the counts and percentages.
        """
        # Get results for original data.
        dataFrame = self.GetCountAndPrecentStrings(originalData,"Original", format=format)

        # If the data has been split, we will add the split information as well.
        if len(self.yTrainingData) != 0:
            dataFrame = pd.concat([dataFrame, self.GetCountAndPrecentStrings(self.yTrainingData, "Training", format=format)], axis=1)

            if len(self.yValidationData) != 0:
                dataFrame = pd.concat([dataFrame, self.GetCountAndPrecentStrings(self.yValidationData, "Validation", format=format)], axis=1)

            dataFrame = pd.concat([dataFrame, self.GetCountAndPrecentStrings(self.yTestingData, "Testing", format=format)], axis=1)

        return dataFrame



    def CreateSplitComparisonPlot(self):
        """
        Plots the split comparisons.

        Parameters
        ----------
        None.

        Returns
        -------
        figure : Matplotlib figure
            The created figure.
        """
        splits  = self.GetSplitComparisons(format="numericalpercentage")
        columns = splits.columns.values
        splits.reset_index(inplace=True)

        PlotHelper.FormatPlot()
        axis = splits.plot(x="index", y=columns, kind="bar", color=sns.color_palette())
        axis.set(title="Split Comparison", xlabel="Category", ylabel="Percentage")

        figure = plt.gcf()
        plt.show()

        return figure


    def DisplayDataShapes(self):
        """
        Print out the shape of all the data.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        self.consoleHelper.PrintTitle("Data Sizes", ConsoleHelper.VERBOSEREQUESTED)
        self.consoleHelper.Display("Data shape:    {0}".format(self.data.shape), ConsoleHelper.VERBOSEREQUESTED)
        self.consoleHelper.Display("Labels length: {0}".format(len(self.data)), ConsoleHelper.VERBOSEREQUESTED)

        if len(self.xTrainingData) != 0:
            self.consoleHelper.PrintNewLine(ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display("Training images shape:  {0}".format(self.xTrainingData.shape), ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display("Training labels length: {0}".format(len(self.yTrainingData)), ConsoleHelper.VERBOSEREQUESTED)

        if len(self.xValidationData) != 0:
            self.consoleHelper.PrintNewLine(ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display("Validation images shape:  {0}".format(self.xValidationData.shape), ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display("Validation labels length: {0}".format(len(self.yValidationData)), ConsoleHelper.VERBOSEREQUESTED)

        if len(self.xTestingData) != 0:
            self.consoleHelper.PrintNewLine(ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display("Testing images shape:  {0}".format(self.xTestingData.shape), ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display("Testing labels length: {0}".format(len(self.yTestingData)), ConsoleHelper.VERBOSEREQUESTED)


    def EncodeDependentVariableForAI(self):
        """
        Converts the categorical columns ("category" data type) to encoded values.
        Prepares categorical columns for use in a model.

        Parameters
        ----------
        columns : list of strings
            The names of the columns to encode.
        dropFirst : bool
            If true, the first category is dropped for the encoding.

        Returns
        -------
        None.
        """
        self.yTrainingEncoded   = tf.keras.utils.to_categorical(self.yTrainingData)
        if len(self.yValidationData) != 0:
            self.yValidationEncoded = tf.keras.utils.to_categorical(self.yValidationData)
        self.yTestingEncoded    = tf.keras.utils.to_categorical(self.yTestingData)