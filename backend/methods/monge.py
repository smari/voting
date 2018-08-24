from copy import deepcopy

def monge(
    votes,             #2d - votes for each list
    c_goals,           #1d - total number of seats in each constituency
    p_goals,           #1d - total number of seats for each party
    prior_allocations, #2d - seats already allocated to lists
    divisor_gen,       #divisor sequence formula
    threshold=None,
    orig_votes=None,
    **kwargs
):
    """Apportion by Monge algorithm"""
    allocations = deepcopy(prior_allocations)
    total_seats = sum(c_goals)
    assert(sum(p_goals) == total_seats)
    while sum([sum(x) for x in allocations]) < total_seats:
        best = find_best_Monge_list(
            votes, allocations, c_goals, p_goals, divisor_gen
        )
        if best == None:
            # if we did not find any list now to allocate to,
            # then we won't on further iterations either
            # throw some exception perhaps?
            # TODO: Find better way to indicate this
            return allocations, "Adjustment seat allocation incomplete."
        #allocate seat based on best Monge ratio
        allocations[best["constituency"]][best["party"]] += 1
    return allocations, None

def find_best_Monge_list(
    votes,       #2d - votes for each list
    allocations, #2d - seats already allocated to lists
    c_goals,     #1d - total number of seats in each constituency
    p_goals,     #1d - total number of seats each party is supposed to get
    divisor_gen  #divisor sequence formula
):
    #calculate max_Monge_ratio
    no_constituencies = len(votes)
    no_parties = len(votes[0])
    considerations = []
    for C in range(no_constituencies):
        if constituency_full(C, c_goals, allocations):
            continue #No need to consider lists that can't be given more seats
        for P in range(no_parties):
            if party_satisfied(P, p_goals, allocations):
                continue
            closest = find_closest_comparison(
                C, P, votes, allocations, c_goals, p_goals, divisor_gen
            )
            if closest == None:
                #do not append, ignore list if there is no valid comparison
                continue
            considerations.append({
                "min_ratio": closest["ratio"],
                "constituency": C,
                "party": P,
                "reference_constituency": closest["reference_constituency"],
                "reference_party": closest["reference_party"]
            })
    if considerations:
        ratios = [conion["min_ratio"] for conion in considerations]
        best = considerations[ratios.index(max(ratios))]
        return best
    return None

def party_satisfied(P, p_goals, allocations):
    return sum([const[P] for const in allocations]) >= p_goals[P]

def constituency_full(C, c_goals, allocations):
    return sum(allocations[C]) >= c_goals[C]

def find_closest_comparison(
    C1,          #index of constituency being considered
    P1,          #index of party        being considered
    votes,       #2d - votes for each list
    allocations, #2d - seats already allocated to lists
    c_goals,     #1d - total number of seats in each constituency
    p_goals,     #1d - total number of seats each party is supposed to get
    divisor_gen  #divisor sequence formula
):
    no_constituencies = len(votes)
    no_parties = len(votes[0])
    a = divided_vote(votes, allocations, C1, P1, divisor_gen)
    comparisons = []
    for C2 in range(no_constituencies):
        if C2 == C1:
            continue #compare to lists in different constituencies only
        if constituency_full(C2, c_goals, allocations):
            continue #TODO: Decide if we should compare to unconsidered lists
        for P2 in range(no_parties):
            if P2 == P1:
                continue #compare to lists for different party only
            if party_satisfied(P2, p_goals, allocations):
                continue
            d = divided_vote(votes, allocations, C2, P2, divisor_gen)
            b = divided_vote(votes, allocations, C1, P2, divisor_gen)
            c = divided_vote(votes, allocations, C2, P1, divisor_gen)
            if b > 0 and c > 0:
                comparisons.append({
                    "ratio": (a*d)/(b*c),
                    "reference_constituency": C2,
                    "reference_party": P2
                })
                #TODO: Decide what to do in case b or c is 0.
                #Is this the way to go?
    if comparisons:
        ratios = [comparison["ratio"] for comparison in comparisons]
        closest = comparisons[ratios.index(min(ratios))]
        return closest
    return None

def divided_vote(votes, prior_allocations, C, P, divisor_gen):
    gen = divisor_gen()
    for seat in range(1+prior_allocations[C][P]):
        divisor = next(gen)
    return float(votes[C][P])/divisor
