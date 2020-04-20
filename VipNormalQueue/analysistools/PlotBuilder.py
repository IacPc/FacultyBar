import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import configparser as cp
import json


class PlotBuilder:
    def __init__(self, plot_profile):
        self.config = cp.ConfigParser()
        self.config.read("settings.ini")
        plt.style.use(self.config["Plot_Profile"]["matplotlib_style"])

        self.figure = plt.figure(figsize=(13.66, 7.68))
        self.plot_axes = plt.gca()
        self.plot_profile = json.loads(self.config.get("Plot_Profile", plot_profile))


    def set_axes_label(self, x_axis_name, y_axis_name):
        self.plot_axes.set_xlabel(x_axis_name, fontsize=12, labelpad=10)
        self.plot_axes.set_ylabel(y_axis_name, fontsize=12, labelpad=10, rotation=90)

    def add_plot_line(self, label, x_axis_value, y_axis_value=None, y_error_bar=None, bins=None, regression_x=None, regression_y=None, color='r', marker=None):
        if self.plot_profile["name"] == "COMPARISON":
            self.plot_axes.errorbar(x_axis_value, y_axis_value, yerr=y_error_bar,
                                    label=label, color=color, marker=marker,
                                    lw=self.plot_profile["line_width"], elinewidth=self.plot_profile["error_line_width"],
                                    capsize=self.plot_profile["error_capsize"], errorevery=self.plot_profile["errorevery"])
            plt.xticks(x_axis_value)

        elif self.plot_profile["name"] == "HISTOGRAM":
            self.plot_axes.hist(x_axis_value, bins=bins, range=(0, max(x_axis_value)),
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

    def to_image(self, directory, file_name, image_format):
        if self.plot_profile["name"] == "COMPARISON":
            self.plot_axes.xaxis.tick_top()
            self.plot_axes.xaxis.set_label_position('top')
            self.plot_axes.set_ylim([0, 35])
            self.plot_axes.yaxis.set_major_locator(ticker.MultipleLocator(3))
            plt.gca().invert_yaxis()
        elif self.plot_profile["name"] == "HISTOGRAM":
            self.plot_axes.set_xlim([0, 25])
            self.plot_axes.xaxis.set_major_locator(ticker.MultipleLocator(1))

        plt.legend(loc=self.plot_profile["legend_position"], prop={'size': 14})
        export_name = directory + file_name + "." + image_format
        plt.savefig(export_name, format=image_format, dpi=1200, bbox_inches='tight')

    def draw(self):
        if self.plot_profile["name"] == "COMPARISON":
            self.plot_axes.xaxis.tick_top()
            self.plot_axes.xaxis.set_label_position('top')
            self.plot_axes.set_ylim([0, 35])
            self.plot_axes.yaxis.set_major_locator(ticker.MultipleLocator(3))
            plt.gca().invert_yaxis()

        plt.legend(loc=self.plot_profile["legend_position"], prop={'size': 14})
        plt.draw()
        plt.show(block=True)


