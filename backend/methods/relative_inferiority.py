#coding:utf-8
from copy import copy
from apportion import apportion1d

def relative_inferiority(m_votes, v_const_seats, v_party_seats,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """
    Apportion by Þorkell Helgason's Relative Inferiority method.
    This method is incomplete.
    """
    m_allocations = copy(m_prior_allocations)
    m_max_seats = [[min(Ci, Pj) for Pj in v_party_seats]
                   for Ci in v_const_seats]
    # Probably not needed:
    const_filled = [False] * len(v_const_seats)
    party_filled = [False] * len(v_party_seats)

    # num_allocated =
    for i in range(10):
        for i in range(len(v_const_seats)):
            app = apportion1d(m_votes[i], 10, m_allocations[i], divisor_gen)

    return m_allocations
