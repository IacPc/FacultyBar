import statsmodels.api as sm
import configparser as cp
import pandas as pd
import numpy as np
import scipy.stats
import math


class StatisticDataFrame:
    def __init__(self, file_name, vip_enabled):
        self.config = cp.ConfigParser()
        self.config.read("settings.ini")

        if vip_enabled:
            self.customer_category = "VOP"
        else:
            self.customer_category = "NOP"

        csv_data = pd.read_csv(file_name, low_memory=False)
        self.statistic_dataframe = self.__build_dataframe(csv_data)

    '''
    Given an Omnet++ exported CSV file, it returns a dataframe in a suitable format for data analysis.
    The dataframe has columns: ['run' 'cashiervalue' 'customervalue' 'repetition' 'statistic' 'vecvalue' 'vectime']
    '''
    def __build_dataframe(self, csv_data):
        cashier_column = csv_data[csv_data["attrname"] == "CASH"][["run", "attrvalue"]]
        cashier_column.rename(columns={'attrvalue': 'cashiervalue'}, inplace=True)

        customer_column = csv_data[csv_data["attrname"] == self.customer_category][["run", "attrvalue"]]
        customer_column.rename(columns={'attrvalue': 'customervalue'}, inplace=True)

        vector_column = csv_data[["run", "name", "vecvalue", "vectime"]].dropna()
        vector_column.rename(columns={'name': 'statistic'}, inplace=True)

        repetition_column = csv_data[(csv_data["attrname"] == "repetition")][["run", "attrvalue"]]
        repetition_column.rename(columns={'attrvalue': 'repetition'}, inplace=True)

        final_dataframe = cashier_column.merge(customer_column, left_on="run", right_on="run", validate="one_to_one")
        final_dataframe = final_dataframe.merge(repetition_column, left_on="run", right_on="run", validate="one_to_one")
        final_dataframe = final_dataframe.merge(vector_column, left_on="run", right_on="run", validate="one_to_one")
        final_dataframe["repetition"] = pd.to_numeric(final_dataframe["repetition"])

        return final_dataframe

    '''
    Returns the dataframe rows associated to the specified combination of cashier service time and customer arrival time.
    The rows are sorted by repetition number in ascending order. 
    '''
    def __get_single_scenario_dataframe(self, cashier_time, customer_time):
        single_scenario_dataframe = self.statistic_dataframe[(self.statistic_dataframe["cashiervalue"] == cashier_time) & (self.statistic_dataframe["customervalue"] == customer_time)]
        single_scenario_dataframe = single_scenario_dataframe.sort_values(by=["repetition"], ascending=True)

        return single_scenario_dataframe

    ''' 
    Each element of the "vecvalue" or "vectime" column of the dataframe is a string of values separated by a whitespace.
    Given a dataframe, the method returns a list of converted "vecvalue" or "vectime" elements.
    If sort_values is True, each list is sorted in ascending order. 
    '''
    def __get_list_of_converted_vecvalues(self, dataframe, vectime=False, sort_values=False):
        veclist = []
        column_name = "vectime" if vectime else "vecvalue"

        for i, row in dataframe.iterrows():
            vecvalue = [float(n) for n in row[column_name].split()]
            if sort_values:
                vecvalue.sort()
            veclist.append(vecvalue)

        return veclist

    ''' 
    Each element of the "vecvalue" or "vectime" column of the dataframe is a string of values separated by a whitespace.
    Given a dataframe, the method combines all the elements contained in the "vecvalue" or "vectime" column in a single 
    lists of elements, which is returned.
    If sort_values is True, the list is sorted in ascending order.
    '''
    def __get_all_vecvalues_obervations(self, dataframe, vectime=False, sort_values=False):
        veclist = []
        column_name = "vectime" if vectime else "vecvalue"

        for i, row in dataframe.iterrows():
            vecvalue = [float(n) for n in row[column_name].split()]
            veclist.extend(vecvalue)

        if sort_values:
            veclist.sort()

        return veclist

    '''
    Given a list of vecvalues and vectimes across repetitions, the method computes the time average of 
    the queue occupancy for each repetition and returns them in the form of a list. 
    '''
    def __compute_time_average(self, obs_vector_list, obs_time_vector_list):
        time_average_list = []

        for repetition_index, obs_vector in enumerate(obs_vector_list):
            obs_time_vector = obs_time_vector_list[repetition_index]

            weight_vector = np.array(obs_time_vector[1:len(obs_time_vector)]) - np.array(obs_time_vector[:-1])
            time_average = np.sum((np.array(obs_vector[:-1])*weight_vector))/(obs_time_vector[-1]-obs_time_vector[0])

            time_average_list.append(time_average)

        return time_average_list

    '''
    Computes the sample quantile of the given list of observations and its confidence interval at the specified level.
    Returns a tuple (sample_quantile, lower_error, upper_error), where the errors are in a format suitable for a plot.
    The confidence interval is computed as follows: given the ordered statistics X1, X2, ..., Xn and supposing n > 30,
    the CI is obtained in the form [Xj, Xk] and returned as a couple representing the distances between 
    the sample quantile and the extremes of the interval.
    '''
    def __compute_sample_quantile(self, obs_vector, quantile_number, confidence_level):
        alpha = 1 - confidence_level
        standard_normal_quantile = scipy.stats.norm.ppf(1 - alpha/2)
        obs_number = len(obs_vector)
        ordered_statistics = np.sort(obs_vector, axis=None)

        if obs_number < 30:
            print("WARNING: the number of observations used to compute the confidence interval for the quantile is not high enough")

        CI_lower_obs_number = math.floor(obs_number*quantile_number - standard_normal_quantile*math.sqrt(obs_number*quantile_number*(1-quantile_number)))
        CI_upper_obs_number = math.ceil(obs_number*quantile_number + standard_normal_quantile*math.sqrt(obs_number*quantile_number*(1-quantile_number))) + 1

        sample_quantile = np.quantile(obs_vector, quantile_number)
        CI_lower_bound = ordered_statistics[CI_lower_obs_number + 1]
        CI_upper_bound = ordered_statistics[CI_upper_obs_number + 1]

        return sample_quantile, sample_quantile-CI_lower_bound, CI_upper_bound-sample_quantile

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
    def __compute_qq_plot_points(self, obs_vector, theoretical_distribution, poisson_mean, binomial_n, binomial_p,
                                 geometric_prob, discrete_weibull_shape):
        ordered_statistics = sorted(obs_vector)
        theoretical_quantiles = []

        quantile_number = np.arange(1, len(obs_vector) + 1, 1)
        quantile_number = (quantile_number - 0.5)/len(obs_vector)

        if theoretical_distribution == "poisson":
            theoretical_quantiles = scipy.stats.poisson.ppf(quantile_number, poisson_mean).tolist()
        elif theoretical_distribution == "binomial":
            theoretical_quantiles = scipy.stats.binom.ppf(quantile_number, binomial_n, binomial_p).tolist()
        elif theoretical_distribution == "geometric":
            theoretical_quantiles = scipy.stats.geom.ppf(quantile_number, geometric_prob).tolist()
        elif theoretical_distribution == "weibull":
            theoretical_quantiles = np.floor(scipy.stats.weibull_min.ppf(quantile_number, discrete_weibull_shape)).tolist()
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
    Computes the sample mean and the relative confidence interval for the number of customers in the queue 
    for each combination of cashier service time and customer interarrival time_list.
    It returns a dictionary where each key represents a cashier level and each value is a list of tuples 
    with the format (customer_label, sample_mean, error, error); the error (replicated twice to help plotting)
    is such that the confidence interval is [sample_mean-error, sample_mean+error].
    The sample mean is obtained as the mean across repetitions of the time average occupancy.
    '''
    def get_sample_mean(self, cashier_level, customer_level, confidence_level):
        sample_mean_dict = dict()

        for cashier_time in cashier_level:
            mean_data = []

            for customer_time in customer_level:
                repetition_dataframe = self.__get_single_scenario_dataframe(cashier_time, customer_time)

                obs_vector_list = self.__get_list_of_converted_vecvalues(repetition_dataframe)
                obs_time_vector_list = self.__get_list_of_converted_vecvalues(repetition_dataframe, vectime=True)
                time_average_list = self.__compute_time_average(obs_vector_list, obs_time_vector_list)

                # Parameters useful to compute confidence intervals
                number_repetitions = len(time_average_list)
                alpha = 1 - confidence_level
                standard_normal_quantile = scipy.stats.norm.ppf(1 - alpha / 2)

                mean = np.mean(np.array(time_average_list), dtype=np.float64)
                std = np.std(np.array(time_average_list), ddof=1, dtype=np.float64)
                error = (std / (math.sqrt(number_repetitions))) * standard_normal_quantile

                customer_category = "VIP" if self.customer_category == "VOP" else "NORMAL"
                customer_label = r'$T_{' + customer_category + '} = ' + customer_time + '$'
                mean_data.append((customer_label, mean, error, error))

            cashier_label = r'$T_{CASHIER} = ' + cashier_time + '$'
            sample_mean_dict[cashier_label] = mean_data

        return sample_mean_dict

    '''
    Computes the sample index of dispersion for the number of customers in the queue.
    It returns a dictionary where each key represents a cashier level and each value is a list of tuples 
    with the format (customer_label, sample_IoD).
    The sample mean used in the IoD formula is obtained as the mean across repetitions of the time average occupancy.
    '''
    def get_index_of_dispersion(self, cashier_level, customer_level):
        IoD_dict = dict()

        for cashier_time in cashier_level:
            IoD_data = []

            for customer_time in customer_level:
                repetition_dataframe = self.__get_single_scenario_dataframe(cashier_time, customer_time)

                obs_vector_flat = self.__get_all_vecvalues_obervations(repetition_dataframe)
                obs_vector_list = self.__get_list_of_converted_vecvalues(repetition_dataframe)
                obs_time_vector_list = self.__get_list_of_converted_vecvalues(repetition_dataframe, vectime=True)
                time_average_list = self.__compute_time_average(obs_vector_list, obs_time_vector_list)

                sample_mean = np.mean(np.array(time_average_list), dtype=np.float64)
                sample_variance = np.var(obs_vector_flat, ddof=1, dtype=np.float64)
                sample_IoD = sample_variance/sample_mean

                customer_category = "VIP" if self.customer_category == "VOP" else "NORMAL"
                customer_label = r'$T_{' + customer_category + '} = ' + customer_time + '$'
                IoD_data.append((customer_label, sample_IoD))

            cashier_label = r'$T_{CASHIER} = ' + cashier_time + '$'
            IoD_dict[cashier_label] = IoD_data

        return IoD_dict

    '''
    Computes the sample quantile and the relative confidence interval for each combination of cashier service time 
    and customer interarrival time_list.
    Returns a dictionary where each key is the name of a statistic and each value is a list of tuples 
    with the format (cashier_label, sample_quantile, lower_error, upper_error).
    '''
    def get_sample_quantile(self, cashier_level, customer_level, quantile_number, confidence_level):
        quantile_dict = dict()

        for cashier_time in cashier_level:
            quantile_data = []

            for customer_time in customer_level:
                repetition_dataframe = self.__get_single_scenario_dataframe(cashier_time, customer_time)

                obs_vector = self.__get_all_vecvalues_obervations(repetition_dataframe)
                quantile, lower_error, upper_error = self.__compute_sample_quantile(obs_vector, quantile_number, confidence_level)

                customer_category = "VIP" if self.customer_category == "VOP" else "NORMAL"
                customer_label = r'$T_{' + customer_category + '} = ' + customer_time + '$'
                quantile_data.append((customer_label, quantile, lower_error, upper_error))

            cashier_label = r'$T_{CASHIER} = ' + cashier_time + '$'
            quantile_dict[cashier_label] = quantile_data

        return quantile_dict

    '''
    Gathers all the information needed to plot an histogram for each combination of cashier service time and customer
    interarrival time: it returns a dictionary where each key represents a cashier level and 
    each value is a list of tuples with the format (customer_label, x_vector, number_of_bins).
    In particular:
    1) x_vector contains all the observations (across repetitions) gathered with the associated customer time; 
    2) number_of_bins is the number of buckets to be used in the histogram plot; it is the same passed as argument.
    '''
    def get_histogram_data(self, cashier_level, customer_level, number_bins):
        histogram_dict = dict()

        for cashier_time in cashier_level:
            hist_data = []

            for customer_time in customer_level:
                repetition_dataframe = self.__get_single_scenario_dataframe(cashier_time, customer_time)
                obs_vector = self.__get_all_vecvalues_obervations(repetition_dataframe)

                customer_category = "VIP" if self.customer_category == "VOP" else "NORMAL"
                customer_label = r'$T_{' + customer_category + '} = ' + customer_time + '$'
                hist_data.append((customer_label, obs_vector, number_bins))

            cashier_label = r'$T_{CASHIER} = ' + cashier_time + '$'
            histogram_dict[cashier_label] = hist_data

        return histogram_dict

    '''
    Computes the qq plot points for the number of customers in the queue, divided by cashier service time and 
    customer interarrival time.
    Returns a dictionary where each key represents a cashier level and each value is a list of tuples 
    with the format (customer_label, theoretical_quantiles, ordered_statistics, regression_x, regression_y), where: 
    1) regression_x and regression_y are the vectors representing the regression line to plot as reference;
    2) customer_label is a list of strings specifying as first element the customer level and as second
        the equation of the regression line with the coefficient of determination R^2.
    '''
    def get_qq_plot_data(self, cashier_level, customer_level, theoretical_distribution="geometric", poisson_mean=None,
                         binomial_n=None, binomial_p=None, geometric_prob=None, discrete_weibull_shape=None):
        qq_dict = dict()

        for cashier_time in cashier_level:
            qq_data = []

            for customer_time in customer_level:
                repetition_dataframe = self.__get_single_scenario_dataframe(cashier_time, customer_time)
                obs_vector = self.__get_all_vecvalues_obervations(repetition_dataframe)

                theor_quant, ordered_stats, regr_x, regr_y, regr_equation = self.__compute_qq_plot_points(obs_vector, theoretical_distribution, poisson_mean, binomial_n,
                                                                                                          binomial_p, geometric_prob, discrete_weibull_shape)

                customer_category = "VIP" if self.customer_category == "VOP" else "NORMAL"
                customer_label = [r'$T_{' + customer_category + '} = ' + customer_time + '$', regr_equation]
                qq_data.append((customer_label, theor_quant, ordered_stats, regr_x, regr_y))
                break

            cashier_label = r'$T_{CASHIER} = ' + cashier_time + '$'
            qq_dict[cashier_label] = qq_data

        return qq_dict

    '''
    Convert a list in the corresponding numpy array and saves the latter in an excel file
    '''
    def list_to_excel(self, list_to_convert, file_name="new_excel_file.xlsx"):
        converted_dataframe = pd.DataFrame(np.array(list_to_convert))
        converted_dataframe.to_excel(file_name, index=False)
