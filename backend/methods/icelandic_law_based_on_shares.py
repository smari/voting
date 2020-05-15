#coding:utf-8
from copy import deepcopy
import random

def icelandic_share_apportionment(
    m_votes,
    v_desired_row_sums,
    v_desired_col_sums,
    m_prior_allocations,
    divisor_gen,
    adj_seat_gen,
    threshold=None,
    orig_votes=None,
    **kwargs
):
    """
    Apportion based on Icelandic law nr. 24/2000.
    """
    m_allocations = deepcopy(m_prior_allocations)
    v_seats = [sum(x) for x in zip(*m_prior_allocations)]
    v_votes = [sum(x) for x in zip(*m_votes)]
    num_allocated = sum(v_seats)
    total_seats = sum(v_desired_row_sums)

    invalid = []
    seats_info = []
    while num_allocated < total_seats:
        #if all parties are either invalid or below threshold,
        #then no more seats can be allocated
        if all(p in invalid or v_votes[p] == 0 for p in range(len(v_votes))):
            raise ValueError(f"No valid recipient of seat nr. {num_allocated+1}")

        seat = next(adj_seat)
        while seat["idx"] in invalid:
            seat = next(adj_seat)
        country_num = seat["active_votes"]
        idx = seat["idx"]

        v_proportions = []
        for const in range(len(m_votes)):
            const_votes = orig_votes[const]
            s = sum(const_votes)
            div = divisor_gen()
            for i in range(m_allocations[const][idx]+1):
                x = next(div)
            p = (float(const_votes[idx])/s)*v_desired_row_sums[const]/x
            v_proportions.append(p)

            if sum(m_allocations[const]) == v_desired_row_sums[const]:
                v_proportions[const] = 0

        if max(v_proportions) != 0:
            const = [j for j,k in enumerate(v_proportions)
                        if k == max(v_proportions)]
            if len(const) > 1:
                const = [random.choice(const)]

            m_allocations[const[0]][idx] += 1
            num_allocated += 1
            seats_info.append({
                "constituency": const[0], "party": idx,
                "reason": "Highest list share",
                "country_num": country_num,
                "list_share": v_proportions[const[0]],
            })
        else:
            invalid.append(idx)
    return m_allocations, (seats_info, print_seats)


def print_seats(rules, allocation_sequence):
    # Return data to print breakdown of adjustment seat apportionment
    header = ["Adj. seat #", "Constituency", "Party",
        "Reason", "Country number", "List share"]
    data = []
    seat_number = 0
    for allocation in allocation_sequence:
        seat_number += 1
        data.append([
            seat_number,
            rules["constituencies"][allocation["constituency"]]["name"],
            rules["parties"][allocation["party"]],
            allocation["reason"],
            round(allocation["country_num"], 1),
            "{:.3%}".format(allocation["list_share"])
        ])

    return header, data
