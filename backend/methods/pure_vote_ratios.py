#coding:utf-8
from copy import deepcopy
from apportion import apportion1d
import random

def pure_vote_ratios_apportionment(m_votes, v_desired_row_sums, v_desired_col_sums,
                            m_prior_allocations, divisor_gen, threshold=None,
                            orig_votes=None, **kwargs):
    m_allocations = deepcopy(m_prior_allocations)

    num_allocated = sum([sum(c) for c in m_allocations])
    total_seats = sum(v_desired_row_sums)
    allocation_sequence = []

    for n in range(total_seats-num_allocated):
        m_seat_props = []
        maximums = []
        for const in range(len(m_votes)):
            m_seat_props.append([])
            s = sum(orig_votes[const])
            for party in range(len(m_votes[const])):
                a = 0
                col_sum = sum(row[party] for row in m_allocations)
                if col_sum < v_desired_col_sums[party]:
                    div = divisor_gen()
                    for k in range(m_allocations[const][party]+1):
                        x = next(div)
                    a = (float(orig_votes[const][party])/s)/x
                m_seat_props[const].append(a)
            maximums.append(max(m_seat_props[const]))

            if sum(m_allocations[const]) == v_desired_row_sums[const]:
                m_seat_props[const] = [0]*len(m_votes[const])
                maximums[const] = 0

        maximum = max(maximums)
        c = maximums.index(maximum)
        p = m_seat_props[c].index(maximum)

        m_allocations[c][p] += 1
        allocation_sequence.append({
            "constituency": c, "party": p,
            "reason": "Highest divided votes",
            "max_list_share": maximum,
        })


    return m_allocations, (allocation_sequence, present_allocation_sequence)


def present_allocation_sequence(rules, allocation_sequence):
    headers = ["Adj. seat #", "Constituency", "Party",
        "Reason", "List share"]
    data = []
    seat_number = 0

    for allocation in allocation_sequence:
        seat_number += 1
        data.append([
            seat_number,
            rules["constituencies"][allocation["constituency"]]["name"],
            rules["parties"][allocation["party"]],
            allocation["reason"],
            "{:.3%}".format(allocation["max_list_share"])
        ])

    return headers, data
