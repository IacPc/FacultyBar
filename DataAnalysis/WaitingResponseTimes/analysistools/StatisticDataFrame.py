from collections import Counter
import statsmodels.api as sm
import pandas as pd
import numpy as np
import scipy.stats
import math


class StatisticDataFrame:
    def __init__(self, file_name):
        csv_data = pd.read_csv(file_name, low_memory=False)
        self.statistic_dataframe = self.__build_dataframe(csv_data)

    '''
    Given an Omnet++ exported CSV file, it returns a dataframe in a suitable format for data analysis.
    The dataframe has columns: ['run' 'cashiervalue' 'repetition' 'statistic' 'vecvalue']
    '''
    def __build_dataframe(self, csv_data):
        cashier_column = csv_data[csv_data["attrname"] == "CASH"][["run", "attrvalue"]]
        cashier_column.rename(columns={'attrvalue': 'cashiervalue'}, inplace=True)

        vector_column = csv_data[["run", "name", "vecvalue"]].dropna()
        vector_column.rename(columns={'name': 'statistic'}, inplace=True)

        repetition_column = csv_data[(csv_data["attrname"] == "repetition")][["run", "attrvalue"]]
        repetition_column.rename(columns={'attrvalue': 'repetition'}, inplace=True)

        final_dataframe = cashier_column.merge(repetition_column, left_on="run", right_on="run", validate="one_to_one")
        final_dataframe = final_dataframe.merge(vector_column, left_on="run", right_on="run", validate="one_to_many")
        final_dataframe["repetition"] = pd.to_numeric(final_dataframe["repetition"])

        return final_dataframe

    '''
    Returns the dataframe rows associated to the specified vector statistic.
    The rows are sorted first by cashier value and then by repetition number, both in ascending order. 
    '''
    def __get_single_statistic_dataframe(self, statistic_name):
        statistic_name = statistic_name + ":vector"
        single_statistic_dataframe = self.statistic_dataframe[self.statistic_dataframe["statistic"] == statistic_name]
        single_statistic_dataframe = single_statistic_dataframe.sort_values(by=["cashiervalue", "repetition"], ascending=[True, True])

        return single_statistic_dataframe

    ''' 
    Each element of the "vecvalue" column of the dataframe is a string of values separated by a whitespace.
    Given a dataframe, the method returns a list of converted "vecvalue" elements.
    If sort_values is True, each vecvalue is sorted in ascending order. 
    '''
    def __get_list_of_converted_vecvalues(self, dataframe, sort_values):
        veclist = []
        for i, row in dataframe.iterrows():
            vecvalue = [float(n) for n in row["vecvalue"].split()]
            if sort_values:
                vecvalue.sort()
            veclist.append(vecvalue)

        return veclist

    ''' 
    Each element of the "vecvalue" column of the dataframe is a string of values separated by a whitespace.
    Given a dataframe, the method combines all the elements contained in the "vecvalue" column in a single list
    of elements, which is returned.
    If sort_values is True, the list is sorted in ascending order.
    '''
    def __get_all_vecvalues_obervations(self, dataframe, sort_values):
        veclist = []
        for i, row in dataframe.iterrows():
            vecvalue = [float(n) for n in row["vecvalue"].split()]
            veclist.extend(vecvalue)

        if sort_values:
            veclist.sort()
        return veclist

    '''
    Given a list of vectors, returns a copy of the list where each vector is truncated and contains the
    same number of values. The size of the final vectors is determined as the minimum between:
    1) the minimum size across all the vectors;
    2) the given max size.
    '''
    def __balance_observations(self, vector_list, max_observations=None):
        min_observation_recorded = min([len(v) for v in vector_list])

        if max_observations is not None:
            balance_level = min(min_observation_recorded, max_observations)
        else:
            balance_level = min_observation_recorded

        balanced_vector_list = []
        for vector in vector_list:
            balanced_vector_list.append(vector[:balance_level])

        return balanced_vector_list

    '''
    Given a list of vectors of the same size, computes a vector of sample means and associated confidence intervals.
    Each sample mean is computed between values in the same position across the vectors (sample mean of each column of
    the matrix of repetitions).
    Each confidence interval is expressed with the following convention (ready to be plotted with matplotlib):
    given the confidence interval CI = [X - error, X + error], the returned value is "error".
    '''
    def __compute_mean_across_repetitions(self, repetition_veclist, confidence_level):
        numpy_repetition_list = np.array(repetition_veclist)

        # Parameters useful to compute confidence intervals
        number_repetitions = numpy_repetition_list.shape[0]
        alpha = 1-confidence_level
        standard_normal_quantile = scipy.stats.norm.ppf(1-alpha/2)

        mean_vector = np.mean(numpy_repetition_list, axis=0, dtype=np.float64)
        std_vector = np.std(numpy_repetition_list, axis=0, ddof=1, dtype=np.float64)
        error_bar = (std_vector/(math.sqrt(number_repetitions)))*standard_normal_quantile

        return mean_vector.tolist(), error_bar.tolist()

    '''
    Given a single list of observations, the method computes and returns the lists containing
    the x values, y values and confidence intervals for an ECDF plot.
    Each confidence interval is expressed with the following convention (ready to be plotted with matplotlib):
    given the confidence interval CI = [X - error, X + error], the returned value is "error".
    '''
    def __compute_ECDF_points(self, obs_vector, error_vector):
        num_observations = len(obs_vector)
        step_height = 1/num_observations
        ECDF_x_vector, ECDF_y_vector, ECDF_error_bar = [], [], []

        observation_classified = [(obs, count) for obs, count in Counter(obs_vector).items()]
        observation_classified.sort(key=lambda tup: tup[0])  # To be sure of the ascending order

        if error_vector is None:
            for obs_tuple in observation_classified:
                ECDF_x_vector.append(obs_tuple[0])
                ECDF_y_vector.append(obs_tuple[1] * step_height)

            ECDF_error_bar = None
        else:
            for obs_tuple in observation_classified:
                duplicate_indexes = [i for i, x in enumerate(obs_vector) if x == obs_tuple[0]]
                ECDF_x_vector.append(obs_tuple[0])
                ECDF_y_vector.append(obs_tuple[1]*step_height)
                ECDF_error_bar.append(max([error_vector[i] for i in duplicate_indexes]))

        ECDF_y_vector = (np.cumsum(ECDF_y_vector)).tolist()
        ECDF_y_vector[-1] = 1  # Remove numerical errors

        return ECDF_x_vector, ECDF_y_vector, ECDF_error_bar

    '''
    Given a single list of observations, the method computes and returns the lists containing
    the x values and y values for a Lorenz curve plot.
    '''
    def __compute_Lorenz_points(self, obs_vector):
        num_observations = len(obs_vector)

        Lorenz_x_vector = ((np.arange(1, num_observations+1))/num_observations).tolist()
        Lorenz_y_vector = (np.cumsum(obs_vector)/np.sum(obs_vector)).tolist()

        # Insert starting point (0,0)
        Lorenz_x_vector.insert(0, 0)  # Index, Value
        Lorenz_y_vector.insert(0, 0)

        return Lorenz_x_vector, Lorenz_y_vector

    '''
    Computes the sample mean of the given list of observations and its confidence interval at the specified level.
    The confidence interval is computed supposing a number of observations higher than 30.
    '''
    def __compute_sample_mean(self, obs_vector, confidence_level):
        alpha = 1-confidence_level
        standard_normal_quantile = scipy.stats.norm.ppf(1-alpha/2)
        obs_number = len(obs_vector)

        if obs_number < 30:
            print("WARNING: the number of observations used to compute the confidence interval for the mean is not high enough")

        sample_mean = np.mean(obs_vector, dtype=np.float64)
        sample_std = np.std(obs_vector, ddof=1, dtype=np.float64)
        error = (sample_std/(math.sqrt(obs_number)))*standard_normal_quantile

        return sample_mean, error

    '''
    Computes the sample median of the given list of observations and its confidence interval at the specified level.
    Returns a tuple (sample_median, lower_error, upper_error), where the errors are in a format suitable for a plot.
    The confidence interval is computed as follows: given the ordered statistics X1, X2, ..., Xn and supposing n > 30,
    the CI is obtained in the form [Xj, Xk] and returned as a couple representing the distances between 
    the sample median and the extremes of the interval.
    '''
    def __compute_sample_median(self, obs_vector, confidence_level):
        alpha = 1 - confidence_level
        standard_normal_quantile = scipy.stats.norm.ppf(1 - alpha/2)
        obs_number = len(obs_vector)
        ordered_statistics = np.sort(obs_vector, axis=None)

        if obs_number < 30:
            print("WARNING: the number of observations used to compute the confidence interval for the median is not high enough")

        CI_lower_obs_number = math.floor(obs_number*0.5 - standard_normal_quantile*math.sqrt(obs_number*0.5*0.5))
        CI_upper_obs_number = math.ceil(obs_number*0.5 + standard_normal_quantile*math.sqrt(obs_number*0.5*0.5)) + 1

        sample_median = np.median(obs_vector)
        # The confidence interval formula gives two indexes in the range 1..N,
        # while the arrays have indexes in the range 0..N-1.
        CI_lower_bound = ordered_statistics[CI_lower_obs_number - 1]
        CI_upper_bound = ordered_statistics[CI_upper_obs_number - 1]

        return sample_median, sample_median-CI_lower_bound, CI_upper_bound-sample_median

    '''
    Computes the coefficient of variation of the given list of observations.
    '''
    def __compute_sample_coefficient_of_variation(self, obs_vector):
        sample_mean = np.mean(obs_vector, dtype=np.float64)
        sample_std = np.std(obs_vector, ddof=1, dtype=np.float64)
        CoV = sample_std/sample_mean

        check_bound = math.sqrt(len(obs_vector)-1)
        if CoV < 0 or CoV > check_bound:
            exit("ERROR: the coefficient of variation is less than 0 or greater than sqrt(n-1)")

        return CoV

    '''
    Executes a linear regression analysis between two list of observations x and y; the model is y = ax + b.
    It returns a tuple (a, b, R^2), where 'a' is the slope of the regression line, 'b' the offset of the latter and
    R^2 is the coefficient of determination.
    '''
    def __linear_regression_analysis(self, x_vector, y_vector):
        numpy_x = np.array(x_vector)
        numpy_y = np.array(y_vector)

        numpy_x = sm.add_constant(numpy_x)  # To add an intercept (offset) in the model
        regression_results = sm.OLS(numpy_y, numpy_x).fit()  # Dependent variable y as first argument

        # Slope, offset, R^2
        return regression_results.params[1], regression_results.params[0], regression_results.rsquared

    '''
    Given a list of observations and the name of a theoretical distribution of reference, the method computes
    the points of a QQ plot and performs a regression analysis to estimate its goodness (as in Excel).
    It returns a tuple (theoretical_quantiles, ordered_statistics, regression_x, regression_y, regr_equation), where:
    1) regression_x and regression_y are the vectors representing the points of the regression line; 
    2) regr_equation is a string containing the mathematical equation of the regression line
       and the obtained coefficient of determination R^2.
    '''
    def __compute_qq_plot_points(self, obs_vector, theoretical_distribution, weibull_shape):
        ordered_statistics = sorted(obs_vector)
        theoretical_quantiles = []

        quantile_number = np.arange(1, len(obs_vector) + 1, 1)
        quantile_number = (quantile_number - 0.5)/len(obs_vector)

        if theoretical_distribution == "normal":
            theoretical_quantiles = scipy.stats.norm.ppf(quantile_number).tolist()
        elif theoretical_distribution == "exponential":
            theoretical_quantiles = scipy.stats.expon.ppf(quantile_number).tolist()
        elif theoretical_distribution == "uniform":
            theoretical_quantiles = scipy.stats.uniform.ppf(quantile_number).tolist()
        elif theoretical_distribution == "weibull":
            theoretical_quantiles = scipy.stats.weibull_min.ppf(quantile_number, weibull_shape).tolist()
        else:
            exit("ERROR: the specified theoretical distribution for the QQ plot is not defined.")

        slope, offset, rsquared = self.__linear_regression_analysis(theoretical_quantiles, ordered_statistics)

        # Compute the regression line
        regression_x = np.linspace(theoretical_quantiles[0], theoretical_quantiles[-1])
        regression_y = regression_x*slope + offset

        offset_sign = 'x ' if offset < 0 else 'x +'
        regr_equation = r'$y = ' + str(round(slope, 4)) + offset_sign + str(round(offset, 4)) + '$' + '\n' + r'$R^2 = ' + str(round(rsquared, 4)) + '$'

        return theoretical_quantiles, ordered_statistics, regression_x.tolist(), regression_y.tolist(), regr_equation


    # PUBLIC INTERFACE

    '''
    Computes the points of an ECDF for a waiting/response time metric (NOT for the occupancy of queues);
    the points are computed for all the statistics in statistic_list, divided by cashier value.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples 
    with the format (cashier_label, x_vector, y_vector, error_vector).
    In particular:
    1) x_vector contains the sample mean of the sorted observations across repetitions.
       After sorting each observation vector in ascending order and calling 
       - n the number of observations per sample;
       - r the number of repetitions.
       Then
                       X11 X12 X13 ... X1n   ||
                       X21 X22 X23 ... X2n   ||   Vertical sample mean
                       ... ... ...     ...   ||
                       Xr1 Xr2 Xr3 ... Xrn   \/
                       ___________________
       [Sample mean]   X'1, X'2, ... , X'n
       
       x_vector is the vector X'1, X'2, ... , X'n;
    2) y_vector contains the points to plot in the vertical axis representing the probability; 
    3) error_vector contains the error bars (confidence intervals) associated to the x values if confidence level is
       not None. If the latter is the case, the error_vector variable is None.
    '''
    def get_ECDF_data(self, statistic_list, cashier_list, confidence_level=None):
        ECDF_data = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]

                if confidence_level is None:
                    obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=True)
                    error_vector = None
                else:
                    repetition_veclist = self.__get_list_of_converted_vecvalues(repetition_by_cashier, sort_values=True)
                    repetition_veclist = self.__balance_observations(repetition_veclist)
                    obs_vector, error_vector = self.__compute_mean_across_repetitions(repetition_veclist, confidence_level)

                ECDF_x_vector, ECDF_y_vector, ECDF_error_bar = self.__compute_ECDF_points(obs_vector, error_vector)
                cashier_label = r'$T_{CASHIER} = ' + cashier_value + '$'
                statistic_data.append((cashier_label, ECDF_x_vector, ECDF_y_vector, ECDF_error_bar))

            ECDF_data[statistic_name] = statistic_data

        return ECDF_data

    '''
    Computes the points of a Lorenz curve for a waiting/response time metric (NOT for the occupancy of queues);
    the points are computed for all the statistics in statistic_list, divided by cashier value.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples
    with the format (cashier_label, x_vector, y_vector).
    In particular:
    1) x_vector contains the steps j/n (n=number of observations) to plot on the x axis; 
    2) y_yector contains the ordinates of the Lorenz curve. The values are obtained starting from a list of 
       all the observations gathered in the different repetitions of the given scenario.
    '''
    def get_Lorenz_Curve_data(self, statistic_list, cashier_list):
        Lorenz_data = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]
                obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=True)
                Lorenz_x_vector, Lorenz_y_vector = self.__compute_Lorenz_points(obs_vector)

                cashier_label = r'$T_{CASHIER} = ' + cashier_value + '$'
                statistic_data.append((cashier_label, Lorenz_x_vector, Lorenz_y_vector))

            Lorenz_data[statistic_name] = statistic_data

        return Lorenz_data

    '''
    Gathers all the observations of a statistic, so that they can be used to plot an histogram.
    Returns a dictionary where each key is the name of a statistic from the given statistic_list
    and each value is a list of tuples with the format (cashier_label, x_vector, number_of_bins).
    In particular:
    1) x_vector contains all the observations (across repetitions) gathered with the associated cashier value; 
    2) number_of_bins is the number of buckets to be used in the histogram plot; it is the same passed as argument.
    '''
    def get_histogram_data(self, statistic_list, cashier_list, number_bins):
        histogram_data = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]
                obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=False)

                cashier_label = r'$T_{CASHIER} = ' + cashier_value + '$'
                statistic_data.append((cashier_label, obs_vector, number_bins))

            histogram_data[statistic_name] = statistic_data

        return histogram_data

    '''
    Computes the sample mean and the relative confidence interval for all 
    the statistics in statistic_list, divided by cashier value.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples 
    with the format (cashier_label, sample_mean, error).
    In particular, the error is such that the confidence interval is [sample_mean-error, sample_mean+error].
    '''
    def get_sample_mean(self, statistic_list, cashier_list, confidence_level):
        sample_mean_dict = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]
                obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=False)

                sample_mean, error = self.__compute_sample_mean(obs_vector, confidence_level)
                cashier_label = r'$T_{CASHIER} = ' + cashier_value + '$'
                statistic_data.append((cashier_label, sample_mean, error))

            sample_mean_dict[statistic_name] = statistic_data

        return sample_mean_dict

    '''
    Computes the sample median for all the statistics in statistic_list, divided by cashier value.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples 
    with the format (cashier_label, sample_median, lower_error, upper_error).
    '''
    def get_sample_median(self, statistic_list, cashier_list, confidence_level):
        median_dict = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]
                obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=False)

                median, lower_error, upper_error = self.__compute_sample_median(obs_vector, confidence_level)
                cashier_label = r'$T_{CASHIER} = ' + cashier_value + '$'
                statistic_data.append((cashier_label, median, lower_error, upper_error))

            median_dict[statistic_name] = statistic_data

        return median_dict

    '''
    Computes the sample coefficient of variation for all the statistics in statistic_list, divided by cashier value.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples 
    with the format (cashier_label, sample CoV).
    '''
    def get_sample_coefficient_of_variation(self, statistic_list, cashier_list):
        CoV_dict = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]
                obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=False)

                CoV = self.__compute_sample_coefficient_of_variation(obs_vector)
                cashier_label = r'$T_{CASHIER} = ' + cashier_value + '$'
                statistic_data.append((cashier_label, CoV))

            CoV_dict[statistic_name] = statistic_data

        return CoV_dict

    '''
    Computes the qq plot points for all the statistics in statistic_list, divided by cashier value.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples 
    with the format (cashier_label, theoretical_quantiles, ordered_statistics, regression_x, regression_y), where: 
    1) regression_x and regression_y are the vectors representing the regression line to plot as reference;
    2) cashier_label is a list of strings specifying as first element the cashier level and as second
        the equation of the regression line with the coefficient of determination R^2.
    '''
    def get_qq_plot_data(self, statistic_list, cashier_list, theoretical_distribution="normal", weibull_shape=None):
        qq_dict = dict()

        for statistic_name in statistic_list:
            repetition_dataframe = self.__get_single_statistic_dataframe(statistic_name)
            statistic_data = []

            for cashier_value in cashier_list:
                repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_value]
                obs_vector = self.__get_all_vecvalues_obervations(repetition_by_cashier, sort_values=False)

                theor_quant, ordered_stats, regr_x, regr_y, regr_equation = self.__compute_qq_plot_points(obs_vector, theoretical_distribution, weibull_shape)

                cashier_label = [r'$T_{CASHIER} = ' + cashier_value + '$', regr_equation]
                statistic_data.append((cashier_label, theor_quant, ordered_stats, regr_x, regr_y))

            qq_dict[statistic_name] = statistic_data

        return qq_dict

    '''
    Convert a list in the corresponding numpy array and saves the latter in an excel file
    '''
    def list_to_excel(self, list_to_convert, file_name="new_excel_file.xlsx"):
        converted_dataframe = pd.DataFrame(np.array(list_to_convert))
        converted_dataframe.to_excel(file_name, index=False)