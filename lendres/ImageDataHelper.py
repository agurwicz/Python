"""
Created on June 30, 2022
@author: Lance A. Endres
"""
from   matplotlib                                import pyplot                     as plt
import seaborn                                   as sns
import pandas                                    as pd
import numpy                                     as np
import tensorflow                                as tf
import cv2

import random

from   sklearn.model_selection                   import train_test_split

import lendres
from   lendres.ConsoleHelper                     import ConsoleHelper
from   lendres.PlotHelper                        import PlotHelper
from   lendres.UnivariateAnalysis                import UnivariateAnalysis
from   lendres.Algorithms                        import FindIndicesByValues
from   lendres.ImageHelper                       import ImageHelper


class ImageDataHelper():
    """
    Class for storing and manipulating images for use in a machine learning model.

    General Notes
        - Split the data before preprocessing the images.
            - The class is set up so the original data is preserved in the self.data variable and
              the processed data is in the split variables (xTrainingData, xValidationData, xTestingdata).
              This allows the images to be plotted after processing.  For example, while demonstrating/comparing
              predictions.

    To Do
        Update to use LabelEncoder().
        Add plotting of blurred images that is similar to plotting of chromakey and color separation (before "applying").
    """

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
        self.xTrainingData             = []
        self.xTestingData              = []
        self.xValidationData           = []

        self.yTrainingData             = []
        self.yValidationData           = []
        self.yTestingData              = []

        # Save the console helper first so it can be used while processing things.
        self.consoleHelper  = None
        if consoleHelper == None:
            self.consoleHelper = ConsoleHelper()
        else:
            self.consoleHelper = consoleHelper

        # Initialize the variable.  Helpful to know if something goes wrong.
        self.data                    = []
        self.labels                  = []
        self.yTrainingEncoded        = []
        self.yValidationEncoded      = []
        self.yTestingEncoded         = []
        self.labelCategories         = []
        self.numberOfLabelCategories = 0
        self.colorConversion         = None


    def Copy(self):
        """
        Creates a copy (copy constructor).

        Parameters
        ----------
        deep : bool, optional
            Specifies if a deep copy should be done. The default is False.

        Returns
        -------
        None.
        """
        imageDataHelper                         = ImageDataHelper()
        imageDataHelper.data                    = self.data.copy()
        imageDataHelper.labels                  = self.labels.copy(deep=True)
        imageDataHelper.consoleHelper           = self.consoleHelper

        imageDataHelper.xTrainingData           = self.xTrainingData.copy()
        imageDataHelper.yTrainingData           = self.yTrainingData.copy()

        imageDataHelper.xValidationData         = self.xValidationData.copy()
        imageDataHelper.yValidationData         = self.yValidationData.copy()

        imageDataHelper.xTestingData            = self.xTestingData.copy()
        imageDataHelper.yTestingData            = self.yTestingData.copy()

        imageDataHelper.yTrainingEncoded        = self.yTrainingEncoded.copy()
        imageDataHelper.yValidationEncoded      = self.yValidationEncoded.copy()
        imageDataHelper.yTestingEncoded         = self.yTestingEncoded.copy()

        imageDataHelper.labelCategories         = self.labelCategories.copy()
        imageDataHelper.numberOfLabelCategories = self.numberOfLabelCategories

        imageDataHelper.colorConversion         = self.colorConversion

        return imageDataHelper


    def LoadImagesFromNumpyArray(self, inputFile):
        """
        Loads a data file of images stored as a numpy array.

        Parameters
        ----------
        inputFile : string
            Path and name of the file to load.

        Returns
        -------
        None.
        """
        self.data = np.load(inputFile)


    def LoadLabelsFromCsv(self, inputFile):
        """
        Loads the labels from a CSV file.

        Parameters
        ----------
        inputFile : string
            Path and name of the file to load.

        Returns
        -------
        None.
        """
        self.labels = pd.read_csv(inputFile)
        self.labels.rename(columns={self.labels.columns[0] : "Names"}, inplace=True)

        self.labels["Names"]   = self.labels["Names"].astype("category")
        self.labels["Numbers"] = self.labels["Names"].cat.codes

        uniqueLabels = self.labels["Names"].unique().categories.tolist()
        self.SetLabelCategories(uniqueLabels)


    def LoadLabelNumbersFromCsv(self, inputFile, labelCategories):
        """
        Loads the labels from a CSV file.

        Parameters
        ----------
        inputFile : string
            Path and name of the file to load.

        Returns
        -------
        None.
        """
        self.SetLabelCategories(labelCategories)

        self.labels = pd.read_csv(inputFile)
        self.labels.rename(columns={self.labels.columns[0] : "Numbers"}, inplace=True)

        labels = [self.labelCategories[i] for i in self.labels["Numbers"]]

        self.labels["Names"] = labels
        self.labels["Names"] = self.labels["Names"].astype("category")


    def SetLabelCategories(self, labelCategories):
        """
        Sets the category labels.  These are the unique text labels of the dependent variable.  That is, while
        the text labels and numerical labels for the dependent variable are the length of the number of data samples,
        this is only a few text labels as only one of each category is present.

        The labels should be in the same order as the numerical labels such that a numerical label of i returns the correct
        text name of the category by using self.labelCategories[i].

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        self.labelCategories         = labelCategories
        self.numberOfLabelCategories = len(labelCategories)


    def DisplayLabelCategories(self):
        """
        Neatly displays the label categories.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        labelsDataFrame = pd.DataFrame(self.labelCategories, index=range(0, self.numberOfLabelCategories), columns=["Labels"])
        self.consoleHelper.Display(labelsDataFrame)


    def GetImageShape(self):
        """
        Gets the size of the images.  Can be used as the "input_shape" to a neural network.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        return self.data[0].shape


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
        self.consoleHelper.PrintTitle("Data Sizes")
        self.consoleHelper.Display("Data shape:    {0}".format(self.data.shape))
        self.consoleHelper.Display("Labels length: {0}".format(len(self.data)))

        if len(self.xTrainingData) != 0:
            self.consoleHelper.PrintNewLine()
            self.consoleHelper.Display("Training images shape:  {0}".format(self.xTrainingData.shape))
            self.consoleHelper.Display("Training labels length: {0}".format(len(self.yTrainingData)))

        if len(self.xValidationData) != 0:
            self.consoleHelper.PrintNewLine()
            self.consoleHelper.Display("Validation images shape:  {0}".format(self.xValidationData.shape))
            self.consoleHelper.Display("Validation labels length: {0}".format(len(self.yValidationData)))

        if len(self.xTestingData) != 0:
            self.consoleHelper.PrintNewLine()
            self.consoleHelper.Display("Testing images shape:  {0}".format(self.xTestingData.shape))
            self.consoleHelper.Display("Testing labels length: {0}".format(len(self.yTestingData)))


    def GetDataSet(self, dataSet="original"):
        xData = None
        yData = None

        if dataSet == "original":
            xData = self.data
            yData = self.labels["Numbers"]
        elif dataSet == "training":
            xData = self.xTrainingData
            yData = self.yTrainingData
        elif dataSet == "validation":
            xData = self.xValidationData
            yData = self.yValidationData
        elif dataSet == "testing":
            xData = self.xTestingData
            yData = self.yTestingData
        else:
            raise Exception("Invalid argument for dat type.")

        return xData, yData


    def PlotImage(self, index=None, random=False, size=6):
        """
        Plot example image.

        Parameters
        ----------
        index : index value
            Index value of image to plot.
        random : boolean
            If true, a random image is selected.
        size : float
            Size (width and height) of figure.

        Returns
        -------
        None.
        """
        # Generating random indices from the data and plotting the images.
        if random:
            index = np.random.randint(0, self.labels.shape[0])

        # Get the image.
        image = self.data[index]

        title = self.labels["Names"].loc[index]
        ImageHelper.PlotImage(image, title=title, size=size, colorConversion=self.colorConversion)


    def PlotImages(self, rows=4, columns=4, random=False, indices=None, dataSet="original"):
        """
        Plot example images.

        Parameters
        ----------
        rows : integer
            The number of rows to plot.
        columns : integer
            The number of columns to plot.
        random : boolean
            If true, random images are selected and plotted.  This overrides the value of indices.  That is,
            if true, random images will plot regardless of the value of indices (None or provided).
        indices : list of integers
            If provided, these images are plotted.  If not provided, the first rows*columns are plotted.  Note,
            this argument only has an effect if random=False.

        Returns
        -------
        None.
        """
        xData, yData   = self.GetDataSet(dataSet)
        numberOfImages = len(xData)
        images = []
        labels = []

        # If no indices are provided, we are going to print out the start of the data.
        if indices == None:
            indices = range(rows*columns)

        for k in range(rows*columns):
            # Generating random indices from the data and plotting the images.
            if random:
                index = np.random.randint(0, numberOfImages)
            else:
                index = indices[k]

            # Plotting the image using cmap=gray.
            images.append(xData[index])
            labels.append(self.labelCategories[yData.iloc[index]])

        ImageHelper.CreateImageArrayPlot(images, labels, columns, self.colorConversion)


    def GetIndicesByCategory(self, numberOfExamples, categoryName=None, categoryNumber=None, dataSet="original"):
        """
        Gets the indices of images that fall into the specified category.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of the category to plot.
        categoryName : string
            The name of the category to plot examples of.  Provide the name or the number, but not both.
        categoryNumber : integory
            The number of the category to plot examples of.  Provide the name or the number, but not both.

        Returns
        -------
        indices : array of int
            The indices of images in the specified category.
        """
        # If a name was provided, convert it to a number.  Searching by number is faster.
        if categoryName != None:
            categoryNumber = FindIndicesByValues(self.labelCategories, searchValue=categoryName, maxCount=1)
            # The find indices function returns an array, we only want one entry.
            categoryNumber = categoryNumber[0]

        # If neither name nor number is provided, it is an error.
        if categoryNumber == None:
            raise Exception("A valid category name or a valid category number must be provided.")

        xData, yData = self.GetDataSet(dataSet)
        indices      = FindIndicesByValues(yData, categoryNumber, numberOfExamples)

        if len(indices) == 0:
            categoryName = self.labelCategories[categoryNumber]
            raise Exception("No examples of the category were found.\nCategory Number: "+str(categoryNumber)+"\nCategory Name: "+categoryName)

        return indices


    def PlotImageExamplesByCategory(self, numberOfExamples, categoryName=None, categoryNumber=None, dataSet="original"):
        """
        Plots example images of the specified category type.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of the category to plot.
        categoryName : string
            The name of the category to plot examples of.  Provide the name or the number, but not both.
        categoryNumber : integory
            The number of the category to plot examples of.  Provide the name or the number, but not both.

        Returns
        -------
        None.
        """
        indices = self.GetIndicesByCategory(numberOfExamples, categoryName, categoryNumber, dataSet=dataSet)
        self.PlotImages(rows=1, columns=numberOfExamples, indices=indices, dataSet=dataSet)


    def PlotImageExamplesForAllCategories(self, numberOfExamples, dataSet="original"):
        """
        Plots example images of each category type.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of each category to plot.

        Returns
        -------
        None.
        """
        # Note, the below assumes all categories are numbered in sequence from 0 to numberOfLabelCategories.  That is, the
        # categories cannot be arbitrarily numbered.
        for i in range(self.numberOfLabelCategories):
            # For subsequent sections, add space after the preceeding.
            if i > 0:
                self.consoleHelper.PrintNewLine()

            self.consoleHelper.PrintTitle(self.labelCategories[i])
            self.PlotImageExamplesByCategory(numberOfExamples, categoryNumber=i, dataSet=dataSet)


    def PlotColorChannels(self, indices):
        """
        Plots images along with its separated color channels.

        Parameters
        ----------
        indices : list of index values
            The indices of the images to plot.

        Returns
        -------
        None.
        """
        for index in indices:
            ImageHelper.DisplayColorChannels(self.data[index], self.colorConversion)


    def PlotColorChannelsByCategory(self, numberOfExamples=1, categoryName=None, categoryNumber=None):
        """
        Plots images along with its separated color channels for an image in the specified category.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of the category to plot.
        categoryName : string
            The name of the category to plot examples of.  Provide the name or the number, but not both.
        categoryNumber : integory
            The number of the category to plot examples of.  Provide the name or the number, but not both.

        Returns
        -------
        None.
        """
        indices = self.GetIndicesByCategory(numberOfExamples, categoryName, categoryNumber)

        self.PlotColorChannels(indices)


    def PlotColorChannelsForAllCategories(self, numberOfExamples=1):
        """
        Plots example images of each category type.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of each category to plot.

        Returns
        -------
        None.
        """
        # Note, the below assumes all categories are numbered in sequence from 0 to numberOfLabelCategories.  That is, the
        # categories cannot be arbitrarily numbered.
        for i in range(self.numberOfLabelCategories):
            # For subsequent sections, add space after the preceeding.
            if i > 0:
                self.consoleHelper.PrintNewLine()

            self.consoleHelper.PrintTitle(self.labelCategories[i])
            self.PlotColorChannelsByCategory(numberOfExamples, categoryNumber=i)


    def PlotChromaKeyedImages(self, indices, lowerBounds, upperBounds, maskBlurSize=3, inputBoundsFormat="hsv"):
        """
        Plots chroma keyed images for the specified indices.
        """
        for index in indices:
            ImageHelper.DisplayChromaKey(self.data[index], lowerBounds, upperBounds, maskBlurSize, colorConversion=self.colorConversion, inputBoundsFormat=inputBoundsFormat)


    def PlotChromaKeyedImagesByCategory(self, lowerBounds, upperBounds, maskBlurSize=3, inputBoundsFormat="hsv", categoryName=None, categoryNumber=None, numberOfExamples=1):
        """
        Plots images along with it's separated color channels for an image in the specified category.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of the category to plot.
        categoryName : string
            The name of the category to plot examples of.  Provide the name or the number, but not both.
        categoryNumber : integory
            The number of the category to plot examples of.  Provide the name or the number, but not both.

        Returns
        -------
        None.
        """
        indices = self.GetIndicesByCategory(numberOfExamples, categoryName, categoryNumber)

        self.PlotChromaKeyedImages(indices, lowerBounds, upperBounds, maskBlurSize=maskBlurSize, inputBoundsFormat=inputBoundsFormat)


    def PlotChromaKeyedImagesForAllCategories(self, lowerBounds, upperBounds, maskBlurSize=3, inputBoundsFormat="hsv", numberOfExamples=1):
        """
        Plots example images of each category type.

        Parameters
        ----------
        numberOfExamples : integer
            The number of examples of each category to plot.

        Returns
        -------
        None.
        """
        # Note, the below assumes all categories are numbered in sequence from 0 to numberOfLabelCategories.  That is, the
        # categories cannot be arbitrarily numbered.
        for i in range(self.numberOfLabelCategories):
            # For subsequent sections, add space after the preceeding.
            if i > 0:
                self.consoleHelper.PrintNewLine()

            self.consoleHelper.PrintTitle(self.labelCategories[i])
            self.PlotChromaKeyedImagesByCategory(lowerBounds, upperBounds, maskBlurSize=maskBlurSize, inputBoundsFormat=inputBoundsFormat, categoryNumber=i, numberOfExamples=numberOfExamples)


    def CreateCountPlot(self):
        """
        Creates a count plot of the image categories.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        PlotHelper.FormatPlot()
        axis = sns.countplot(x=self.labels["Names"], palette=sns.color_palette("mako"))
        axis.set(title="Category Count Plot", xlabel="Category", ylabel="Count")
        UnivariateAnalysis.LabelPercentagesOnCountPlot(axis)

        # The categories are labeled by name (text) so rotate the text so it does not run together.
        axis.set_xticklabels(axis.get_xticklabels(), rotation=45, ha="right")
        plt.show()


    def ApplyColorConversion(self, colorConversion=None):
        """
        colorConversion : OpenCV color conversion enumeration.
                    Color conversion to perform before plotting.  Images are plotted in RGB.  For example, if the
                    image is in BGR cv2.COLOR_BGR2RGB should be passed.  If None, self.colorConversion will be used.
        """
        if colorConversion is None:
            if self.colorConversion is None:
                raise Exception("No color conversion has been specified.")
            colorConversion = self.colorConversion

        self.xTrainingData = ImageHelper.ApplyColorConversion(self.xTrainingData, colorConversion)
        if len(self.xValidationData) != 0:
            self.xValidationData = ImageHelper.ApplyColorConversion(self.xValidationData, colorConversion)
        self.xTestingData  = ImageHelper.ApplyColorConversion(self.xTestingData, colorConversion)

        # If there was a color conversion specified, it is no longer needed.
        self.colorConversion = None


    def ApplyGaussianBlur(self, **kwargs):
        """
        Applies a Gaussian blur to the images.  This should be done after splitting.  The original
        data is overwritten.

        Parameters
        ----------
        **kwargs : keyword arguments
            Arguments passed to the Gaussian filter.  For example, "ksize=(5,5), sigmaX=0"

        Returns
        -------
        None.
        """
        self.xTrainingData = ImageHelper.ApplyGaussianBlur(self.xTrainingData, **kwargs)
        if len(self.xValidationData) != 0:
            self.xValidationData = ImageHelper.ApplyGaussianBlur(self.xValidationData, **kwargs)
        self.xTestingData  = ImageHelper.ApplyGaussianBlur(self.xTestingData, **kwargs)


    def ApplyChromaKey(self, lowerBounds, upperBounds, maskBlurSize=3, inputBoundsFormat="hsv", keep="bounded"):
        """
        Applies a chroma key filter to the images.  This should be done after splitting.  The original data is overwritten.

        Parameters
        ----------
        lowerBounds : numpy array of 3 values.
            Lower bounds of mask.
        upperBounds : numpy array of 3 values.
            Upper bounds of mask.
        maskBlurSize : int
            Size of the blur to apply to the mask.  Must be an odd number.
        inputBoundsFormat : string
            Format of lowerBounds and upperBounds.
        keep : string
            Part of the split image to keep.
            bounded : The original image that is bounded by the input.
            remainder : The original image that is outside of the input bounds.
            mask : The mask used to separate the image.

        Returns
        -------
        None.
        """
        self.xTrainingData = ImageHelper.GetChromaKeyPart(self.xTrainingData, lowerBounds, upperBounds, maskBlurSize, inputBoundsFormat, keep)
        if len(self.xValidationData) != 0:
            self.xValidationData = ImageHelper.GetChromaKeyPart(self.xValidationData, lowerBounds, upperBounds, maskBlurSize, inputBoundsFormat, keep)
        self.xTestingData  = ImageHelper.GetChromaKeyPart(self.xTestingData, lowerBounds, upperBounds, maskBlurSize, inputBoundsFormat, keep)


    def NormalizePixelValues(self):
        """
        Normalizes all the pixel valus.  Call after splitting the data.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        self.xTrainingData = self.xTrainingData / 255
        if len(self.xValidationData) != 0:
            self.xValidationData = self.xValidationData / 255
        self.xTestingData  = self.xTestingData / 255


    def SplitData(self, testSize, validationSize=None, stratify=False):
        """
        Creates a linear regression model.  Splits the data and creates the model.

        Parameters
        ----------
        dependentVariable : string
            Name of the column that has the dependant data.
        testSize : double
            Fraction of the data to use as test data.  Must be in the range of 0-1.
        validationSize : double
            Fraction of the non-test data to use as validation data.  Must be in the range of 0-1.
        stratify : bool
            If true, the approximate ratio of value in the dependent variable is maintained.

        Returns
        -------
        data : pandas.DataFrame
            Data in a pandas.DataFrame
        """
        if len(self.data) == 0:
            raise Exception("Data has not been loaded.")

        x = self.data
        y = self.labels["Numbers"]

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


    def GetSplitComparisons(self):
        """
        Returns the value counts and percentages of the dependant variable for the
        original, training (if available), and testing (if available) data.

        Parameters
        ----------
        None.

        Returns
        -------
        comparisonFrame : pandas.DataFrame
            DataFrame with the counts and percentages.
        """
        # Get results for original data.
        dataFrame = self.GetCountAndPrecentStrings(self.labels["Numbers"] ,"Original")

        # If the data has been split, we will add the split information as well.
        if len(self.yTrainingData) != 0:
            dataFrame = pd.concat([dataFrame, self.GetCountAndPrecentStrings(self.yTrainingData, "Training")], axis=1)

            if len(self.yValidationData) != 0:
                dataFrame = pd.concat([dataFrame, self.GetCountAndPrecentStrings(self.yValidationData, "Validation")], axis=1)

            dataFrame = pd.concat([dataFrame, self.GetCountAndPrecentStrings(self.yTestingData, "Testing")], axis=1)

        return dataFrame


    def GetCountAndPrecentStrings(self, dataSet, dataSetName):
        """
        Gets a string that is the value count of "classValue" and the percentage of the total
        that the "classValue" accounts for in the column.

        Parameters
        ----------
        dataSet : string
            Which data set(s) to plot.

        Returns
        -------
        None.
        """
        valueCounts        = [""] * self.numberOfLabelCategories
        totalCount         = len(dataSet)

        # Turn the numbers into formated strings.
        for i in range(self.numberOfLabelCategories):
            classValueCount = sum(dataSet == i)
            valueCounts[i] = "{0} ({1:0.2f}%)".format(classValueCount, classValueCount/totalCount*100)

        # Create the data frame.
        comparisonFrame = pd.DataFrame(
            valueCounts,
            columns=[dataSetName],
            index=self.labelCategories
        )

        return comparisonFrame


    def EncodeCategoricalColumns(self):
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


    def DisplayEncodingResults(self, numberOfEntries, randomEntries=False):
        """
        Prints a summary of the encoding processes.

        Parameters
        ----------
        numberOfEntries : int
            The number of entries to display.
        randomEntries : bool
            If true, random entries are chosen, otherwise, the first few entries are displayed.

        Returns
        -------
        None.
        """
        indices = []
        if randomEntries:
            numberOfImages = len(self.yTrainingEncoded)
            indices = random.sample(range(0, numberOfImages), numberOfEntries)
        else:
            indices = list(range(numberOfEntries))

        self.consoleHelper.PrintTitle("Dependent Variable Numerical Labels")
        yNumbers = self.yTrainingData.iloc[indices]
        self.consoleHelper.Display(pd.DataFrame(yNumbers))

        self.consoleHelper.PrintNewLine()
        self.consoleHelper.PrintTitle("Dependent Variable Text Labels")
        labels = [self.labelCategories[i] for i in yNumbers]
        self.consoleHelper.Display(pd.DataFrame(labels, columns=["Labels"], index=yNumbers.index))

        self.consoleHelper.PrintNewLine()
        self.consoleHelper.PrintTitle("Dependent Variable Encoded Labels")
        self.consoleHelper.Display(pd.DataFrame(self.yTrainingEncoded[indices], index=yNumbers.index))