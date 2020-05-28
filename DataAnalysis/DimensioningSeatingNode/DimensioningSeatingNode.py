import configparser as cp
import texttable as tt
import numpy as np
import json
import mpmath as math


def convert_min_to_sec(value):
    return value * 60


def load_parameters():
    config = cp.ConfigParser()
    config.read("settings.ini")

    vip_arrival_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("vip_interarrival_time"))
    normal_arrival_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("normal_interarrival_time"))
    eating_rate = 1 / convert_min_to_sec(config["Customer"].getfloat("eating_time"))
    number_of_seats = np.array(json.loads(config.get("SeatingNode", "number_of_seats")))
    queue_size = np.array(json.loads(config.get("SeatingNode", "queue_size")))

    if len(number_of_seats) != len(queue_size):
        print("ERROR: the two lists number_of_seats and queue_size must have the same size")
        exit()

    u = (vip_arrival_rate + normal_arrival_rate) / eating_rate  # scalar
    u_divided_by_nseat = np.full(fill_value=u, shape=len(number_of_seats)) / number_of_seats
    node_capacity = number_of_seats + queue_size  # scalar

    return u, u_divided_by_nseat, node_capacity, number_of_seats, queue_size


def compute_formula_second_term(u_divided_by_nseat, node_capacity, n_seats, u):
    u_to_n_seat_over_n_seat_fact = math.fdiv(math.power(u, n_seats), math.factorial(n_seats))
    second_fraction = 0

    if u_divided_by_nseat == 1:
        second_fraction = node_capacity - n_seats + 1
    else:
        u_div_nseat_to_node_capacity_minus_n_seat_plus1 = math.power(u_divided_by_nseat, (node_capacity - n_seats + 1))
        one_minus_u_divided_by_nseat = math.fsub(1, u_divided_by_nseat)
        second_fraction_numerator = math.fsub(1, u_div_nseat_to_node_capacity_minus_n_seat_plus1)
        second_fraction = math.fdiv(second_fraction_numerator, one_minus_u_divided_by_nseat)

    return math.fmul(u_to_n_seat_over_n_seat_fact, second_fraction)


def compute_p0(u, u_divided_by_nseat, node_capacity, number_of_seats):
    factorial_sum = []
    for n_seats in number_of_seats:
        temp_sum = math.mpf(0.0)  # type = real with arbitary precision
        for j in range(0, n_seats):
            temp_sum = math.fadd(temp_sum, math.fdiv(math.power(u, j), math.factorial(j)))
        factorial_sum.append(temp_sum)

    second_term = []
    for index, n_seats in enumerate(number_of_seats):
        work = compute_formula_second_term(u_divided_by_nseat[index], node_capacity[index], n_seats, u)
        second_term.append(work)

    p0 = []
    one_extended = math.mpf(1.0)
    for i in range(0, len(factorial_sum)):
        temp_real = math.fadd(factorial_sum[i], second_term[i])
        p0.append(math.fdiv(one_extended, temp_real))
    return p0


def compute_single_item_loss_list(u, node_capacity, n_seats, p0):
    u_to_the_node_capacity = math.power(u, node_capacity)
    n_seats_fact = math.factorial(n_seats)
    n_seats_to_the_node_capacity_minus_n_seats = math.power(n_seats, (node_capacity - n_seats))
    denominator = math.fmul(n_seats_fact, n_seats_to_the_node_capacity_minus_n_seats)
    fraction = math.fdiv(u_to_the_node_capacity, denominator)
    return math.fmul(fraction, p0)


def compute_loss_probability(u, u_divided_by_nseat, node_capacity, number_of_seats):
    p0 = compute_p0(u, u_divided_by_nseat, node_capacity, number_of_seats)

    loss_probability = []
    for index, n_seats in enumerate(number_of_seats):
        loss = compute_single_item_loss_list(u, node_capacity[index], n_seats, p0[index])
        loss_probability.append(loss)

    return loss_probability


def main():
    u, u_divided_by_nseat, node_capacity, number_of_seats, queue_size = load_parameters()
    loss_probability = compute_loss_probability(u, u_divided_by_nseat, node_capacity, number_of_seats)

    result_table = tt.Texttable()
    result_table.header(["u/N_SEAT", "Node capacity", "Number of seats", "Queue capacity", "Loss probability"])
    result_table.set_cols_dtype(["t", "t", "t", "t", "t"])

    for row in zip(u_divided_by_nseat, node_capacity, number_of_seats, queue_size, loss_probability):
        result_table.add_row(row)

    print(result_table.draw())


if __name__ == "__main__":
    main()
