from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker
import configparser as cp
import numpy as np
import json
import mpmath as math
import matplotlib.pyplot as plt
import texttable as tt


def convert_min_to_sec(value): return value * 60


def load_parameters():
    config = cp.ConfigParser()
    config.read("settings.ini")

    vip_arrival_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("vip_interarrival_time"))
    normal_arrival_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("normal_interarrival_time"))
    eating_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("eating_time"))
    number_of_seats = json.loads(config.get("SeatingNode", "number_of_seats"))
    data_length = json.loads(config.get("SeatingNode", "data_length"))
    u = (vip_arrival_rate + normal_arrival_rate) / eating_rate  # scalar
    utilization = np.full(fill_value=u, shape=data_length) / number_of_seats  # utilization but in list form

    return u, utilization, number_of_seats, data_length


def compute_formula_second_term(utilization, node_capacity, n_seats, u):
    u_to_c_over_c_fact = math.fdiv(math.power(u, n_seats), math.factorial(n_seats))
    p_to_K_minus_C_plus1 = math.power(utilization, (node_capacity - n_seats + 1))
    one_minus_p = math.fsub(1, utilization)
    second_fraction_numerator = math.fsub(1, p_to_K_minus_C_plus1)
    second_fraction = math.fdiv(second_fraction_numerator, one_minus_p)
    return math.fmul(u_to_c_over_c_fact, second_fraction)


def compute_p0(u, utilization, node_capacity, number_of_seats):
    factorial_sum = []
    for n_seats in number_of_seats:
        temp_sum = math.mpf(0.0)  # type= real with arbitrary precision
        for j in range(0, n_seats):
            temp_sum = math.fadd(temp_sum, math.fdiv(math.power(u, j), math.factorial(j)))
        factorial_sum.append(temp_sum)

    second_term = []
    for index, n_seats in enumerate(number_of_seats):
        work = compute_formula_second_term(utilization[index], node_capacity[index], n_seats, u)
        second_term.append(work)

    p0 = []
    oneExtended = math.mpf(1.0)
    for i in range(0, len(factorial_sum)):
        temp_real = math.fadd(factorial_sum[i], second_term[i])
        p0.append(math.fdiv(oneExtended, temp_real))
    return p0


def compute_single_item_loss_list(u, node_capacity, n_seats, p0):
    u_to_the_n = math.power(u, node_capacity)
    C_fact = math.factorial(n_seats)
    C_to_the_n_minus_c = math.power(n_seats, (node_capacity - n_seats))
    denominator = math.fmul(C_fact, C_to_the_n_minus_c)
    fraction = math.fdiv(u_to_the_n, denominator)
    return math.fmul(fraction, p0)


def compute_loss_probability(u, utilization, node_capacity, number_of_seats):
    p0 = compute_p0(u, utilization, node_capacity, number_of_seats)

    loss_probability = []
    for index, n_seats in enumerate(number_of_seats):
        loss = compute_single_item_loss_list(u, node_capacity[index], n_seats, p0[index])
        loss_probability.append(loss)

    return loss_probability


def plot_loss_probability(loss_probability_No_Queueing, loss_probability_with_queue):
    figure = plt.figure(figsize=(13.66, 7.68))
    plot_axes = plt.gca()
    plot_axes.set_ylabel(r'$p_{LOSS}[\%]$', fontsize=14, labelpad=10, rotation=90)
    plot_axes.set_xlabel(r'Capacity $K$', fontsize=14, labelpad=10)

    x_values = np.arange(start=6, stop=len(loss_probability_No_Queueing)+6, step=1.0)
    loss_probability_no_queuing_percentage = np.array(loss_probability_No_Queueing)*100
    loss_probability_with_queue_percentage = np.array(loss_probability_with_queue)*100

    plot_axes.plot(x_values, loss_probability_no_queuing_percentage, marker="", lw=2, color="cornflowerblue", label="Increasing only " + r'$N_{SEAT}$')
    plot_axes.plot(x_values, loss_probability_with_queue_percentage, marker="", lw=2, color="darkorange", label="Increasing only " + r'$K_{q, SEATING}$')
    plot_axes.plot(np.arange(start=0, stop=50), np.full(fill_value=1, shape=50), marker="", lw=1, linestyle="--", color="black", label=r'$p_{LOSS}=1$%')

    plot_axes.set_xlim([6, 30])
    plot_axes.set_ylim([0, 10])

    plot_axes.xaxis.set_major_locator(ticker.MultipleLocator(base=1))
    plot_axes.yaxis.set_major_locator(ticker.MultipleLocator(base=1))

    plt.margins(0)
    plt.legend(loc="upper right", prop={'size': 14})

    plt.savefig("DimensioningSeatingNode.png", format="png", dpi=300, bbox_inches='tight')
    plt.draw()
    plt.show(block=True)


def main():
    u, utilization, number_of_seats, data_length = load_parameters()
    node_capacity_no_queue = np.arange(start=number_of_seats, stop=number_of_seats + data_length)
    loss_probability_No_Queueing = compute_loss_probability(u, utilization, node_capacity_no_queue, node_capacity_no_queue)

    queue_size_not_null = np.arange(0, data_length)
    number_of_seats_with_queue = np.full(fill_value=number_of_seats, shape=data_length)
    node_capacity_with_queue = np.add(queue_size_not_null, number_of_seats_with_queue)
    loss_probability_with_queue = compute_loss_probability(u, utilization, node_capacity_with_queue, number_of_seats_with_queue)
    plot_loss_probability(loss_probability_No_Queueing, loss_probability_with_queue)
    
    result_table_more_seats = tt.Texttable()
    result_table_more_seats.header(["Node capacity", "Number of seats", "Queue capacity", "Loss probability"])
    result_table_more_seats.set_cols_dtype(["t", "t", "t", "t"])

    for row in zip(node_capacity_no_queue, node_capacity_no_queue, np.full(fill_value=0, shape=len(node_capacity_no_queue)), loss_probability_No_Queueing):
        result_table_more_seats.add_row(row)
    print("************* INCREASING NUMBER OF SEATS *************")
    print(result_table_more_seats.draw())

    result_table_more_queue = tt.Texttable()
    result_table_more_queue.header(["Node capacity", "Number of seats", "Queue capacity", "Loss probability"])
    result_table_more_queue.set_cols_dtype(["t", "t", "t", "t"])
    for row in zip(node_capacity_with_queue, number_of_seats_with_queue, queue_size_not_null, loss_probability_with_queue):
        result_table_more_queue.add_row(row)

    print("************* INCREASING QUEUE LENGTH *************")
    print(result_table_more_queue.draw())


if __name__ == "__main__":
    main()
