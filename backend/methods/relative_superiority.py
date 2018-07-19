#coding:utf-8
from copy import deepcopy, copy
from apportion import apportion1d, threshold_elimination_constituencies

def relative_superiority(m_votes, v_const_seats, v_party_seats,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """Apportion by Þorkell Helgason's Relative Superiority method"""

    m_allocations = deepcopy(m_prior_allocations)
    num_allocated = sum([sum(x) for x in m_allocations])
    num_total_seats = sum(v_const_seats)
    for n in range(num_total_seats-num_allocated):
        m_votes = threshold_elimination_constituencies(m_votes, 0.0,
                    v_party_seats, m_allocations)
        superiority = []
        first_in = []
        for j in range(len(m_votes)):
            seats_left = v_const_seats[j] - sum(m_allocations[j])
            if not seats_left:
                superiority.append(0)
                first_in.append(0)
                continue

            # Find the party next in line in the constituency:
            next_alloc_num = sum(m_allocations[j]) + 1
            alloc_next, div_next = apportion1d(m_votes[j], next_alloc_num,
                                   m_allocations[j], divisor_gen)
            diff = [alloc_next[i]-m_allocations[j][i] 
                    for i in range(len(m_votes[j]))]
            next_in = diff.index(1)
            first_in.append(next_in)
            # Calculate continuation:
            _, div_after = apportion1d(m_votes[j],
                                        v_const_seats[j]+1,
                                        m_allocations[j],
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

    return m_allocations
