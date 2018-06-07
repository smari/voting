#coding:utf-8
from copy import deepcopy, copy
from apportion import apportion1d, threshold_elimination_constituencies

def relative_inferiority(m_votes, v_const_seats, v_party_seats,
                         m_prior_allocations, divisor_gen, last, threshold=None,
                         **kwargs):
    """
    Apportion by Þorkell Helgason's Relative Inferiority method.
    This method is incomplete.
    """
    m_allocations = deepcopy(m_prior_allocations)
    num_allocated = sum([sum(x) for x in m_allocations])
    num_total_seats = sum(v_const_seats)
    for n in range(num_total_seats-num_allocated):
        m_votes = threshold_elimination_constituencies(m_votes, 0.0, 
                    v_party_seats, m_allocations)
        inferiority = []
        first_in = []
        L = []
        for j in range(len(m_votes)):
            seats_left = v_const_seats[j] - sum(m_allocations[j])
            if not seats_left:
                inferiority.append(10000000)
                first_in.append(0)
                L.append(0)
                continue

            next_alloc_num = sum(m_allocations[j]) + 1
            alloc_next, div = apportion1d(m_votes[j], next_alloc_num,
                                   m_allocations[j], divisor_gen)
            diff = [alloc_next[i]-m_allocations[j][i] 
                    for i in range(len(m_votes[j]))]
            next_in = diff.index(1)
            first_in.append(next_in)
            L.append(div[2])

            # Calculate relative inferiority
            try:
                rs = float(last[j])/div[2]
            except ZeroDivisionError:
                rs = 10000000
            inferiority.append(rs)

        least = min(inferiority)
        idx = inferiority.index(least)
        m_allocations[idx][first_in[idx]] += 1
        last[idx] = L[idx]

    return m_allocations