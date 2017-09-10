from copy import copy


def apportion1d(v_votes, num_total_seats, prior_allocations, divisor_gen):
    """
    Perform a one-dimensional apportionment of seats.
    Inputs:
        - v_votes: Vector of votes to base the apportionment on.
        - num_total_seats: Total number of seats to allocate.
        - prior_allocations: Prior allocations to each party.
        - divisor_gen: A divisor generator function, e.g. Sainte-Lague.
    Outputs:
        - allocations vector
        - a tuple containing current divisors, divisor generators, and the
          smallest used divided vote value.
    """
    N = len(v_votes)
    divisor_gens = [divisor_gen() for x in range(N)]
    divisors = []
    for n in range(N):
        for j in range(prior_allocations[n]+1):
            x = next(divisor_gens[n])
        divisors.append(x)

    allocations = copy(prior_allocations)

    num_preallocated_seats = sum(prior_allocations)
    min_used = 1000000
    for j in range(num_total_seats-num_preallocated_seats):
        divided_votes = [float(v_votes[i])/divisors[i]
                         if v_votes[i] is not None else None
                         for i in range(N)]
        maxvote = max(divided_votes)
        min_used = maxvote
        maxparty = divided_votes.index(maxvote)
        divisors[maxparty] = next(divisor_gens[maxparty])
        allocations[maxparty] += 1

    return allocations, (divisors, divisor_gens, min_used)

