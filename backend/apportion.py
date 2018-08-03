from copy import copy


def apportion1d(v_votes, num_total_seats, prior_allocations, divisor_gen,
                invalid=[]):
    """
    Perform a one-dimensional apportionment of seats.
    Inputs:
        - v_votes: Vector of votes to base the apportionment on.
        - num_total_seats: Total number of seats to allocate.
        - prior_allocations: Prior allocations to each party.
        - divisor_gen: A divisor generator function, e.g. Sainte-Lague.
        - invalid: A list of parties that cannot be allocated more seats.
            (Added for Icelandic law adjustment seat apportionment.)
    Outputs:
        - allocations vector
        - a tuple containing current divisors, divisor generators, and the
          smallest used divided vote value.
    """
    N = len(v_votes)
    divisor_gens = [divisor_gen() for x in range(N)]
    divisors = []
    for n in range(N):
        for i in range(prior_allocations[n]+1):
            x = next(divisor_gens[n])
        divisors.append(x)

    allocations = copy(prior_allocations)

    num_allocated = sum(prior_allocations)
    min_used = 1000000
    while num_allocated < num_total_seats:
        divided_votes = [float(v_votes[i])/divisors[i]
                         if v_votes[i] is not None else 0
                         for i in range(N)]
        maxvote = max(divided_votes)
        min_used = maxvote
        maxparty = divided_votes.index(maxvote)
        divisors[maxparty] = next(divisor_gens[maxparty])
        if maxparty not in invalid:
            allocations[maxparty] += 1
            num_allocated += 1

    return allocations, (divisors, divisor_gens, min_used)


def threshold_elimination_constituencies(votes, threshold, party_seats=None,
                                            priors=None):
    """
    Eliminate parties that don't reach national threshold.
    Optionally, eliminate parties that have already gotten all their
    calculated seats.

    Inputs:
        - votes: Matrix of votes.
        - threshold: Real value between 0.0 and 1.0 with the cutoff threshold.
        - [party_seats]: seats that should be allocated to each party
        - [priors]: a matrix of prior allocations to each party per
            constituency
    Outputs:
        - Matrix of votes with eliminated parties zeroed out.
    """
    N = len(votes[0])
    totals = [sum(x) for x in zip(*votes)]
    country_total = sum(totals)
    percent = [float(t)/country_total for t in totals]
    m_votes = []

    for c in votes:
        cons = []
        for p in range(N):
            if percent[p] > threshold:
                v = c[p]
            else:
                v = 0
            cons.append(v)
        m_votes.append(cons)

    if not (priors and party_seats):
        return m_votes

    for p in range(N):
        if party_seats[p] == sum([const[p] for const in priors]):
            for c in range(len(votes)):
                m_votes[c][p] = 0

    return m_votes

def threshold_elimination_totals(votes, threshold):
    """
    Eliminate parties that do not reach the threshold proportion of
    national votes. Replaces such parties with zeroes.
    """
    N = len(votes[0])
    totals = [sum(x) for x in zip(*votes)]
    country_total = sum(totals)
    percent = [float(t)/country_total for t in totals]
    cutoff = [totals[p] if percent[p] > threshold else 0
                for p in range(len(totals))]

    return cutoff
