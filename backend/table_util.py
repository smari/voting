
from math import log
from copy import deepcopy


def matrix_subtraction(A, B):
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

def check_vote_table(vote_table):
    """Checks vote_table input, and translates empty cells to zeroes

    Raises:
        KeyError: If vote_table or constituencies are missing a component
        ValueError: If the dimensions of the table are inconsistent
            or not enough seats are specified
        TypeError: If vote or seat counts are not given as numbers
    """
    for info in [
        "name",
        "votes",
        "parties",
        "constituencies",
    ]:
        if info not in vote_table or not vote_table[info]:
            raise KeyError(f"Missing data ('vote_table.{info}')")

    num_parties = len(vote_table["parties"])
    num_constituencies = len(vote_table["constituencies"])

    if not len(vote_table["votes"]) == num_constituencies:
        raise ValueError("The vote_table does not match the constituency list.")
    for row in vote_table["votes"]:
        if not len(row) == num_parties:
            raise ValueError("The vote_table does not match the party list.")
        for p in range(len(row)):
            if not row[p]: row[p] = 0
            if type(row[p]) != int: raise TypeError("Votes must be numbers.")

    for const in vote_table["constituencies"]:
        if "name" not in const or not const["name"]:
            raise KeyError(f"Missing data ('vote_table.constituencies[x].name')")
        name = const["name"]
        for info in ["num_const_seats", "num_adj_seats"]:
            if info not in const:
                raise KeyError(f"Missing data ('{info}' for {name})")
            if not const[info]: const[info] = 0
            if type(const[info]) != int:
                raise TypeError("Seat specifications must be numbers.")
        if const["num_const_seats"]+const["num_adj_seats"] <= 0:
            raise ValueError("Constituency seats and adjustment seats "
                             "must add to a nonzero number. "
                             f"This is not the case for {name}.")

    return vote_table

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
