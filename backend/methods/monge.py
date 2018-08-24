from copy import deepcopy

def monge(
    m_votes,
    v_total_seats,
    v_party_seats,
    m_prior_allocations,
    divisor_gen,
    threshold=None,
    orig_votes=None,
    **kwargs
):
    """Apportion by Monge algorithm"""
    m_allocations = deepcopy(m_prior_allocations)
    total_seats = sum(v_total_seats)
    while sum([sum(x) for x in m_allocations]) < total_seats:
        best = find_best_Monge_list(
            m_votes, m_allocations, v_total_seats, v_party_seats, divisor_gen
        )
        if best == None:
            # if we did not find any list to allocate to now,
            # then we also won't on next iteration
            # throw some exception perhaps?
            return m_allocations, "Adjustment seat allocation incomplete."
        m_allocations[best["constituency"]][best["party"]] += 1
    return m_allocations, None

def find_best_Monge_list(
    votes,
    allocations,
    total_seats,
    party_seats,
    divisor_gen
):
    #calculate max_Monge_ratio
    no_constituencies = len(votes)
    no_parties = len(votes[0])
    considerations = []
    for C in range(no_constituencies):
        if no_seats_left_for_constituency(C, total_seats, allocations):
            continue
        for P in range(no_parties):
            if no_seats_left_for_party(P, party_seats, allocations):
                continue
            closest = find_closest_comparison(
                C, P, votes, allocations, divisor_gen
            )
            if closest == None:
                # do not append, ignore list if there is no valid comparison
                continue
            considerations.append({
                "min_ratio": closest["ratio"],
                "constituency": C,
                "party": P,
                "reference_constituency": closest["reference_constituency"],
                "reference_party": closest["reference_party"]
            })
    if considerations:
        ratios = [consideration["min_ratio"] for consideration in considerations]
        best = considerations[ratios.index(max(ratios))]
        return best
    return None

def no_seats_left_for_party(party, v_party_seats, m_allocations):
    seats_left = v_party_seats[party] - sum([c[party] for c in m_allocations])
    return seats_left <= 0

def no_seats_left_for_constituency(constituency, v_total_seats, m_allocations):
    seats_left = v_total_seats[constituency] - sum(m_allocations[constituency])
    return seats_left <= 0

def find_closest_comparison(
    C1,
    P1,
    votes,
    allocations,
    total_seats,
    party_seats,
    divisor_gen
):
    no_constituencies = len(votes)
    no_parties = len(votes[0])
    a = divided_vote(votes, allocations, C1, P1, divisor_gen)
    comparisons = []
    for C2 in range(no_constituencies):
        if C2 == C1:
            continue
        if no_seats_left_for_constituency(C2, total_seats, allocations):
            continue
        for P2 in range(no_parties):
            if P2 == P1:
                continue
            if no_seats_left_for_party(P2, party_seats, allocations):
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
    if comparisons:
        ratios = [comparison["ratio"] for comparison in comparisons]
        closest = comparisons[ratios.index(min(ratios))]
        return closest
    return None

def divided_vote(votes, prior_allocations, c, p, divisor_gen):
    gen = divisor_gen()
    for seat in range(1+sum([constituency_allocations[p]
                            for constituency_allocations in prior_allocations])):
        divisor = next(gen)
    return float(votes[c][p])/divisor
