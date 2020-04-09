from analysistools.StatisticDataFrame import StatisticDataFrame
from analysistools.PlotBuilder import PlotBuilder
from pprint import pprint
from time import time
import configparser as cp
import json


config = cp.ConfigParser()
config.read("settings.ini")


def load_plot_lines(plot_data, statistic_name, statistic_plot):
    color_list = json.loads(config.get("Plot_Profile", "color_list"))
    color_index = 0
    x_error_bar = None

    for statistic_data in plot_data[statistic_name]:
        if len(statistic_data) > 3:
            x_error_bar = statistic_data[3]

        statistic_plot.add_plot_line(statistic_data[0], statistic_data[1], statistic_data[2],
                                     x_error_bar=x_error_bar, color=color_list[color_index])
        color_index = color_index+1


def plot_statistic(statistic_name, plot_data, plot_profile, x_axis_name="", y_axis_name=""):
    plot = PlotBuilder(plot_profile=plot_profile)
    plot.set_axes_label(x_axis_name, y_axis_name)

    load_plot_lines(plot_data=plot_data, statistic_name=statistic_name, statistic_plot=plot)

    if config["General"].getboolean("save_to_file"):
        plot.to_image(directory=config["General"]["export_directory"], file_name=statistic_name + "_" + str(time()), image_format="png")

    if config["General"].getboolean("draw_plots"):
        plot.draw()


def plot_histogram(statistic_name, plot_data, x_axis_name="", y_axis_name=""):
    color_list = json.loads(config.get("Plot_Profile", "color_list"))
    color_index = 0

    for statistic_data in plot_data[statistic_name]:
        plot = PlotBuilder(plot_profile="histogram")
        plot.set_axes_label(x_axis_name, y_axis_name)

        plot.add_plot_line(statistic_data[0], statistic_data[1], num_bins=statistic_data[2], color=color_list[color_index])
        color_index = color_index+1

        if config["General"].getboolean("save_to_file"):
            plot.to_image(directory=config["General"]["export_directory"], file_name=statistic_name + "_" + str(time()), image_format="png")

        if config["General"].getboolean("draw_plots"):
            plot.draw()


def plot_qq(statistic_name, plot_data, x_axis_name="", y_axis_name=""):
    color_list = json.loads(config.get("Plot_Profile", "color_list"))
    color_index = 0

    for statistic_data in plot_data[statistic_name]:
        plot = PlotBuilder(plot_profile="qq")
        plot.set_axes_label(x_axis_name, y_axis_name)

        plot.add_plot_line(statistic_data[0], statistic_data[1], statistic_data[2], regression_x=statistic_data[3], regression_y=statistic_data[4], color=color_list[color_index])
        color_index = color_index+1

        if config["General"].getboolean("save_to_file"):
            plot.to_image(directory=config["General"]["export_directory"], file_name=statistic_name + "_" + str(time()), image_format="png")

        if config["General"].getboolean("draw_plots"):
            plot.draw()


def main():
    cashier_level = json.loads(config.get("Analysis", "cashier_level"))
    statistic_list = json.loads(config.get("Analysis", "statistic_list"))
    confidence_level = config["Analysis"].getfloat("confidence_level")
    dataframe = StatisticDataFrame(config["General"]["working_csv"])

    '''************* DATA ANALYSIS *************'''
    start_time = time()

    #ECDF_data = dataframe.get_ECDF_data(statistic_list, cashier_level, confidence_level)
    #ECDF_no_error = dataframe.get_ECDF_data(statistic_list, cashier_level, confidence_level=None)
    #Lorenz_data = dataframe.get_Lorenz_Curve_data(statistic_list, cashier_level)
    #histogram_data = dataframe.get_histogram_data(statistic_list, cashier_level, number_bins=200)
    #qq_data = dataframe.get_qq_plot_data(statistic_list, cashier_level, theoretical_distribution="weibull", weibull_shape=1.2)
    #sample_mean = dataframe.get_sample_mean(statistic_list, cashier_level, confidence_level)
    #sample_median = dataframe.get_sample_median(statistic_list, cashier_level)
    #sample_CoV = dataframe.get_sample_coefficient_of_variation(statistic_list, cashier_level)

    print("Data analysis completed")
    print("--- %s seconds ---" % (time() - start_time))

    '''************* DATA PLOT *************'''

    #"""
    #pprint(sample_mean)
    #pprint(sample_median)
    #pprint(sample_CoV)
    #"""

    """
    plot_statistic("waitingTimeVipCustomerCashierQueueStatistic", ECDF_data, plot_profile="ecdf", x_axis_name="Waiting time VIP customer [s]", y_axis_name="Probability")
    plot_statistic("responseTimeVipCustomerCashierNodeStatistic", ECDF_data, plot_profile="ecdf", x_axis_name="Response time VIP customer [s]", y_axis_name="Probability")
    plot_statistic("waitingTimeNormalCustomerCashierQueueStatistic", ECDF_data, plot_profile="ecdf", x_axis_name="Waiting time normal customer [s]", y_axis_name="Probability")
    plot_statistic("responseTimeNormalCustomerCashierNodeStatistic", ECDF_data, plot_profile="ecdf", x_axis_name="Response time normal customer [s]", y_axis_name="Probability")
    """

    """
    plot_statistic("waitingTimeVipCustomerCashierQueueStatistic", ECDF_no_error, plot_profile="ecdf", x_axis_name="Waiting time VIP customer [s]", y_axis_name="Probability")
    plot_statistic("responseTimeVipCustomerCashierNodeStatistic", ECDF_no_error, plot_profile="ecdf", x_axis_name="Response time VIP customer [s]", y_axis_name="Probability")
    plot_statistic("waitingTimeNormalCustomerCashierQueueStatistic", ECDF_no_error, plot_profile="ecdf", x_axis_name="Waiting time normal customer [s]", y_axis_name="Probability")
    plot_statistic("responseTimeNormalCustomerCashierNodeStatistic", ECDF_no_error, plot_profile="ecdf", x_axis_name="Response time normal customer [s]", y_axis_name="Probability")
    """

    """
    plot_statistic("waitingTimeVipCustomerCashierQueueStatistic", Lorenz_data, plot_profile="lorenz", x_axis_name="Waiting time VIP customer")
    plot_statistic("responseTimeVipCustomerCashierNodeStatistic", Lorenz_data, plot_profile="lorenz", x_axis_name="Response time VIP customer")
    plot_statistic("waitingTimeNormalCustomerCashierQueueStatistic", Lorenz_data, plot_profile="lorenz", x_axis_name="Waiting time normal customer")
    plot_statistic("responseTimeNormalCustomerCashierNodeStatistic", Lorenz_data, plot_profile="lorenz", x_axis_name="Response time normal customer")
    """

    """
    plot_histogram("waitingTimeVipCustomerCashierQueueStatistic", histogram_data, x_axis_name="Waiting time VIP customer [s]", y_axis_name="Frequency")
    plot_histogram("responseTimeVipCustomerCashierNodeStatistic", histogram_data, x_axis_name="Response time VIP customer [s]", y_axis_name="Frequency")
    plot_histogram("waitingTimeNormalCustomerCashierQueueStatistic", histogram_data, x_axis_name="Waiting time normal customer [s]", y_axis_name="Frequency")
    plot_histogram("responseTimeNormalCustomerCashierNodeStatistic", histogram_data, x_axis_name="Response time normal customer [s]", y_axis_name="Frequency")
    """

    """
    plot_qq("waitingTimeVipCustomerCashierQueueStatistic", qq_data, y_axis_name="Waiting time VIP customer", x_axis_name="Exponential quantiles")
    plot_qq("responseTimeVipCustomerCashierNodeStatistic", qq_data, y_axis_name="Response time VIP customer [s]", x_axis_name="Exponential quantiles")
    plot_qq("waitingTimeNormalCustomerCashierQueueStatistic", qq_data, y_axis_name="Waiting time normal customer [s]", x_axis_name="Exponential quantiles")
    plot_qq("responseTimeNormalCustomerCashierNodeStatistic", qq_data, y_axis_name="Response time normal customer [s]", x_axis_name="Exponential quantiles")
    """

    """
    plot_qq("waitingTimeVipCustomerCashierQueueStatistic", qq_data, y_axis_name="Waiting time VIP customer", x_axis_name="Weibull quantiles")
    plot_qq("responseTimeVipCustomerCashierNodeStatistic", qq_data, y_axis_name="Response time VIP customer [s]", x_axis_name="Weibull quantiles")
    plot_qq("waitingTimeNormalCustomerCashierQueueStatistic", qq_data, y_axis_name="Waiting time normal customer [s]", x_axis_name="Weibull quantiles")
    plot_qq("responseTimeNormalCustomerCashierNodeStatistic", qq_data, y_axis_name="Response time normal customer [s]", x_axis_name="Weibull quantiles")
    """

if __name__ == "__main__":
    main()
