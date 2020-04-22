import configparser as cp
import numpy as np
import json
import mpmath as math
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter


def convert_min_to_sec(value): return value * 60


def load_parameters():
    config = cp.ConfigParser()
    config.read("settings.ini")

    vip_arrival_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("vip_interarrival_time"))
    normal_arrival_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("normal_interarrival_time"))
    eating_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("eating_time"))
    number_of_seats = json.loads(config.get("SeatingNode", "number_of_seats"))  #min number of seats to have utilization <1
    data_length = json.loads(config.get("SeatingNode", "data_length"))
    u = (vip_arrival_rate + normal_arrival_rate) / eating_rate  # utilization:scalar
    if u/number_of_seats >= 1:
        print("ERROR: utilization greater or equal than 1")
        exit(-1)

    utilization = np.full(fill_value=u, shape=data_length) / number_of_seats  # same as u but in list form

    return u, utilization, number_of_seats,data_length


def compute_formula_second_term(utilization, node_capacity, n_seats, u):
    u_to_c_over_c_fact = math.fdiv(math.power(u, n_seats), math.factorial(n_seats))
    p_to_K_minus_C_plus1 = math.power(utilization, (node_capacity - n_seats + 1))
    one_minus_p = math.fsub(1, utilization)
    second_fraction_numerator = math.fsub(1, p_to_K_minus_C_plus1)
    second_fraction = math.fdiv(second_fraction_numerator, one_minus_p)
    return math.fmul(u_to_c_over_c_fact, second_fraction)


def realNumbSum(a, b): return math.fadd(a, b)


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
        temp_real = realNumbSum(factorial_sum[i], second_term[i])
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


def plot_loss_probability(loss_probability_No_Queueing,loss_probability_with_queue):
    plot_axes = plt.gca()
    plot_axes.set_ylabel("Loss Probability", fontsize=14, labelpad=10, rotation=90)
    plot_axes.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

    x_values = np.arange(start=0, stop=len(loss_probability_No_Queueing), step=1.0)

    plot_axes.plot(x_values, loss_probability_No_Queueing, marker="", lw=2, label="More Seat")
    plot_axes.plot(x_values, loss_probability_with_queue, marker="", lw=2, label="More Queue")

    plt.legend(loc="upper right", prop={'size': 14})
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
   

if __name__ == "__main__":
    main()
