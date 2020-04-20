from analysistools.StatisticDataFrame import StatisticDataFrame
from analysistools.PlotBuilder import PlotBuilder
from pprint import pprint
from time import time
import numpy as np
import configparser as cp
import json


config = cp.ConfigParser()
config.read("settings.ini")


def plot_data_comparison(plot, plot_data, marker, color_list):
    x_axis_value = [1, 1.5, 2, 2.5]
    label_list = []

    customer_5min_series, customer_7min_series, customer_10min_series = [], [], []
    customer_5min_series_lower_err, customer_7min_series_lower_err, customer_10min_series_lower_err = [], [], []
    customer_5min_series_upper_err, customer_7min_series_upper_err, customer_10min_series_upper_err = [], [], []

    for cashier_time in x_axis_value:
        dict_key = '$T_{CASHIER} = ' + str(cashier_time) + 'min$'
        plot_tuple = plot_data[dict_key]

        label_list.append(plot_tuple[0][0])
        label_list.append(plot_tuple[1][0])
        label_list.append(plot_tuple[2][0])

        customer_5min_series.append(plot_tuple[0][1])
        customer_7min_series.append(plot_tuple[1][1])
        customer_10min_series.append(plot_tuple[2][1])

        customer_5min_series_lower_err.append(plot_tuple[0][2])
        customer_7min_series_lower_err.append(plot_tuple[1][2])
        customer_10min_series_lower_err.append(plot_tuple[2][2])

        customer_5min_series_upper_err.append(plot_tuple[0][3])
        customer_7min_series_upper_err.append(plot_tuple[1][3])
        customer_10min_series_upper_err.append(plot_tuple[1][3])


    plot.add_plot_line(label_list[0], x_axis_value, customer_5min_series,
                       y_error_bar=np.array([customer_5min_series_lower_err, customer_5min_series_upper_err]),
                       marker=marker, color=color_list[0])

    plot.add_plot_line(label_list[1], x_axis_value, customer_7min_series,
                       y_error_bar=np.array([customer_7min_series_lower_err, customer_7min_series_upper_err]),
                       marker=marker, color=color_list[1])

    plot.add_plot_line(label_list[2], x_axis_value, customer_10min_series,
                       y_error_bar=np.array([customer_10min_series_lower_err, customer_10min_series_upper_err]),
                       marker=marker, color=color_list[2])


def plot_histogram(plot_data, x_axis_name="", y_axis_name=""):
    color_list = json.loads(config.get("Plot_Profile", "color_list"))

    for cashier_time in plot_data.keys():
        color_index = 0
        for hist_tuple in plot_data[cashier_time]:
            plot = PlotBuilder(plot_profile="histogram")

            x_axis_full_name = x_axis_name + " (" + cashier_time + ")"
            plot.set_axes_label(x_axis_full_name, y_axis_name)

            plot.add_plot_line(hist_tuple[0], hist_tuple[1], bins=hist_tuple[2], color=color_list[color_index])
            color_index = color_index+1

            if config["General"].getboolean("save_to_file"):
                plot.to_image(directory=config["General"]["export_directory"], file_name=x_axis_name + "_" + str(time()), image_format="png")

            if config["General"].getboolean("draw_plots"):
                plot.draw()


def plot_qq(plot_data, x_axis_name="", y_axis_name=""):
    color_list = json.loads(config.get("Plot_Profile", "color_list"))

    for cashier_time in plot_data.keys():
        color_index = 0
        for qq_tuple in plot_data[cashier_time]:
            plot = PlotBuilder(plot_profile="qq")

            x_axis_full_name = x_axis_name + " (" + cashier_time + ")"
            plot.set_axes_label(x_axis_full_name, y_axis_name)

            plot.add_plot_line(qq_tuple[0], qq_tuple[1], qq_tuple[2], regression_x=qq_tuple[3],
                               regression_y=qq_tuple[4], color=color_list[color_index])
            color_index = color_index+1

            if config["General"].getboolean("save_to_file"):
                plot.to_image(directory=config["General"]["export_directory"], file_name=x_axis_name + "_" + str(time()), image_format="png")

            if config["General"].getboolean("draw_plots"):
                plot.draw()


def main():
    vip_customer_level = json.loads(config.get("Analysis", "vip_level"))
    vip_csv = config["General"]["vip_csv"]
    normal_customer_level = json.loads(config.get("Analysis", "normal_level"))
    normal_csv = config["General"]["normal_csv"]
    cashier_level = json.loads(config.get("Analysis", "cashier_level"))
    confidence_level = config["Analysis"].getfloat("confidence_level")

    dataframe_vip = StatisticDataFrame(vip_csv, vip_enabled=True)
    dataframe_normal = StatisticDataFrame(normal_csv, vip_enabled=False)

    '''************* DATA ANALYSIS *************'''
    start_time = time()

    #sample_mean_vip = dataframe_vip.get_sample_mean(cashier_level, vip_customer_level, confidence_level)
    #sample_IoD_vip = dataframe_vip.get_index_of_dispersion(cashier_level, vip_customer_level)
    sample_quantile_vip = dataframe_vip.get_sample_quantile(cashier_level, vip_customer_level, quantile_number=0.99, confidence_level=confidence_level)
    #histogram_data_vip = dataframe_vip.get_histogram_data(cashier_level, vip_customer_level, bins=np.arange(0, 50))
    #qq_data_vip = dataframe_vip.get_qq_plot_data(cashier_level, vip_customer_level, theoretical_distribution="weibull", discrete_weibull_shape=3)

    #sample_mean_normal = dataframe_normal.get_sample_mean(cashier_level, normal_customer_level, confidence_level)
    #sample_IoD_normal = dataframe_normal.get_index_of_dispersion(cashier_level, normal_customer_level)
    sample_quantile_normal = dataframe_normal.get_sample_quantile(cashier_level, normal_customer_level, quantile_number=0.95, confidence_level=confidence_level)
    #histogram_data_normal = dataframe_normal.get_histogram_data(cashier_level, normal_customer_level,np.arange(0, 50))
    #qq_data_normal = dataframe_normal.get_qq_plot_data(cashier_level, normal_customer_level, theoretical_distribution="weibull", discrete_weibull_shape=3)

    print("Data analysis completed")
    print("--- %s seconds ---" % (time() - start_time))

    '''************* DATA PLOT *************'''

    #pprint(sample_mean_vip)
    #pprint(sample_mean_normal)
    #pprint(sample_IoD_vip)
    #pprint(sample_IoD_normal)
    pprint(sample_quantile_vip)
    pprint(sample_quantile_normal)

    """
    plot_vip = PlotBuilder(plot_profile="comparison")
    plot_vip.set_axes_label('$T_{CASHIER} [min]$', r'$N^{VIP}_{q,CASHIER}$')
    plot_data_comparison(plot_vip, sample_quantile_vip, marker='^', color_list=["crimson", "darkorange", "cornflowerblue"])
    plot_data_comparison(plot_vip, sample_quantile_normal, marker='s', color_list=["lightgrey", "lightgrey", "lightgrey"])
    plot_vip.to_image(directory=config["General"]["export_directory"], file_name="Queue VIP" + "_" + str(time()), image_format="png")
    """

    """
    plot_normal = PlotBuilder(plot_profile="comparison")
    plot_normal.set_axes_label('$T_{CASHIER} [min]$', r'$N^{NORMAL}_{q,CASHIER}$')
    plot_data_comparison(plot_normal, sample_quantile_vip, marker='^', color_list=["lightgrey", "lightgrey", "lightgrey"])
    plot_data_comparison(plot_normal, sample_quantile_normal, marker='s', color_list=["crimson", "darkorange", "cornflowerblue"])
    plot_normal.to_image(directory=config["General"]["export_directory"], file_name="Queue normal" + "_" + str(time()), image_format="png")
    """

    #plot_histogram(histogram_data_vip, x_axis_name=r'$N^{VIP}_{q,CASHIER}$', y_axis_name="Frequency")
    #plot_histogram(histogram_data_normal, x_axis_name=r'$N^{NORMAL}_{q,CASHIER}$', y_axis_name="Frequency")

    #plot_qq(qq_data_vip, y_axis_name="Number of VIP customers", x_axis_name="Theoretical quantiles")
    #plot_qq(qq_data_normal, y_axis_name="Number of normal customers", x_axis_name="Theoretical quantiles")


if __name__ == "__main__":
    main()
