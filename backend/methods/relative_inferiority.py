#coding:utf-8
from copy import deepcopy, copy
from apportion import apportion1d, threshold_elimination_constituencies

def relative_inferiority(m_votes, v_desired_row_sums, v_desired_col_sums,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """Apportion by Þorkell Helgason's Relative Inferiority method."""

    assert("last" in kwargs)
    last = kwargs["last"]

    m_allocations = deepcopy(m_prior_allocations)
    num_allocated = sum([sum(x) for x in m_allocations])
    num_total_seats = sum(v_desired_row_sums)
    allocation_sequence = []
    for n in range(num_total_seats-num_allocated):
        m_votes = threshold_elimination_constituencies(m_votes, 0.0,
                    v_desired_col_sums, m_allocations)
        inferiority = []
        first_in = []
        next_used = []
        for j in range(len(m_votes)):
            seats_left = v_desired_row_sums[j] - sum(m_allocations[j])
            if not seats_left:
                inferiority.append(10000000)
                first_in.append(0)
                next_used.append(0)
                continue

            # Find the party next in line in the constituency:
            next_alloc_num = sum(m_allocations[j]) + 1
            alloc_next, div = apportion1d(m_votes[j], next_alloc_num,
                                   m_allocations[j], divisor_gen)
            diff = [alloc_next[i]-m_allocations[j][i]
                    for i in range(len(m_votes[j]))]
            next_in = diff.index(1)
            first_in.append(next_in)
            next_used.append(div[2])

            # Calculate relative inferiority:
            ri = float(last[j])/next_used[j]
            inferiority.append(ri)

        # Allocate seat in constituency where the calculated
        #  relative inferiority is lowest:
        least = min(inferiority)
        idx = inferiority.index(least)
        m_allocations[idx][first_in[idx]] += 1
        last[idx] = next_used[idx]
        allocation_sequence.append({
            "constituency": idx, "party": first_in[idx],
            "reason": "Smallest relative inferiority",
            "min": least,
        })

    return m_allocations, (allocation_sequence, present_allocation_sequence)


def present_allocation_sequence(rules, allocation_sequence):
    headers = ["Adj. seat #", "Constituency", "Party",
        "Reason", "Inferiority"]
    data = []
    seat_number = 0

    for allocation in allocation_sequence:
        seat_number += 1
        data.append([
            seat_number,
            rules["constituencies"][allocation["constituency"]]["name"],
            rules["parties"][allocation["party"]],
            allocation["reason"],
            round(allocation["min"], 3),
        ])

    return headers, data
