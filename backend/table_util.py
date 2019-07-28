
from math import log
from copy import deepcopy


def v_subtract(u, v):
    n = len(u)
    assert len(v) == n
    return [u[i] - v[i] for i in range(n)]

def m_subtract(A, B):
    m = len(A)
    assert(len(B) == m)
    if m == 0:
        return []
    n = len(A[0])
    assert(all([len(A[i]) == n and len(B[i]) == n for i in range(m)]))
    return [
        [A[i][j] - B[i][j] for j in range(n)]
        for i in range(m)
    ]

def scale_matrix(A, c):
    return [[a*c for a in row] for row in A]

def add_totals(m):
    """Add sums of rows and columns to a table."""
    nm = deepcopy(m)
    for i in range(len(m)):
        nm[i].append(sum(m[i]))
    totals = [sum(x) for x in zip(*nm)]
    nm.append(totals)
    return nm

def find_xtd_shares(xtd_table):
    return [[float(v)/c[-1] if c[-1]!=0 else 0 for v in c] for c in xtd_table]

def find_shares(table):
    return [find_shares_1d(c) for c in table]

def find_shares_1d(v_votes):
    assert all(v>=0 for v in v_votes), f"negative values detected in {v_votes}"
    s = sum(v_votes)
    return [float(v)/s for v in v_votes] if s!=0 else v_votes

def entropy(votes, allocations, divisor_gen):
    """
    Calculate entropy of the election, taking into account votes and
     allocations.
     $\\sum_i \\sum_j \\sum_k \\log{v_{ij}/d_k}$, more or less.
    """
    assert(type(votes) == list)
    assert(all(type(v) == list for v in votes))
    assert(type(allocations) == list)
    assert(all(type(a) == list for a in allocations))

    e = 0
    for c in range(len(votes)):
        for p in range(len(votes[c])):
            gen = divisor_gen()
            for k in range(allocations[c][p]):
                dk = next(gen)
                e += log(votes[c][p]/dk)
    return e
