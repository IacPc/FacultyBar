import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import math
import statsmodels.api as sm


def build_dataframe(csv_data):
    vector_column = csv_data[["run", "name", "vecvalue"]].dropna()
    vector_column.rename(columns={'name': 'statistic'}, inplace=True)

    repetition_column = csv_data[(csv_data["attrname"] == "repetition")][["run", "attrvalue"]]
    repetition_column.rename(columns={'attrvalue': 'repetition'}, inplace=True)

    final_dataframe = repetition_column.merge(vector_column, left_on="run", right_on="run", validate="one_to_one")
    final_dataframe["repetition"] = pd.to_numeric(final_dataframe["repetition"])

    return final_dataframe


def get_all_vecvalues(dataframe):
    vecvalue_list = []

    for i, row in dataframe.iterrows():
        vecvalue = [float(n) for n in row["vecvalue"].split()]
        vecvalue_list.extend(vecvalue)

    return vecvalue_list


def linear_regression_analysis(x_vector, y_vector):
    numpy_x = np.array(x_vector)
    numpy_y = np.array(y_vector)

    numpy_x = sm.add_constant(numpy_x)  # To add an intercept (offset) in the model
    regression_results = sm.OLS(numpy_y, numpy_x).fit()  # Dependent variable y as first argument

    # Slope, offset, R^2
    return regression_results.params[1], regression_results.params[0], regression_results.rsquared


def compute_qq_plot_points(obs_vector):
    ordered_statistics = sorted(obs_vector)
    theoretical_quantiles = []

    quantile_number = np.arange(1, len(obs_vector) + 1, 1)
    quantile_number = (quantile_number - 0.5)/len(obs_vector)

    theoretical_quantiles = scipy.stats.expon.ppf(quantile_number).tolist()
    slope, offset, rsquared = linear_regression_analysis(theoretical_quantiles, ordered_statistics)

    # Compute the regression line
    regression_x = np.linspace(theoretical_quantiles[0], theoretical_quantiles[-1])
    regression_y = regression_x*slope + offset

    offset_sign = 'x ' if offset < 0 else 'x +'
    regr_equation = r'$y = ' + str(round(slope, 4)) + offset_sign + str(round(offset, 4)) + '$' + '\n' + r'$R^2 = ' + str(round(rsquared, 4)) + '$'

    return theoretical_quantiles, ordered_statistics, regression_x.tolist(), regression_y.tolist(), regr_equation


def compute_sample_mean(obs_vector, confidence_level):
    alpha = 1 - confidence_level
    standard_normal_quantile = scipy.stats.norm.ppf(1 - alpha / 2)
    obs_number = len(obs_vector)

    sample_mean = np.mean(obs_vector, dtype=np.float64)
    sample_std = np.std(obs_vector, ddof=1, dtype=np.float64)
    error = (sample_std / (math.sqrt(obs_number))) * standard_normal_quantile

    return sample_mean, error


def compute_coefficient_of_variation(obs_vector):
    sample_mean = np.mean(obs_vector, dtype=np.float64)
    sample_std = np.std(obs_vector, ddof=1, dtype=np.float64)
    CoV = sample_std / sample_mean

    return CoV


def plot_qq(theor_quant, ordered_stats, regr_x, regr_y, regr_equation):
    figure = plt.figure()
    plot_axes = plt.gca()

    plot_axes.set_xlabel("Exponential quantile", fontsize=12, labelpad=10)
    plot_axes.set_ylabel("Interdeparture time", fontsize=12, labelpad=10, rotation=90)

    # QQ points
    plot_axes.plot(theor_quant, ordered_stats, marker="o", lw=0, color="cornflowerblue")

    # Regression line
    plot_axes.plot(regr_x, regr_y, linestyle="--", linewidth=1, label=regr_equation, color="black")

    plt.legend(loc="upper left")
    plt.draw()
    plt.show(block=True)


'''
The CSV file must contain only the vector values of the interdeparture statistic and 
it must be obtained from a scenario with static parameters, i.e. without iteration variables 
(it must be pre-filtered when exporting from Omnet++).
'''
def main():
    csv_data = pd.read_csv("./InterDepartureTimes.csv", low_memory=False)
    interdeparture_dataframe = build_dataframe(csv_data)
    obs_vector = get_all_vecvalues(interdeparture_dataframe)

    sample_mean, error = compute_sample_mean(obs_vector, confidence_level=0.99)

    print("Coefficient of variation: " + str(compute_coefficient_of_variation(obs_vector)))
    print("Sample mean: " + str(sample_mean) + "\n" + "Error: " + str(error))

    theor_quant, ordered_stats, regr_x, regr_y, regr_equation = compute_qq_plot_points(obs_vector)

    plot_qq(theor_quant, ordered_stats, regr_x, regr_y, regr_equation)



if __name__ == "__main__":
    main()




