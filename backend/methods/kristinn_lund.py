from apportion import apportion1d
from copy import deepcopy

def kristinn_lund(m_votes, v_const_seats, v_party_seats, m_prior_allocations,
					divisor_gen, threshold=None, orig_votes=None, **kwargs):

	all_const_seats = []
	for c in range(len(m_prior_allocations)):
		alloc, div = apportion1d(m_votes[c], v_const_seats[c],
						m_prior_allocations[c], divisor_gen)
		all_const_seats.append(alloc)

	