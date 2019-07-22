#coding:utf-8
from copy import deepcopy, copy
from apportion import apportion1d, threshold_elimination_constituencies

def relative_superiority(m_votes, v_desired_row_sums, v_desired_col_sums,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """Apportion by Þorkell Helgason's Relative Superiority method"""

    m_allocations = deepcopy(m_prior_allocations)
    num_allocated = sum([sum(x) for x in m_allocations])
    num_total_seats = sum(v_desired_row_sums)
    for n in range(num_total_seats-num_allocated):
        m_votes = threshold_elimination_constituencies(m_votes, 0.0,
                    v_desired_col_sums, m_allocations)
        superiority = []
        first_in = []
        for c in range(len(m_votes)):
            seats_left = v_desired_row_sums[c] - sum(m_allocations[c])
            if not seats_left:
                superiority.append(0)
                first_in.append(0)
                continue

            # Find the party next in line in the constituency:
            next_alloc_num = sum(m_allocations[c]) + 1
            alloc_next, div_next = apportion1d(m_votes[c], next_alloc_num,
                                   m_allocations[c], divisor_gen)
            diff = [alloc_next[p]-m_allocations[c][p]
                    for p in range(len(m_votes[c]))]
            next_in = diff.index(1)
            first_in.append(next_in)

            # Calculate continuation:
            _, div_after = apportion1d(m_votes[c],
                                        v_desired_row_sums[c]+1,
                                        m_allocations[c],
                                        divisor_gen)

            # Calculate relative superiority
            try:
                rs = float(div_next[2])/div_after[2]
            except ZeroDivisionError:
                # If the next party is last possible, it must get the seat
                rs = 1000000
            superiority.append(rs)

        # Allocate seat in constituency where the calculated
        #  relative superiority is highest:
        greatest = max(superiority)
        idx = superiority.index(greatest)
        m_allocations[idx][first_in[idx]] += 1

    return m_allocations, None
