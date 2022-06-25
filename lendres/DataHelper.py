"""
Created on December 27, 2021
@author: Lance A. Endres
"""
import pandas                                    as pd
import numpy                                     as np
import scipy.stats                               as stats

from   sklearn.model_selection                   import train_test_split
from   sklearn.preprocessing                     import StandardScaler
from   scipy.stats                               import zscore

import os
import io

import lendres
from   lendres.ConsoleHelper                     import ConsoleHelper

class DataHelper():

    def __init__(self, fileName=None, data=None, copy=False, deep=False, consoleHelper=None):
        """
        Constructor.

        Parameters
        ----------
        fileName : stirng, optional
            Path to load the data from.  This is a shortcut for creating a DataHelper and
            then calling "LoadAndInspectData."
        data : pandas.DataFrame, optional
            DataFrame to operate on. The default is None.  If None is specified, the
            data should be loaded in a separate function call, e.g., with "LoadAndInspectData"
            or by providing a fileName to load the data from.  You cannot provide both a file
            and data.
        deep : bool, optional
            Specifies if a deep copy should be done. The default is False.  Only valid if
            the "data" parameter is specified.
        consoleHelper : ConsoleHelper
            Class the prints messages.  The following verbose levels are used.
            Specified how much output should be written. The default is 2.
            0 : None.  Use with caution.
            1 : Erors and warnings are output.
            2 : All messages are output.

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
        self.data = None

        # Either load the data from file or the supplied existing data, but not both.
        if fileName is not None:
            self.LoadAndInspectData(fileName)

        elif data is not None:
            if copy:
                self.data = data.copy(deep)
            else:
                self.data = data


    @classmethod
    def CopyFrom(cls, original, deep=False):
        """
        Creates a copy from another DataHelper (copy constructor).

        Parameters
        ----------
        original : DataHelper
            The source of the data.
        deep : bool, optional
            Specifies if a deep copy should be done. The default is False.

        Returns
        -------
        None.
        """
        dataHelper                = DataHelper()
        dataHelper.data           = original.data.copy(deep)
        dataHelper.consoleHelper  = original.consoleHelper
        return dataHelper


    def Copy(self, deep=False):
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
        dataHelper                = DataHelper()
        dataHelper.data           = self.data.copy(deep)
        dataHelper.consoleHelper  = self.consoleHelper

        if len(self.xTrainingData) != 0:
            dataHelper.xTrainingData             = self.xTrainingData.copy(deep=deep)
            dataHelper.yTrainingData             = self.yTrainingData.copy(deep=deep)

        if len(self.xValidationData) != 0:
            dataHelper.xValidationData           = self.xValidationData.copy(deep=deep)
            dataHelper.yValidationData           = self.yValidationData.copy(deep=deep)

        if len(self.xTestingData) != 0:
            dataHelper.xTestingData              = self.xTestingData.copy(deep=deep)
            dataHelper.yTestingData              = self.yTestingData.copy(deep=deep)

        return dataHelper


    def LoadAndInspectData(self, inputFile):
        """
        Loads a data file and performs some initial inspections and reports results.

        Parameters
        ----------
        inputFile : string
            Path and name of the file to load.

        Returns
        -------
        data : pandas.DataFrame
            Data in a pandas.DataFrame
        """

        # Validate the input file.
        if type(inputFile) != str:
            raise Exception("The input file is not a string.")

        if not os.path.exists(inputFile):
            raise Exception("The input file \"" + inputFile + "\" does not exist.")


        # Read the file in.
        self.consoleHelper.PrintTitle("Input File: " + inputFile)
        self.data = pd.read_csv(inputFile)

        # Data size and shape.
        self.consoleHelper.PrintTitle("Data Size")
        self.consoleHelper.Display(self.data.shape)

        # The first few records.
        self.consoleHelper.PrintTitle("First Few Records")
        self.consoleHelper.Display(self.data.head())

        # Random records.
        np.random.seed(1)
        self.consoleHelper.PrintTitle("Random Sampling")
        self.consoleHelper.Display(self.data.sample(n=10))

        # Data summary (mean, min, max, et cetera.
        self.consoleHelper.PrintTitle("Data Summary")
        self.consoleHelper.Display(self.data.describe())

        # Check data types.
        buffer = io.StringIO()
        self.data.info(buf=buffer)
        self.consoleHelper.PrintTitle("Data Types")
        self.consoleHelper.Print(buffer.getvalue())

        # Check unique value counts.
        self.consoleHelper.PrintTitle("Unique Counts")
        self.consoleHelper.Display(self.data.nunique())

        # See if there are any missing entries, if so they will have to be cleaned.
        self.PrintNotAvailableCounts()

        return self.data


    def PrintFinalDataSummary(self):
        """
        Prints a final data summary.

        Returns
        -------
        None.
        """
        self.consoleHelper.PrintTitle("Data Size", ConsoleHelper.VERBOSEREQUESTED)
        self.consoleHelper.Display(self.data.shape, ConsoleHelper.VERBOSEREQUESTED)

        self.consoleHelper.PrintTitle("Data Types", ConsoleHelper.VERBOSEREQUESTED)
        self.consoleHelper.Display(self.data.info(), ConsoleHelper.VERBOSEREQUESTED)

        self.consoleHelper.PrintTitle("Continuous Data", ConsoleHelper.VERBOSEREQUESTED)
        self.consoleHelper.Display(self.data.describe().T, ConsoleHelper.VERBOSEREQUESTED)

        if self.data.select_dtypes(include=['category']).shape[1] > 0:
            self.consoleHelper.PrintTitle("Categorical", ConsoleHelper.VERBOSEREQUESTED)
            self.consoleHelper.Display(self.data.describe(include=["category"]).T, ConsoleHelper.VERBOSEREQUESTED)


    def PrintNotAvailableCounts(self):
        """
        Prints the counts of any missing (not available) entries.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        notAvailableCounts, totalNotAvailable = self.GetNotAvailableCounts()

        self.consoleHelper.PrintTitle("Missing Entry Counts")
        self.consoleHelper.Display(notAvailableCounts)

        if totalNotAvailable:
            self.consoleHelper.PrintWarning("Some data entries are missing.")
            self.consoleHelper.Print("Total missing: "+str(totalNotAvailable))
        else:
            self.consoleHelper.Print("No entries are missing.")


    def GetNotAvailableCounts(self):
        """
        Gets the counts of any missing (not available) entries.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        notAvailableCounts = self.data.isna().sum()
        totalNotAvailable  = sum(notAvailableCounts)
        return notAvailableCounts, totalNotAvailable


    def DisplayUniqueValues(self, columns):
        """
        Prints a list of the unique values in a column.

        Parameters
        ----------
        columns : list of strings
            Columns to display the counts for.

        Returns
        -------
        None.
        """
        for column in columns:
            title  = "Unique counts in \"" + column + "\":"
            self.consoleHelper.PrintTitle(title, ConsoleHelper.VERBOSEREQUESTED)

            values = pd.DataFrame(np.sort(self.data[column].unique()), columns=["Values"])
            self.consoleHelper.Display(values, ConsoleHelper.VERBOSEREQUESTED)


    def DisplayCategoryCounts(self, columns):
        """
        Displays all the values counts for the specified columns columns.

        Will not dispaly NaN values.

        Parameters
        ----------
        columns : list, array of strings
            Names of the columns to operate on.

        Returns
        -------
        None.
        """
        for column in columns:
            title  = "Category counts in \"" + column + "\":"
            self.consoleHelper.PrintTitle(title, ConsoleHelper.VERBOSEREQUESTED)

            self.consoleHelper.Display(self.data[column].value_counts(), ConsoleHelper.VERBOSEREQUESTED)


    def DisplayAllCategoriesValueCounts(self):
        """
        Displays the value counts of all columns of type "category."

        Will not dispaly NaN values.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        # Find all the category types in the DataFrame and passes them to the display function.
        self.DisplayCategoryCounts(self.data.dtypes[self.data.dtypes == "category"].index)


    def ApplyTo(self, columns, function):
        """
        Runs a function on every column in the list.

        This runs the "apply" operation on the columns.  Therefore, "function" must take a
        pandas Series as the input.

        Parameters
        ----------
        columns : list of strings
            Columns to operate on.
        function : function
            The function that is applied to each column.

        Returns
        -------
        None.
        """
        for column in columns:
             self.data[column] = self.data[column].apply(function)


    def ChangeToCategoryType(self, columns):
        """
        Changes the specified columns to type "category."

        Parameters
        ----------
        columns : list, array of strings
            Names of the columns to change to the category data type.

        Returns
        -------
        None.
        """
        for column in columns:
            self.data[column] = self.data[column].astype("category")


    def ChangeAllObjectColumnsToCategories(self):
        """
        Changes all the columns with the "object" data type to the "category" data type.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        columnNames = self.data.dtypes[self.data.dtypes == "object"].index
        self.ChangeToCategoryType(columnNames)


    def ChangeAllCategoryColumnsToIntegers(self):
        """
        Changes all the columns with the "category" data type to the "integer" data type.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        columnNames = self.data.dtypes[self.data.dtypes == "category"].index
        self.data[columnNames] = self.data[columnNames].astype("int")


    def GetDuplicates(self, column):
        # Returns a list that has True/False values at the duplicate entries.
        duplicates         = self.dataHelper.data.duplicated(subset=[column], keep=False)

        # Gets the indices of just the "True" (duplicate) entries.
        indices            = duplicates[duplicates == True].index

        # Extract the duplicate entries from the main DataFrame and sort them by the
        # column of interest.
        duplicateDataFrame = self.dataHelper.data.iloc[indices, :].sort_values(by=[column])
        return duplicateDataFrame


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
        not have that choice.  It also maintains the column name.  This can be
        useful when dealing with a dependent variable.  If get_dummies is used,
        the new column name would have to be determined.

        Parameters
        ----------
        column : string
            The column to convert.
        trueValue : string or other type comparable with the "==" operator.
            The value in the column that is consided to be the "true" or "1" value.  This
            value will be output as 1, the other value as 0.

        Returns
        -------
        None.
        """
        if pd.api.types.is_categorical_dtype(self.data[column]):
            self.data[column] = self.data[column].astype("object")

        # Set the locations that have the "trueValue" as equal to one.  Have to do the not equal first.
        self.data.loc[self.data[column] != trueValue, column] = 0
        self.data.loc[self.data[column] == trueValue, column] = 1
        self.data[column] = self.data[column].astype("int")


    def DropRowsWhereDataNotAvailable(self, columns):
        """
        Drops any rows that do not have data available in the column.

        Parameters
        ----------
        columns : list of strings
            Name of the columns to look for not available entries.

        Returns
        -------
        None.
        """
        for column in columns:
            # Gets an Series of boolean values indicating where values were not available.
            indexMask = self.data[column].isna()

            # The indexMask is a Series that has the indexes from the original DataFrame and the values are the result
            # of the test statement (bools).  The indices do not necessarily correspond to the location in the DataFrame.  For
            # example some rows may have been removed.  Extract only the indices we want to remove by using the mask itself.
            dropIndices = indexMask[indexMask].index

            # Drop the rows.
            self.data.drop(dropIndices, inplace=True)


    def DropAllRowsWhereDataNotAvailable(self, inPlace=True):
        """
        Drops any rows that are missing one or more entries from the data.

        Parameters
        ----------
        inPlace : bool, optional
            If true, the modifications are done in place.  Default is true.

        Returns
        -------
        : pandas.DataFrame or None
            DataFrame without the removed rows or None if inPlace=True.
        """
        # Gets an self.dataSeries of boolean values indicating where values were not available.
        # to_numpy returns array inside of a tuple for some odd reason.  The [0] extracts the array.
        dropIndices = self.data.isna().sum(axis=1).to_numpy().nonzero()[0]

        # Drop the rows.
        return self.data.drop(dropIndices, inplace=inPlace)


    def GetRowsWithMissingEntries(self):
        """
        Gets the rows that contain missing data.

        Parameters
        ----------
        None.

        Returns
        -------
        locations : numpy array
            A list that contains the indices of the rows that contain at least one missing entry.
        count : int
            Number of rows with missing entries.
        """
        locations = self.data.isna().sum(axis=1).to_numpy().nonzero()[0]
        count     = len(locations)

        return locations, count


    def ExtractLastStringTokens(self, columns):
        """
        Gets the second string token from all entries in the specified columns.

        Parameters
        ----------
        columns : list, array of strings
            Names of the columns to operate on.

        Returns
        -------
        dataFrame : pandas.DataFrame
            A DataFrame that contains the string tokens.
        """
        # Initialize variables.
        numberOfRows    = self.data.shape[0]
        dataFrame       = pd.DataFrame(index=range(numberOfRows), columns=columns)

        # Extract all the units information from the cells.  Loop over all the cells and extract the second half of the split string.
        for column in columns:
            for i in range(numberOfRows):
                value = self.data[column].iloc[i]
                dataFrame[column].iloc[i] = value.split()[1]

        return dataFrame


    def KeepFirstStringToken(self, value):
        """
        Takes a string that has multiple tokens and keeps only the first.

        Parameters
        ----------
        value : string
            The entry to be split.

        Returns
        -------
        : string
            The first token of the string.
        """
        # Make sure we are processing a string.
        if isinstance(value, str):
            # Splits the string at the space and returns the first entry as a number.
            return value.split()[0]

        else:
            # Entry wasn't a string, return an empty string.
            return ""


    def KeepFirstTokenAsNumber(self, value):
        """
        Takes a string that has two tokens (a number followed by a string), extracts the numerical part, and returns it as a float.

        Parameters
        ----------
        value : string
            The entry to be split.

        Returns
        -------
        value : float
            The first token of the string as a number of np.nan if the entry was not a string or number.
        """
        # Make sure we are processing a string.
        if isinstance(value, str):
            # Splits the string at the space and returns the first entry as a number.
            return float(value.split()[0])

        elif isinstance(value, float):
            # Already a number, return it.
            return value

        else:
            # Entry wasn't a string or number, so return an out of range value.
            return np.nan


    def ConvertMileage(self, value):
        """
        Takes a value from the mileage column, strips the units string, converts the units, and returns it as a float.

        Parameters
        ----------
        value : string
            The entry to be split.

        Returns
        -------
        value : float
            The mileage as km per liter or np.nan if entry was not a string or number.
        """
        # Make sure we are processing a string.
        if isinstance(value, str):
            # Splits the string at the space and returns the first entry as a number.
            splitString = value.split()
            value       = float(splitString[0])

            if splitString[1] == "km/kg":
                # Approximately 1.35 kg/liter.
                # km   1.35 kg   km
                # -- * ------  = --
                # kg     l       l
                value *= 1.35

            return value

        elif isinstance(value, float):
            # Already a number, return it.
            return value

        else:
            # Entry wasn't a string or number, so return an out of range value.
            return np.nan


    def GetMinAndMaxValues(self, column, criteria, method="quantity"):
        """
        Display and maximum and minimum values in a Series.

        Parameters
        ----------
        column : string
            Names of the column to sort and display.
        criteria : list of two floats or a float
            The criteria used to determine which numbers are dropped.  See "method" for more information.
        method : string
            How to determine which values are dropped.
                percent - A percentage of the top and bottom values are dropped.
                quantity - The number of values specified is dropped.

        Returns
        -------
        : pandas.DataFrame
            A DataFrame that has both the minimum and maximum values, along with the indices where those values
            occur.  The DataFrame contains the following headings:
            Smallest_Index", "Smallest", "Largest_Index", "Largest"
        """
        # Initialize the variable so it is in scope.
        numberOfRows = criteria

        if method == "quantity":
            # Handled by the initialization above, no need to do anything except that the stupid ass Python parser
            # thinks it needs something.
            numberOfRows = criteria
        elif method == "percent":
            # Convert the fraction to a number of rows.
            numberOfRows = round(len(self.data[column]) * criteria / 100)
        else:
            # A boo-boo was made.
            raise Exception("Invalid \"method\" specified.")

        # Sort then display the start and end of the series.
        sortedSeries = self.data[column].sort_values()

        # Create new DataFrames for the head (smallest values) and the tail (largest values).
        # Reset the index to move the index to a column and create a new, renumbered index.  This lets us combine the two DataFrames at
        # the same index and saves the indices so we can use them later.
        # Also rename the columns to make them more meaningful.
        head = sortedSeries.head(numberOfRows).reset_index()
        head.rename({"index" : "Smallest_Index", column : "Smallest"}, axis=1, inplace=True)

        tail = sortedSeries.tail(numberOfRows).reset_index()
        tail.rename({"index" : "Largest_Index", column : "Largest"}, axis=1, inplace=True)

        # Combine the two along the columns and return the result.
        return pd.concat([head, tail], axis=1)


    def ReplaceLowOutlierWithMean(self, column, criteria):
        """
        Replaces values beyond the criteria with the mean value for the column.  Done in place.

        Parameters
        ----------
        column : string
            Column name in the data.
        criteria : float
            Criteria used to determine what is an outlier.

        Returns
        -------
        None.
        """
        mean = self.data[column].mean()
        self.data.loc[self.data[column] < criteria, column] = mean


    def DropMinAndMaxValues(self, column, criteria, method="fraction", inPlace=False):
        """
        Drops any rows that do not have data available in the column of "column."

        Parameters
        ----------
        column : string
            Names of the column to look for not available entries.
        criteria : list of two floats or a float
            The criteria used to determine which numbers are dropped.  See "method" for more information.
        method : string
            How to determine which values are dropped.
                fraction - A percentage of the top and bottom values are dropped.
                quantity - The number of values specified is dropped.
        inPlace : bool
            If true, the modifications are done in place.

        Returns
        -------
        data : pandas.DataFrame
            DataFrame without the removed rows or None if inPlace=True.
        """
        # This will return a struction that has the values and the indices of the minimums and maximums.
        minAndMaxValues = self.GetMinAndMaxValues(column, criteria, method=method)

        # numpy.where returns array inside of a tuple for some odd reason.  The [0] extracts the array.
        dropIndices = pd.concat([minAndMaxValues["Smallest_Index"], minAndMaxValues["Largest_Index"]])

        # Drop the rows.
        return self.data.drop(dropIndices, inplace=inPlace)


    def DropOutliers(self, columns, irqScale=1.5):
        """
        Drops any rows that are considered outliers by the definition of

        Parameters
        ----------
        columns : string or list of strings
            Names of the column(s) to have outliers dropped.
        irqScale : float
            Scale factor of interquartile range used to define outliers.

        Returns
        -------
        data : pandas.DataFrame
            DataFrame without the removed rows or None if inPlace=True.
        """
        if type(columns) != list:
            columns = [columns]

        for column in columns:
            # Get the stats we need.
            interQuartileRange = stats.iqr(self.data[column])
            limits             = np.quantile(self.data[column], q=(0.25, 0.75))

            # Set the outlier limits.
            limits[0] -= irqScale*interQuartileRange
            limits[1] += irqScale*interQuartileRange

            # Gets an Series of boolean values indicating where values are outside of the range.  These are the
            # values we want to drop.
            indexMask = (self.data[column] < limits[0]) | (self.data[column] > limits[1])

            # The indexMask is a Series that has the indexes from the original DataFrame and the values are the result
            # of the test statement (bools).  The indices do not necessarily correspond to the location in the DataFrame.  For
            # example some rows may have been removed.  Extract only the indices we want to remove by using the mask itself.
            dropIndices = indexMask[indexMask].index

            # Drop the rows.
            self.data.drop(dropIndices, inplace=True)


    def RemoveAllUnusedCategories(self):
        """
        Removes any unused categories (value count is zero) from all series that are of type "column."
        Performs operation "in place."

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        # Find all the column types in the DataFrame and loop over them.
        for column in self.data.dtypes[self.data.dtypes == "category"].index:
            self.data[column] = self.data[column].cat.remove_unused_categories()


    def RemoveRowsWithLowValueCounts(self, column, criteria):
        """
        Finds the entries in "column" with low value counts and drops them.
        Performs operation in place.

        Parameters
        ----------
        column : string
            Column to search through.
        criteria : int
            Values counts less than this value will be dropped.

        Returns
        -------
        None.
        """
        # Get the value counts of the column.
        valueCounts = self.data[column].value_counts()

        # Extract the values that are below the threshold criteria.
        dropValues = valueCounts[valueCounts.values < criteria].index.tolist()

        # Drop the rows.
        for value in dropValues:
             self.RemoveRowByEntryValue(column, value, inPlace=True)


    def RemoveRowByEntryValue(self, column, value, inPlace=True):
        """
        Finds the locations in "column" that are equal to "value" and drops those rows.

        Parameters
        ----------
        column : string
            Column to search through.
        value : type of data in column
            Value to search for and remove.
        inPlace : bool
            Specified is the operation should be performed in place.

        Returns
        -------
        data : pandas.DataFrame
            DataFrame without the removed rows or None if inPlace=True.
        """
        # Gets indices of the rows we want to drop.
        dropIndices = self.data[self.data[column] == value].index.tolist()

        # Drop the rows.
        return self.data.drop(dropIndices, inplace=inPlace)


    def RemoveRowsWithValueOutsideOfCriteria(self, column, criteria, method, inPlace=False):
        """
        Replaces values beyond the criteria with the mean value for the column.  Done in place.

        Parameters
        ----------
        column: string
            Column name in the DataFrame.
        criteria : float
            Values below this will be removed.
        method : string
            Determines if high values or low values should be dropped.
                dropabove - Values above the criteria are removed.
                dropbelow - Values below the criteria are removed.
        inPlace : bool
            If true, the modifications are done in place.

        Returns
        -------
        data : pandas.DataFrame
            DataFrame without the removed rows or None if inPlace=True.
        """
        # Gets an Series of boolean values indicating where values are outside of the range.  These are the
        # values we want to drop.
        indexMask = None
        if method == "dropabove":
            indexMask = self.data[column] > criteria
        elif method == "dropbelow":
            indexMask = self.data[column] < criteria
        else:
            raise Exception("Invalid \"method\" specified.")

        # The indexMask is a Series that has the indexes from the original DataFrame and the values are the result
        # of the test statement (bools).  The indices do not necessarily correspond to the location in the DataFrame.  For
        # example some rows may have been removed.  Extract only the indices we want to remove by using the mask itself.
        dropIndices = indexMask[indexMask].index

        # Drop the rows.
        return self.data.drop(dropIndices, inplace=inPlace)


    def MergeCategories(self, column, fromCategories, toCategory):
        """
        Replaces every instance of a value ("from") with another in a column ("to").  Multiple from values can be
        specified at once.
        Useful for merging categories of a categorical column.
        Operation performed in place.

        Parameters
        ----------
        column : string
            Column name to perform the operate on.
        fromCategories : list
            List of items that will be converted.
        toCategory : string
            Item that all the "fromCategories" get converted to.

        Returns
        -------
        None.
        """
        for fromCategory in fromCategories:
            self.data[column] = self.data[column].replace({fromCategory : toCategory})


    def MergeNumericalDataByRange(self, column, labels, boundaries, replaceExisting=False):
        """
        Take a numerical column and groups them into categories based on range boundaries.

        Parameters
        ----------
        column : string
            Column name to perform the merge on.
        labels : list of strings
            A list that specifies the names for each range.
        boundaries : list of ints or floats
            A list that specifies the end points of the ranges.
        replaceExisting : bool
            If true, the existing column of data is replaced by the new column of merged data.

        Returns
        -------
        newColumnName : string
            Name of the new column that contains the categorized numbers.
        """
        newColumn      = pd.Series(np.zeros(self.data.shape[0]))
        existingColumn = self.data[column]

        for i in range(existingColumn.size):
            boundedIndices   = lendres.Algorithms.BoundingBinarySearch(existingColumn.iloc[i], boundaries, returnedUnits="indices")
            newColumn.loc[i] = labels[boundedIndices[0]]

        # Default to the original column name, then determine how to procede based on if we are to replace
        # the existing column or add a new one while retaining the original one.
        newColumnName = column
        if replaceExisting:
            self.data.drop([column], axis=1, inplace=True)
        else:
            newColumnName = column + "_categories"

        self.data[newColumnName] = newColumn.astype("category")
        return newColumnName


    def EncodeAllCategoricalColumns(self, dropFirst=True):
        """
        Converts all categorical columns (that have data type "category") to encoded values.
        Prepares categorical columns for use in a model.

        Parameters
        ----------
        dropFirst : bool
            If true, the first category is dropped for the encoding (one hot encoding).

        Returns
        -------
        None.
        """
        # Find all the category types in the data.
        # Gets all the columns that have the category data type.  That is returned as a DataSeries.  The
        # index (where the names are) is extracted from that.
        allCategoricalColumns = self.data.dtypes[self.data.dtypes == "category"].index.tolist()
        self.EncodeCategoricalColumns(allCategoricalColumns, dropFirst)


    def EncodeCategoricalColumns(self, columns, dropFirst=True):
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
        self.data = pd.get_dummies(self.data, columns=columns, drop_first=dropFirst)


    def SplitData(self, dependentVariable, testSize, validationSize=None, stratify=False):
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
        # Remove the dependent varaible from the rest of the data.
        x = self.data.drop([dependentVariable], axis=1)

        # The dependent variable.
        y = self.data[dependentVariable]
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


    def ScaleData(self, columns, method="zscore"):
        """
        Scale data.

        There seems to be a bug in the "StandardScaler," it is recommened to use the "zscore" method.

        Parameters
        ----------
        method : string
            Method used to normalized the data.
            standardscaler : Uses the StandardScaler class.
            zscore : Uses the zscore.

        Returns
        -------
        None.
        """
        if len(self.xTrainingData) == 0:
            raise Exception("Data has not been split.")

        self._ScaleData(self.xTrainingData, columns, method)
        self._ScaleData(self.xTestingData, columns, method)

        if len(self.xValidationData) != 0:
            self._ScaleData(self.xValidationData, columns, method)


    def _ScaleData(self, data, columns, method):
        """
        Scale data.

        Parameters
        ----------
        method : string
            Method used to normalized the data.
            standardscaler : Uses the StandardScaler class.
            zscore : Uses the zscore.

        Returns
        -------
        None.
        """
        scaledData = data[columns].copy(deep=True)

        if method == "standardscaler":
            scaler          = StandardScaler()
            data[columns]   = pd.DataFrame(scaler.fit_transform(scaledData), columns=columns)
        elif method == "zscore":
            data[columns]   = scaledData.apply(zscore)
        else:
            raise Exception("The specified scaling method is invalid.")



    def GetSplitComparisons(self):
        """
        Returns the value counts and percentages of the dependant variable for the
        original, training (if available), and testing (if available) data.

        Returns
        -------
        comparisonFrame : pandas.DataFrame
            DataFrame with the counts and percentages.
        """
        # Get results for original data.
        false = [self.GetCountAndPrecentString(0, "original")]
        true  = [self.GetCountAndPrecentString(1, "original")]
        index = ["Original"]

        # If the data has been split, we will add the split information as well.
        if len(self.xTrainingData) != 0:
            false.append(self.GetCountAndPrecentString(0, "training"))
            true.append(self.GetCountAndPrecentString(1, "training"))
            index.append("Training")

            if len(self.xValidationData) != 0:
                false.append(self.GetCountAndPrecentString(0, "validation"))
                true.append(self.GetCountAndPrecentString(1, "validation"))
                index.append("Validation")

            false.append(self.GetCountAndPrecentString(0, "testing"))
            true.append(self.GetCountAndPrecentString(1, "testing"))
            index.append("Testing")

        # Create the data frame.
        comparisonFrame = pd.DataFrame(
                    {"False" : false,
                     "True"  : true},
                     index=index)

        return comparisonFrame


    def GetCountAndPrecentString(self, classValue, dataSet="original", column=None):
        """
        Gets a string that is the value count of "classValue" and the percentage of the total
        that the "classValue" accounts for in the column.

        Parameters
        ----------
        classValue : int or string
            The value to count and calculate the percentage for.
        dataSet : string
            Which data set(s) to plot.
            original - Gets the results from the original data.
            training - Gets the results from the training data.
            testing  - v the results from the test data.
        column : string, optional
            If provided, that column will be used for the calculations.  If no value is provided,
            the dependant variable is used. The default is None.

        Returns
        -------
        None.
        """
        classValueCount = 0
        totalCount      = 0

        if dataSet == "original":
            if column == None:
                column = self.GetDependentVariableName()
            classValueCount = sum(self.data[column] == classValue)
            totalCount      = self.data[column].size

        elif dataSet == "training":
            classValueCount = sum(self.yTrainingData == classValue)
            totalCount      = self.yTrainingData.size

        elif dataSet == "validation":
            classValueCount = sum(self.yValidationData == classValue)
            totalCount      = self.yValidationData.size

        elif dataSet == "testing":
            classValueCount = sum(self.yTestingData == classValue)
            totalCount      = self.yTestingData.size

        else:
            raise Exception("Invalid data set specified.")

        string = "{0} ({1:0.2f}%)".format(classValueCount, classValueCount/totalCount * 100)
        return string


    def GetDependentVariableName(self):
        """
        Returns the name of the dependent variable (column heading).

        Parameters
        ----------
        None.

        Returns
        -------
        : string
            The name (column heading) of the dependent variable.
        """
        if len(self.yTrainingData) == 0:
            raise Exception("The data has not been split (dependent variable not set).")

        return self.yTrainingData.name