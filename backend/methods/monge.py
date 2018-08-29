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
            if list_unsupported(votes, C, P):
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

def constituency_full(C, c_goals, allocations):
    return c_unclaimed(C, c_goals, allocations) <= 0

def party_satisfied(P, p_goals, allocations):
    return p_unclaimed(P, p_goals, allocations) <= 0

def list_unsupported(votes, C, P):
    return votes[C][P] <= 0

def c_unclaimed(C, c_goals, allocations):
    return c_goals[C] - sum(allocations[C])

def p_unclaimed(P, p_goals, allocations):
    return p_goals[P] - sum([c[P] for c in allocations])

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
            continue
        for P2 in range(no_parties):
            if P2 == P1:
                continue #compare to lists for different party only
            if party_satisfied(P2, p_goals, allocations):
                continue
            d = fully_divided_vote(
                votes, allocations, C2, P2, c_goals, p_goals, divisor_gen
            )
            # d = divided_vote(votes, allocations, C2, P2, divisor_gen)
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
            #TODO: Finish this thought:
            #we are already assuming a>0
            # elif b == 0 or c == 0:
            #     if d > 0:
            #         include = False
            #     else:
            #         if b == 0 and c == 0:
            #             include = False
            #         else:
            #             ratio = a/(max(b,c))
            #             include = True
            # else:
            #     ratio = (a*d)/(b*c)
            #     include = True
            # if include:
            #     comparisons.append({
            #         "ratio": ratio,
            #         "reference_constituency": C2,
            #         "reference_party": P2
            #     })
    if comparisons:
        ratios = [comparison["ratio"] for comparison in comparisons]
        closest = comparisons[ratios.index(min(ratios))]
        return closest
    return None

def divided_vote(votes, prior_allocations, C, P, divisor_gen):
    k = prior_allocations[C][P]
    return float(votes[C][P]) / divisor(k, divisor_gen)

def divisor(k, divisor_gen):
    gen = divisor_gen()
    d = next(gen)
    for step in range(k):
        d = next(gen)
    return d

def fully_divided_vote(votes, allocations, C, P, c_goals, p_goals, divisor_gen):
    slack = seats_still_available(C, P, c_goals, p_goals, allocations)
    N = allocations[C][P] + slack
    return float(votes[C][P]) / divisor(N, divisor_gen)

def seats_still_available(C, P, c_goals, p_goals, allocations):
    c_left = c_unclaimed(C, c_goals, allocations)
    p_left = p_unclaimed(P, p_goals, allocations)
    return min(c_left, p_left)
