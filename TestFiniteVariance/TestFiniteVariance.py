import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def build_dataframe(csv_data):
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


def get_single_statistic_dataframe(statistic_name, statistic_dataframe):
    statistic_name = statistic_name + ":vector"
    single_statistic_dataframe = statistic_dataframe[statistic_dataframe["statistic"] == statistic_name]
    single_statistic_dataframe = single_statistic_dataframe.sort_values(by=["cashiervalue", "repetition"], ascending=[True, True])

    return single_statistic_dataframe


def get_all_vecvalues_obervations(dataframe, sort_values):
    veclist = []
    for i, row in dataframe.iterrows():
        vecvalue = [float(n) for n in row["vecvalue"].split()]
        veclist.extend(vecvalue)

    if sort_values:
        veclist.sort()

    return veclist


def get_partial_variance(obs_vector):
    n = np.arange(1, len(obs_vector) + 1)
    cumulative_mean = (np.cumsum(obs_vector) / np.arange(1, len(obs_vector) + 1))

    cum_squared_obs = np.cumsum((np.array(obs_vector) * np.array(obs_vector)))
    cum_squared_mean = cumulative_mean * cumulative_mean * n
    cum_double_product = 2 * cumulative_mean * np.cumsum(obs_vector)

    partial_variance = (cum_squared_obs + cum_squared_mean - cum_double_product) / (n - 1)
    partial_variance[0] = 0

    return partial_variance


def plot_partial_variance(partial_variance, label):
    figure = plt.figure()
    plot_axes = plt.gca()

    plot_axes.set_xlabel("Number of observations", fontsize=12, labelpad=10)
    plot_axes.set_ylabel("Partial variance", fontsize=12, labelpad=10, rotation=90)

    x_axis_value = np.arange(1, len(partial_variance) + 1)
    plot_axes.plot(x_axis_value, partial_variance, label=label)
    plt.legend(loc="lower right")
    plt.show(block=True)


def main():
    csv_name = "./ResponseWaiting100d.csv"
    statistic_list = ["waitingTimeVipCustomerCashierQueueStatistic", "responseTimeVipCustomerCashierNodeStatistic",
                      "waitingTimeNormalCustomerCashierQueueStatistic", "responseTimeNormalCustomerCashierNodeStatistic",
                      "numberOfVipCustomersCashierQueueStatistic", "numberOfNormalCustomersCashierQueueStatistic"]
    cashier_level = ["1min", "1.5min", "2min", "2.5min"]
    statistic_name = statistic_list[0]
    cashier_time = cashier_level[0]



    statistic_dataframe = build_dataframe(pd.read_csv(csv_name, low_memory=False))
    repetition_dataframe = get_single_statistic_dataframe(statistic_name, statistic_dataframe)
    repetition_by_cashier = repetition_dataframe[repetition_dataframe["cashiervalue"] == cashier_time]

    obs_vector = get_all_vecvalues_obervations(repetition_by_cashier, sort_values=False)
    pareto_sample = np.random.pareto(1, len(obs_vector))  # For reference, since it has infinite variance

    partial_variance_obs = get_partial_variance(obs_vector)
    partial_variance_pareto = get_partial_variance(pareto_sample)

    plot_partial_variance(partial_variance_obs, statistic_name)
    plot_partial_variance(partial_variance_pareto, "Pareto")


if __name__ == "__main__":
    main()