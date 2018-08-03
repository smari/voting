#coding:utf-8
from copy import deepcopy
from apportion import apportion1d
import random

def pure_vote_ratios_apportionment(m_votes, v_const_seats, v_party_seats,
                            m_prior_allocations, divisor_gen, threshold=None,
                            orig_votes=None, **kwargs):
	m_allocations = deepcopy(m_prior_allocations)

	num_allocated = sum([sum(c) for c in m_allocations])
	total_seats = sum(v_const_seats)

	for n in range(total_seats-num_allocated):
		m_seat_props = []
		maximums = []
		for const in range(len(m_votes)):
			m_seat_props.append([])
			s = sum(orig_votes[const])
			for party in range(len(m_votes[const])):
				div = divisor_gen()
				for k in range(m_allocations[const][party]+1):
					x = next(div)
				a = (float(orig_votes[const][party])/s)/x
				m_seat_props[const].append(a)
			maximums.append(max(m_seat_props[const]))

			if sum(m_allocations[const]) == v_const_seats[const]:
				m_seat_props[const] = [0]*len(m_votes[const])
				maximums[const] = 0

		maximum = max(maximums)
		c = maximums.index(maximum)
		p = m_seat_props[c].index(maximum)

		m_allocations[c][p] += 1


	return m_allocations, None
