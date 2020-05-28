import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def build_dataframe(csv_data):
    vector_column = csv_data[["run", "name", "vecvalue", "vectime"]].dropna()
    vector_column.rename(columns={'name': 'statistic'}, inplace=True)

    repetition_column = csv_data[(csv_data["attrname"] == "repetition")][["run", "attrvalue"]]
    repetition_column.rename(columns={'attrvalue': 'repetition'}, inplace=True)

    final_dataframe = repetition_column.merge(vector_column, left_on="run", right_on="run", validate="one_to_one")
    final_dataframe["repetition"] = pd.to_numeric(final_dataframe["repetition"])

    return final_dataframe


def convert_vecvalues(dataframe):
    vecvalue_list, vectime_list = [], []

    for i, row in dataframe.iterrows():
        vecvalue = [float(n) for n in row["vecvalue"].split()]
        vectime = [float(n) for n in row["vectime"].split()]
        vecvalue_list.append(vecvalue)
        vectime_list.append(vectime)

    return vecvalue_list, vectime_list


def get_sampling_times(vectime_list):
    sampling_time = [0]

    for vectime in vectime_list:
        sampling_time.extend(vectime)

    sampling_time = (np.unique(sampling_time)).tolist()

    return sampling_time


def get_throughput_at_each_sample_time(vecvalue_list, vectime_list, sampling_time):
    throughput_per_run = []

    for run_index, vectime in enumerate(vectime_list):
        complete_vecvalue = np.zeros(shape=len(sampling_time))
        intersect1d, comm1, comm2 = np.intersect1d(vectime, sampling_time, assume_unique=True, return_indices=True)

        for comm1_index, comm2_index in enumerate(comm2):
            complete_vecvalue[comm2_index:-1] = vecvalue_list[run_index][comm1_index]

        complete_vecvalue[-1] = vecvalue_list[run_index][-1]

        throughput_per_run.append(complete_vecvalue)
        print("Computed throughput of run: " + str(run_index+1) + "/" + str(len(vectime_list)))

    return throughput_per_run


def plot_throughput(sampling_time, vectime_list, vecvalue_list, mean_throughput):
    figure = plt.figure(figsize=(13.66, 7.68))
    plot_axes = plt.gca()

    plot_axes.set_xlabel("Simulation time [s]", fontsize=14, labelpad=10)
    plot_axes.set_ylabel("Throughput " + r'$[\mathrm{\frac{customer}{s}}]$', fontsize=14, labelpad=10, rotation=90)

    plot_axes.set_xlim([0, 80000])
    plot_axes.set_ylim([0, 0.01])

    for i in range(len(vecvalue_list)):
        plot_axes.plot(vectime_list[i], vecvalue_list[i], marker="", lw=2)

    plot_axes.plot(sampling_time, mean_throughput, label="Mean", marker="", lw=2, color="black")

    plt.legend(loc="upper right", prop={'size': 14})
    plt.savefig("Throughput.png", format="png", dpi=300, bbox_inches='tight')
    plt.draw()
    plt.show(block=True)


'''
The CSV file must contain only the vector values of the throughput statistic and 
it must be obtained from a scenario with static parameters, i.e. without iteration variables 
(it must be pre-filtered when exporting from Omnet++).
'''
def main():
    csv_data = pd.read_csv("./Throughput.csv", low_memory=False)
    throughput_dataframe = build_dataframe(csv_data)
    vecvalue_list, vectime_list = convert_vecvalues(throughput_dataframe)

    sampling_time = get_sampling_times(vectime_list)
    throughput_per_run = get_throughput_at_each_sample_time(vecvalue_list, vectime_list, sampling_time)
    mean_throughput = np.mean(np.array(throughput_per_run), axis=0, dtype=np.float64)

    plot_throughput(sampling_time, vectime_list, vecvalue_list, mean_throughput)



if __name__ == "__main__":
    main()




