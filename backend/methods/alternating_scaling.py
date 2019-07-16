from apportion import apportion1d
from copy import deepcopy


def alternating_scaling(m_votes, v_desired_row_sums, v_desired_col_sums,
                        m_prior_allocations, divisor_gen, threshold,
                        **kwargs):
    """
    # Implementation of the Alternating-Scaling algorithm.

    Inputs:
        - m_votes: A matrix of votes (rows: constituencies, columns:
            parties)
        - v_desired_row_sums: A vector of total seats in each constituency
        - v_desired_col_sums: A vector of seats allocated to parties
        - m_prior_allocations: A matrix of where parties have previously
            gotten seats
        - divisor_gen: A generator function generating divisors, e.g. d'Hondt
        - threshold: A cutoff threshold for participation, between 0 and 100.
    """
    m_allocations = deepcopy(m_prior_allocations)

    def const_step(v_votes, const_id, const_multipliers, party_multipliers):
        num_total_seats = v_desired_row_sums[const_id]
        cm = const_multiplier = const_multipliers[const_id]
        # See IV.3.5 in paper:
        v_scaled_votes = [a/(b*cm) if b*cm != 0 else 0
                          for a, b in zip(v_votes, party_multipliers)]

        v_priors = m_allocations[const_id]

        _, div = apportion1d(v_scaled_votes, num_total_seats,
                                 v_priors, divisor_gen)

        # See IV.3.9 in paper:
        minval = div[2] # apportion1d gives the last used value, which is min
        maxval = max([float(a)/b for a, b in zip(v_scaled_votes, div[0])])
        const_multiplier = (minval+maxval)/2

        return const_multiplier

    def party_step(v_votes, party_id, const_multipliers, party_multipliers):
        num_total_seats = v_desired_col_sums[party_id]
        pm = party_multiplier = party_multipliers[party_id]

        v_scaled_votes = [a/(b*pm) if b*pm != 0 else 0
                          for a, b in zip(v_votes, const_multipliers)]

        v_priors = [const_alloc[party_id] for const_alloc in m_allocations]

        _, div = apportion1d(v_scaled_votes, num_total_seats, v_priors,
                                 divisor_gen)

        minval = div[2]
        maxval = max([float(a)/b for a, b in zip(v_scaled_votes, div[0])])
        party_multiplier = (minval+maxval)/2

        return party_multiplier

    num_constituencies = len(m_votes)
    num_parties = len(m_votes[0])
    const_multipliers = [1] * num_constituencies
    party_multipliers = [1] * num_parties
    step = 0

    while step < 100:
        # Constituency step:
        c_muls = []
        for c in range(num_constituencies):
            mul = const_step(m_votes[c], c, const_multipliers,
                                party_multipliers)
            const_multipliers[c] *= mul
            c_muls.append(mul)
        const_done = all([round(x, 5) == 1.0 or x == 500000 for x in c_muls])

        # Party step:
        p_muls = []
        for p in range(num_parties):
            vp = [v[p] for v in m_votes]
            mul = party_step(vp, p, const_multipliers, party_multipliers)
            party_multipliers[p] *= mul
            p_muls.append(mul)
        party_done = all([round(x, 5) == 1.0 or x == 500000 for x in p_muls])

        step += 1

        if const_done and party_done:
            break

    if not (const_done and party_done):
        raise RuntimeError("AS does not seem to be converging.")


    # Finally, use party_multipliers and const_multipliers to arrive at
    #  final apportionment:
    results = []
    for c in range(num_constituencies):
        num_total_seats = v_desired_row_sums[c]
        cm = const_multipliers[c]
        v_scaled_votes = [a/(b*cm) if b*cm != 0 else None
                          for a, b in zip(m_votes[c], party_multipliers)]
        v_priors = m_allocations[c]
        alloc, _ = apportion1d(v_scaled_votes, num_total_seats,
                                 v_priors, divisor_gen)
        results.append(alloc)

    return results, None
