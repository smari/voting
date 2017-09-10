


def alternating_scaling(m_votes, v_const_seats, v_party_seats,
                        m_prior_allocations, divisor_gen, threshold, **kwargs):
    """
    # Implementation of the Alternating-Scaling algorithm.

    Inputs:
        - m_votes_orig: A matrix of votes (rows: constituencies, columns:
          parties)
        - v_const_seats: A vector of constituency seats
        - v_party_seats: A vector of seats allocated to parties
        - m_prior_allocations: A matrix of where parties have previously gotten
          seats
        - divisor_gen: A generator function generating divisors, e.g. d'Hondt
        - threshold: A cutoff threshold for participation.
    """

    def const_step(v_votes, const_id, v_const_multipliers, v_party_multipliers):
        num_total_seats = v_const_seats[const_id]
        cm = const_multiplier = v_const_multipliers[const_id]
        # See IV.3.5 in paper:
        v_scaled_votes = [a/(b*cm) if b*cm != 0 else 0
                          for a, b in zip(v_votes, v_party_multipliers)]

        v_priors = m_prior_allocations[const_id]

        alloc, div = apportion1d(v_scaled_votes, num_total_seats,
                                 v_priors, divisor_gen)

        # See IV.3.9 in paper:
        minval = div[2] # apportion1d gives us the last used value, which is min
        maxval = max([float(a)/b if a is not 0 and a is not None else 0
                      for a, b in zip(v_scaled_votes, div[0])])
        const_multiplier = (minval+maxval)/2

        # TODO: Make pretty-print intermediate tables on --debug
        # Results -- kind of
        #print "Constituency %d" % (const_id)
        #print " - Divisors: ", div[0]
        #print " - Scaled: ", v_scaled_votes
        #print " - Min: ", minval
        #print " - Max: ", maxval
        #print " - New const multiplier: ", const_multiplier
        #print " - Allocations: ", alloc
        return alloc, const_multiplier

    def party_step(v_votes, party_id, v_const_multipliers, v_party_multipliers):
        num_total_seats = v_party_seats[party_id]
        pm = party_multiplier = v_party_multipliers[party_id]
        #
        v_scaled_votes = [a/(b*pm) if b != 0 else None
                          for a, b in zip(v_votes, v_const_multipliers)]

        v_priors = [m_prior_allocations[x][party_id]
                    for x in range(len(m_prior_allocations))]

        alloc, div = apportion1d(v_scaled_votes, num_total_seats, v_priors,
                                 divisor_gen)

        minval = div[2]
        maxval = max([float(a)/b if a is not None else 0
                      for a, b in zip(v_scaled_votes, div[0])])
        party_multiplier = (minval+maxval)/2

        # TODO: Make pretty-print intermediate tables on --debug
        #print "Party %d" % (party_id)
        #print " - Divisors: ", div[0]
        #print " - Scaled: ", v_scaled_votes
        #print " - Min: ", minval
        #print " - Max: ", maxval
        #print " - New const multiplier: ", party_multiplier
        #print " - Allocations: ", alloc

        return alloc, party_multiplier

    num_constituencies = len(m_votes)
    num_parties = len(m_votes[0])
    const_multipliers = [1] * num_constituencies
    party_multipliers = [1] * num_parties
    step = 0

    const_done = False
    party_done = False
    while step < 200:
        step += 1
        if step % 2 == 1:
            #Constituency step:
            muls = []
            for c in range(num_constituencies):
                alloc, mul = const_step(m_votes[c], c, const_multipliers,
                                        party_multipliers)
                const_multipliers[c] *= mul
                muls.append(mul)
            const_done = all([round(x, 5) == 1.0 or x == 500000 for x in muls])
        else:
            # print "== Party step %d ==" % step
            muls = []
            for p in range(num_parties):
                vp = [v[p] for v in m_votes]
                alloc, mul = party_step(vp, p, const_multipliers, party_multipliers)
                party_multipliers[p] *= mul
                muls.append(mul)
            party_done = all([round(x, 5) == 1.0 or x == 500000 for x in muls])

        if const_done and party_done:
            break

    # Finally, use party_multipliers and const_multipliers to arrive at
    #  final apportionment:
    results = []
    for c in range(num_constituencies):
        num_total_seats = v_const_seats[c]
        cm = const_multipliers[c]
        v_scaled_votes = [a/(b*cm) if b != 0 else None
                          for a, b in zip(m_votes[c], party_multipliers)]
        v_priors = m_prior_allocations[c]
        alloc, div = apportion1d(v_scaled_votes, num_total_seats,
                                 v_priors, divisor_gen)
        results.append(alloc)

    return results
