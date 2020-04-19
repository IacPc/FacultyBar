import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import configparser as cp
import numpy as np
import json


class PlotBuilder:
    def __init__(self, plot_profile):
        self.config = cp.ConfigParser()
        self.config.read("settings.ini")
        plt.style.use(self.config["Plot_Profile"]["matplotlib_style"])

        self.figure = plt.figure(figsize=(13.66, 7.68))
        self.plot_axes = plt.gca()
        self.plot_profile = json.loads(self.config.get("Plot_Profile", plot_profile))
        plt.margins(0)

        if self.plot_profile["name"] == "LORENZ":
            self.__add_Lorenz_reference_lines()


    def set_axes_label(self, x_axis_name, y_axis_name):
        self.plot_axes.set_xlabel(x_axis_name, fontsize=14, labelpad=10)
        self.plot_axes.set_ylabel(y_axis_name, fontsize=14, labelpad=10, rotation=90)

    def add_plot_line(self, label, x_axis_value, y_axis_value=None, x_error_bar=None, num_bins=None, regression_x=None, regression_y=None, color='r'):
        if self.plot_profile["name"] == "ECDF":
            # Conversion to minutes
            x_axis_value = (np.array(x_axis_value))/60
            x_error_bar = (np.array(x_error_bar))/60

            self.plot_axes.errorbar(x_axis_value, y_axis_value, xerr=x_error_bar,
                                    label=label, color=color, marker=self.plot_profile["marker"],
                                    lw=self.plot_profile["line_width"], elinewidth=self.plot_profile["error_line_width"],
                                    capsize=self.plot_profile["error_capsize"], errorevery=self.plot_profile["errorevery"])

        elif self.plot_profile["name"] == "LORENZ":
            self.plot_axes.plot(x_axis_value, y_axis_value, label=label, color=color,
                                marker=self.plot_profile["marker"], lw=self.plot_profile["line_width"])

        elif self.plot_profile["name"] == "HISTOGRAM":
            self.plot_axes.hist(x_axis_value, bins=num_bins, range=(0, max(x_axis_value)),
                                label=label, color=color, edgecolor=self.plot_profile["edgecolor"],
                                lw=self.plot_profile["line_width"])

        elif self.plot_profile["name"] == "QQ":
            # QQ points
            self.plot_axes.plot(x_axis_value, y_axis_value, marker=self.plot_profile["marker"], lw=0,
                                color=color, label=label[0])
            # Regression line
            self.plot_axes.plot(regression_x, regression_y, linestyle=self.plot_profile["linestyle"],
                                linewidth=self.plot_profile["line_width"],
                                label=label[1], color=self.plot_profile["regression_color"])

    def __add_Lorenz_reference_lines(self):
        # Line of maximum fairness
        self.plot_axes.plot(np.arange(0, 2), np.arange(0, 2), lw=self.plot_profile["line_width"], color="black")

        # Line of maximum unfairness
        self.plot_axes.plot(np.arange(0, 2), np.array([0, 0]), lw=self.plot_profile["line_width"], color="black")
        self.plot_axes.plot(np.array([1, 1]), np.array([0, 1]), lw=self.plot_profile["line_width"], color="black")

    def to_image(self, directory, file_name, image_format):
        plt.legend(loc=self.plot_profile["legend_position"], prop={'size': 14})
        export_name = directory + file_name + "." + image_format
        plt.savefig(export_name, format=image_format, dpi=1200, bbox_inches='tight')

    def draw(self):
        plt.legend(loc=self.plot_profile["legend_position"], prop={'size': 14})
        plt.draw()
        plt.show(block=True)


