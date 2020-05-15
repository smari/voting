

import division_rules
from methods.alternating_scaling import alternating_scaling

def solution_exists(votes, row_constraints, col_constraints, prior_allocations):
    assert sum(row_constraints) == sum(col_constraints)
    num_constituencies = len(row_constraints)
    num_parties = len(col_constraints)
    assert len(votes) == num_constituencies, (
        "The vote matrix does not match the constituency list.")
    assert all(len(row) == num_parties for row in votes), (
        "The vote matrix does not match the party list.")
    assert len(prior_allocations) == num_constituencies, (
        "The allocation matrix does not match the constituency list.")
    assert all(len(row) == num_parties for row in prior_allocations), (
        "The allocation matrix does not match the party list.")

    epsilon = 0.0000001
    adjusted_votes = [[v if v>0 else epsilon for v in row] for row in votes]
    try:
        result, _ = alternating_scaling(
            m_votes=adjusted_votes,
            v_desired_row_sums=row_constraints,
            v_desired_col_sums=col_constraints,
            m_prior_allocations=prior_allocations,
            divisor_gen=division_rules.dhondt_gen,
            threshold=0)
    except RuntimeError:
        return False
    for c in range(num_constituencies):
        for p in range(num_parties):
            if result[c][p]>prior_allocations[c][p] and votes[c][p]==0:
                return False
    return True
