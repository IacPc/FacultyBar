import configparser as cp
import texttable as tt
import numpy as np
import json
import math


def convert_min_to_sec(value):
    return value*60


def load_parameters():
    config = cp.ConfigParser()
    config.read("settings.ini")

    vip_arrival_rate = 1/convert_min_to_sec(config["Customer"].getfloat("vip_interarrival_time"))
    normal_arrival_rate = 1/convert_min_to_sec(config["Customer"].getfloat("normal_interarrival_time"))
    eating_rate = 1/convert_min_to_sec(config["Customer"].getfloat("eating_time"))
    number_of_seats = np.array(json.loads(config.get("SeatingNode", "number_of_seats")))
    queue_size = np.array(json.loads(config.get("SeatingNode", "queue_size")))

    if len(number_of_seats) != len(queue_size):
        print("ERROR: the two lists number_of_seats and queue_size must have the same size")
        exit()

    u = (vip_arrival_rate + normal_arrival_rate)/eating_rate
    utilization = np.full(fill_value=u, shape=len(number_of_seats))/number_of_seats
    node_capacity = number_of_seats + queue_size

    if len(utilization[utilization >= 1]) > 0:
        print("ERROR: One utilization is higher than one")
        exit()

    return u, utilization, node_capacity, number_of_seats, queue_size


def compute_p0(u, utilization, node_capacity, number_of_seats):
    factorial_sum = []
    for n_seats in number_of_seats:
        temp_sum = 0
        for j in range(0, n_seats):
            temp_sum += (u**j)/math.factorial(j)

        factorial_sum.append(temp_sum)

    second_term = []
    if u == 1:
        for index, n_seats in enumerate(number_of_seats):
            work = ((1-((1/n_seats)**(node_capacity[index]-n_seats+1)))/(1-1/n_seats))*(1/math.factorial(n_seats))
            second_term.append(work)
    else:
        for index, n_seats in enumerate(number_of_seats):
            work = ((1-(utilization[index]**(node_capacity[index]-n_seats+1)))/(1-utilization[index]))*((u**n_seats)/math.factorial(n_seats))
            second_term.append(work)

    denominator = np.array(factorial_sum) + np.array(second_term)

    return np.ones(shape=len(utilization))/denominator


def compute_loss_probability(u, utilization, node_capacity, number_of_seats):
    p0 = compute_p0(u, utilization, node_capacity, number_of_seats)

    loss_probability = []
    for index, n_seats in enumerate(number_of_seats):
        loss = ((u**node_capacity[index])/(math.factorial(n_seats)*(n_seats**(node_capacity[index]-n_seats))))*p0[index]
        loss_probability.append(loss)

    return loss_probability


def main():
    u, utilization, node_capacity, number_of_seats, queue_size = load_parameters()
    loss_probability = compute_loss_probability(u, utilization, node_capacity, number_of_seats)

    result_table = tt.Texttable()
    result_table.header(["Node capacity", "Number of seats", "Queue capacity", "Loss probability"])
    result_table.set_cols_dtype(["t", "t", "t", "t"])

    for row in zip(node_capacity, number_of_seats, queue_size, loss_probability):
        result_table.add_row(row)

    print(result_table.draw())


if __name__ == "__main__":
    main()
