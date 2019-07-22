import numpy as np
# from scipy.optimize import minimize, LinearConstraint

from copy import copy, deepcopy
from math import log


def entropy(alloc, votes, divisor_gen, c_num, p_num):
    """
    Calculate entropy of the election, taking into account votes and
     allocations.
     $\\sum_i \\sum_j \\sum_k \\log{v_{ij}/d_k}$, more or less.
    """
    e = 0
    for i in range(c_num):
        divisor_gens = [divisor_gen() for x in range(p_num)]
        for j in range(p_num):
            for k in range(int(alloc[i*p_num+j])):
                dk = next(divisor_gens[j])
                e -= log(votes[i*p_num+j]/dk)

    return e


def opt_entropy(m_votes, v_desired_row_sums, v_desired_col_sums,
                m_prior_allocations, divisor_gen, threshold, **kwargs):

    alloc = []
    for const in m_prior_allocations:
        alloc.extend(copy(const))
    votes = []
    for const in m_votes:
        votes.extend(copy(const))
    seats = copy(v_desired_row_sums)

    c = len(m_votes)
    p = len(m_votes[0])
    linear_constraints = []
    for i in range(c):
        a = [0]*p*i
        a.extend([1]*p)
        a.extend([0]*p*(c-i-1))
        lc = LinearConstraint(a, seats[i], seats[i])
        linear_constraints.append(lc)

    res = minimize(entropy, alloc, args=(votes,divisor_gen,c,p),
            method='trust-constr', constraints=linear_constraints)

    v_results = res.x
    results = []
    for i in range(c):
        results.append(v_results[i*p:(i+1)*p])

    return results, None
