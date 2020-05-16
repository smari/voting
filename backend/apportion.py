from copy import copy
from table_util import find_shares_1d

def apportion1d(v_votes, num_total_seats, prior_allocations, divisor_gen,
                threshold=0, v_max_left=[]):
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
    v_votes = threshold_elimination_1d(v_votes, threshold)
    N = len(v_votes)
    divisor_gens = [divisor_gen() for x in range(N)]
    divisors = []
    for n in range(N):
        for i in range(prior_allocations[n]+1):
            x = next(divisor_gens[n])
        divisors.append(x)

    allocations = copy(prior_allocations)
    v_max_left = copy(v_max_left) if v_max_left else [num_total_seats]*N

    num_allocated = sum(prior_allocations)
    min_used = 1000000
    while num_allocated < num_total_seats:
        divided_votes = [float(v_votes[i])/divisors[i]
                         if v_max_left[i]>0 else 0
                         for i in range(N)]
        maxvote = max(divided_votes)
        if maxvote == 0:
            raise ValueError(f"No valid recipient of seat nr. {num_allocated+1}")
        min_used = maxvote
        maxparty = divided_votes.index(maxvote)
        divisors[maxparty] = next(divisor_gens[maxparty])
        allocations[maxparty] += 1
        num_allocated += 1
        v_max_left[maxparty] -= 1

    return allocations, (divisors, divisor_gens, min_used)

def apportion1d_general(
    v_votes,
    num_total_seats,
    prior_allocations,
    rule,
    type_of_rule,
    threshold=0,
):
    """
    Perform a one-dimensional apportionment of seats,
    with a general method,
    whether using largest remainders or a divisor method.
    Inputs:
        - v_votes: Vector of votes to base the apportionment on.
        - num_total_seats: Total number of seats to allocate.
        - prior_allocations: Prior allocations to each party.
        - rule: A rule for selecting the next seat.
        - type_of_rule: A string specifying rule type: "Division" or "Quota".
        - threshold: A cutoff threshold in range [0,100].
    Outputs:
        - allocations vector
        - a generator that generates a sequence of seat allocations,
        -  including vote values used.
        - easy reference to the last seat to be allocated
        - information about the first seat that was not allocated
    """
    N = len(v_votes)
    allocations = copy(prior_allocations) if prior_allocations else [0]*N

    seat_gen = seat_generator(
        votes=threshold_elimination_1d(v_votes, threshold),
        num_total_seats=num_total_seats,
        prior_allocations=copy(allocations),
        rule=rule,
        type_of_rule=type_of_rule
    )

    last_in = None
    gen = seat_gen()
    while sum(allocations) < num_total_seats:
        seat = next(gen)
        allocations[seat["idx"]] += 1
        last_in = seat
    next_in_line = next(gen)

    return allocations, seat_gen, last_in, next_in_line

def seat_generator(
    votes,
    num_total_seats,
    prior_allocations,
    rule,
    type_of_rule
):
    if type_of_rule == "Division":
        seat_gen = seat_generator_div(
            votes=votes,
            prior_allocations=prior_allocations,
            divisor_gen=rule
        )
    else:
        assert type_of_rule == "Quota"
        seat_gen = seat_generator_quota(
            votes=votes,
            num_total_seats=num_total_seats,
            prior_allocations=prior_allocations,
            quota_rule=rule
        )
    return seat_gen

def seat_generator_div(
    votes,
    prior_allocations,
    divisor_gen,
):
    """
    Perform a one-dimensional apportionment of seats,
    using a divsion rule.
    Inputs:
        - votes: Vector of votes to base the apportionment on.
        - prior_allocations: Prior allocations to each party.
        - divisor_gen: A generator for a sequene of divisors to update votes.
    Outputs:
        - a generator that generates a sequence of seat allocations,
        -  including vote values used.
    """
    N = len(votes)
    assert N == len(prior_allocations)
    def seat_gen():
        divisor_gens = [divisor_gen() for x in range(N)]
        active_votes = [0]*N
        for i in range(N):
            for k in range(prior_allocations[i]):
                next(divisor_gens[i])
            active_votes[i] = votes[i]*1.0/next(divisor_gens[i])
        while True:
            idx = active_votes.index(max(active_votes))
            yield {
                "idx": idx,
                "active_votes": active_votes[idx],
            }
            active_votes[idx] = votes[idx]*1.0/next(divisor_gens[idx])

    return seat_gen

def seat_generator_quota(
    votes,
    num_total_seats,
    prior_allocations,
    quota_rule,
):
    """
    Assist with one-dimensional apportionment of seats,
    using a method of largest remainders.
    Inputs:
        - votes: Vector of votes to base the apportionment on.
        - num_total_seats: Total number of seats to allocate.
        - prior_allocations: Prior allocations to each party.
        - quota_rule: A rule to find the number of votes required for a seat.
    Outputs:
        - a generator that generates a sequence of seat allocations,
        -  including vote values used.
    """
    N = len(votes)
    assert N == len(prior_allocations)

    total_votes = sum(votes)
    quota = quota_rule(total_votes, num_total_seats)
    for n in range(N):
        votes[n] -= quota*prior_allocations[n]

    def seat_gen():
        active_votes = copy(votes)
        while True:
            idx = active_votes.index(max(active_votes))
            yield {
                "idx": idx,
                "active_votes": active_votes[idx],
            }
            active_votes[idx] -= quota

    return seat_gen


def threshold_elimination_constituencies(votes, threshold, party_seats=None,
                                            priors=None):
    """
    Eliminate parties that don't reach national threshold.
    Optionally, eliminate parties that have already gotten all their
    calculated seats.

    Inputs:
        - votes: Matrix of votes.
        - threshold: Real value between 0.0 and 100.0 with the cutoff threshold.
        - [party_seats]: seats that should be allocated to each party
        - [priors]: a matrix of prior allocations to each party per
            constituency
    Outputs:
        - Matrix of votes with eliminated parties zeroed out.
    """
    N = len(votes[0])
    totals = [sum(x) for x in zip(*votes)]
    shares = find_shares_1d(totals)
    m_votes = [[c[p] if shares[p]*100 > threshold else 0 for p in range(N)]
               for c in votes]

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
    totals = [sum(x) for x in zip(*votes)]
    return threshold_elimination_1d(totals, threshold)

def threshold_elimination_1d(v_votes, threshold):
    shares = find_shares_1d(v_votes)
    cutoff = [v_votes[p] if shares[p]*100 > threshold else 0
                for p in range(len(shares))]
    return cutoff
