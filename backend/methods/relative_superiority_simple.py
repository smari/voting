#coding:utf-8
from copy import deepcopy, copy
from apportion import apportion1d, threshold_elimination_constituencies
from table_util import v_subtract

def relative_superiority_simple(m_votes, v_desired_row_sums, v_desired_col_sums,
    m_prior_allocations, divisor_gen, threshold=None, **kwargs):
    """Apportion by Þorkell Helgason's Relative Superiority method"""
    num_constituencies = len(v_desired_row_sums)
    num_parties        = len(v_desired_col_sums)
    assert len(m_votes) == num_constituencies
    assert all(len(row) == num_parties for row in m_votes)
    assert len(m_prior_allocations) == num_constituencies
    assert all(len(row) == num_parties for row in m_prior_allocations)
    m_allocations = deepcopy(m_prior_allocations)
    num_allocated = sum([sum(x) for x in m_allocations])
    num_total_seats = sum(v_desired_row_sums)
    allocation_sequence = []
    for n in range(num_total_seats-num_allocated):
        v_col_sums = [sum(col) for col in zip(*m_allocations)]
        v_col_slacks = v_subtract(v_desired_col_sums, v_col_sums)
        hungry_parties = [p for p in range(num_parties) if v_col_slacks[p]>0]
        v_row_sums = [sum(row) for row in m_allocations]
        v_row_slacks = v_subtract(v_desired_row_sums, v_row_sums)
        unfilled_const = [c for c in range(num_constituencies) if v_row_slacks[c]>0]
        necessary = []
        available = []
        violating = []
        for c in unfilled_const:
            running_lists = [p for p in range(num_parties) if m_votes[c][p]>0]
            if len(running_lists) == 0:
                raise RuntimeError(f"After allocating {n} adjustment seats, "
                    f"constituency {c} has not been filled, "
                    "but there are no parties with any votes "
                    "in this constituency (after threshold elimination).")
            hungry_lists = set(running_lists).intersection(hungry_parties)
            if len(hungry_lists) == 0:
                # All parties running in this constituency (and above threshold)
                #  have already been satisfied
                v_slacks = []
            else:
                v_slacks = v_col_slacks

            # Find the party next in line in the constituency:
            alloc_next, div_next = apportion1d(
                v_votes=m_votes[c],
                num_total_seats=v_row_sums[c] + 1,
                prior_allocations=m_allocations[c],
                divisor_gen=divisor_gen,
                v_max_left=v_slacks
            )
            diff = v_subtract(alloc_next, m_allocations[c])
            next_in = diff.index(1)
            if len(hungry_lists) == 0:
                violating.append({
                    "constituency": c,
                    "party": next_in,
                    "divided_votes": div_next[2],
                })
                continue

            # Calculate continuation:
            v_slacks = [v_col_slacks[p] if m_votes[c][p]>0 else 0 for p in range(num_parties)]
            v_slacks[next_in] = 0
            if sum(v_slacks) < v_row_slacks[c]:
                # top list must get a seat, else it's impossible to man all seats in this constituency
                necessary.append({
                    "constituency": c,
                    "party": next_in,
                    "divided_votes": div_next[2],
                })
                continue
            _, div_after = apportion1d(
                v_votes=m_votes[c],
                num_total_seats=v_row_sums[c] + 1,
                prior_allocations=m_allocations[c],
                divisor_gen=divisor_gen,
                v_max_left=v_slacks
            )

            # Calculate relative superiority
            rs = float(div_next[2])/div_after[2]
            available.append({
                "constituency": c,
                "party": next_in,
                "divided_votes": div_next[2],
                "superiority": rs,
            })

        greatest = 0
        first = None
        if necessary:
            # Allocate necessary seats first
            for item in necessary:
                if item["divided_votes"] > greatest:
                    greatest = item["divided_votes"]
                    first = item
            first["reason"] = "Can't fill this constituency without this list"
        elif available:
            # Allocate seat in constituency where the calculated
            #  relative superiority is highest:
            for item in available:
                if item["superiority"] > greatest:
                    greatest = item["superiority"]
                    first = item
            first["reason"] = "Greatest relative superiority"
        else:
            assert violating
            # Allocate violating seats last
            for item in violating:
                if item["divided_votes"] > greatest:
                    greatest = item["divided_votes"]
                    first = item
            first["reason"] = "Must violate party sums to fill this constituency"
        const = first["constituency"]
        party = first["party"]
        m_allocations[const][party] += 1
        allocation_sequence.append(first)

    return m_allocations, (allocation_sequence, present_allocation_sequence)


def present_allocation_sequence(rules, allocation_sequence):
    headers = ["Adj. seat #", "Constituency", "Party",
        "Reason", "Superiority"]
    data = []
    seat_number = 0

    for allocation in allocation_sequence:
        seat_number += 1
        superiority = round(allocation["superiority"], 3) \
            if "superiority" in allocation else "N/A"
        data.append([
            seat_number,
            rules["constituencies"][allocation["constituency"]]["name"],
            rules["parties"][allocation["party"]],
            allocation["reason"],
            superiority,
        ])

    return headers, data
