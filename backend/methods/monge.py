from copy import deepcopy

def monge(
    m_votes,             #2d - votes for each list
    v_desired_row_sums,  #1d - total number of seats in each constituency
    v_desired_col_sums,  #1d - total number of seats for each party
    m_prior_allocations, #2d - seats already allocated to lists
    divisor_gen,         #divisor sequence formula
    threshold=None,
    orig_votes=None,
    **kwargs
):
    """
    # Apportion by Monge algorithm

    Inputs:
        - m_votes: A 2d matrix of votes (rows: constituencies, columns:
            parties)
        - v_desired_row_sums: A 1d vector of total seats in each constituency
        - v_desired_col_sums: A 1d vector of seats allocated to parties
        - m_prior_allocations: A 2d matrix of where parties have previously
            gotten seats
        - divisor_gen: A generator function generating divisors, e.g. d'Hondt
        - threshold: A cutoff threshold for participation, between 0 and 100.
    """
    allocations = deepcopy(m_prior_allocations)
    allocation_sequence = []
    total_seats = sum(v_desired_row_sums)
    assert(sum(v_desired_col_sums) == total_seats)
    while sum([sum(x) for x in allocations]) < total_seats:
        trivial_lists = find_trivial_seats(allocations, v_desired_col_sums, v_desired_row_sums)
        for l in trivial_lists:
            allocations[l["constituency"]][l["party"]] += l["seats"]
            allocation_sequence.append(l)
        if sum([sum(x) for x in allocations]) >= total_seats:
            break
        best = find_best_Monge_list(
            m_votes, allocations, v_desired_row_sums, v_desired_col_sums, divisor_gen
        )
        if best == None:
            # if we did not find any list now to allocate to,
            # then we won't on further iterations either
            # throw some exception perhaps?
            # TODO: Find better way to indicate this
            allocation_sequence.append({
                "reason": "Unable to determine next seat. Could not finish."
            })
            break
        #allocate seat based on best Monge ratio
        allocations[best["constituency"]][best["party"]] += 1
        allocation_sequence.append(best)
    return allocations, (allocation_sequence, print_seats)

def find_trivial_seats(allocations, p_goals, c_goals):
    num_constituencies = len(allocations)
    num_parties = len(allocations[0])
    available_constituencies = []
    for C in range(num_constituencies):
        if not constituency_full(C, c_goals, allocations):
            available_constituencies.append(C)
    if available_constituencies == []:
        return []
    hungry_parties = []
    for P in range(num_parties):
        if not party_satisfied(P, p_goals, allocations):
            hungry_parties.append(P)
    if hungry_parties == []:
        return []
    if len(available_constituencies) == 1:
        trivial_seats = []
        C = available_constituencies[0]
        c_slack = c_unclaimed(C, c_goals, allocations)
        p_slack = 0
        for P in hungry_parties:
            slack = p_unclaimed(P, p_goals, allocations)
            p_slack += slack
            trivial_seats.append({
                "constituency": C,
                "party": P,
                "seats": slack,
                "reason": "Only one constituency available.",
            })
        assert(p_slack == c_slack)
        return trivial_seats
    if len(hungry_parties) == 1:
        trivial_seats = []
        P = hungry_parties[0]
        p_slack = p_unclaimed(P, p_goals, allocations)
        c_slack = 0
        for C in available_constituencies:
            slack = c_unclaimed(C, c_goals, allocations)
            c_slack += slack
            trivial_seats.append({
                "constituency": C,
                "party": P,
                "seats": slack,
                "reason": "Only one party available.",
            })
        assert(p_slack == c_slack)
        return trivial_seats
    return [] # Multiple options, non-trivial.

def find_best_Monge_list(
    votes,       #2d - votes for each list
    allocations, #2d - seats already allocated to lists
    c_goals,     #1d - total number of seats in each constituency
    p_goals,     #1d - total number of seats each party is supposed to get
    divisor_gen  #divisor sequence formula
):
    #calculate max_Monge_ratio
    num_constituencies = len(votes)
    num_parties = len(votes[0])
    considerations = []
    for C in range(num_constituencies):
        if constituency_full(C, c_goals, allocations):
            continue #No need to consider lists that can't be given more seats
        for P in range(num_parties):
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
                "min_det": closest["det"],
                "constituency": C,
                "party": P,
                "reference_constituency": closest["reference_constituency"],
                "reference_party": closest["reference_party"],
                "ad": closest["ad"],
                "bc": closest["bc"],
                "a": closest["a"],
                "b": closest["b"],
                "c": closest["c"],
                "d": closest["d"],
            })
    if considerations:
        determinants = [conion["min_det"] for conion in considerations]
        best = considerations[determinants.index(max(determinants))]
        best["reason"] = "Maximizes comparison against closest competitor."
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
    num_constituencies = len(votes)
    num_parties = len(votes[0])
    a = divided_vote(votes, allocations, C1, P1, divisor_gen)
    comparisons = []
    for C2 in range(num_constituencies):
        if C2 == C1:
            continue #compare to lists in different constituencies only
        if constituency_full(C2, c_goals, allocations):
            continue
        for P2 in range(num_parties):
            if P2 == P1:
                continue #compare to lists for different party only
            if party_satisfied(P2, p_goals, allocations):
                continue
            # d = fully_divided_vote(
            #     votes, allocations, C2, P2, c_goals, p_goals, divisor_gen
            # )
            d = divided_vote(votes, allocations, C2, P2, divisor_gen)
            b = divided_vote(votes, allocations, C1, P2, divisor_gen)
            c = divided_vote(votes, allocations, C2, P1, divisor_gen)
            comparisons.append({
                "det": a*d-b*c,
                "ad": a*d,
                "bc": b*c,
                "a": a,
                "b": b,
                "c": c,
                "d": d,
                "reference_constituency": C2,
                "reference_party": P2
            })
    if comparisons:
        determinants = [comparison["det"] for comparison in comparisons]
        closest = comparisons[determinants.index(min(determinants))]
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









def print_seats(rules, adj_seats_info):
    # Return data to print breakdown of adjustment seat apportionment
    header = ["Adj. seat #", "Constituency", "Party", "Reason",
        "Closest comparison constituency", "Closest comparison party",
        "Monge ratio",
        # "Determinant", "ad", "bc", "a", "d", "b", "c",
    ]

    allocation_sequence = []
    seat_number = 0
    for i in range(len(adj_seats_info)):
        allocation = adj_seats_info[i]
        if "constituency" not in allocation:
            allocation_sequence.append([
                0,
                "No constituency",
                "No party",
                allocation["reason"],
            ])
            continue
        reason = allocation["reason"]
        c_idx  = allocation["constituency"]
        p_idx  = allocation["party"]
        const_name = rules["constituencies"][c_idx]["name"]
        party_name = rules["parties"       ][p_idx]
        if "min_det" in allocation:
            ref_c_idx = allocation["reference_constituency"]
            ref_p_idx = allocation["reference_party"]
            ad = allocation["ad"]
            bc = allocation["bc"]
            comparison = {
                "const_name": rules["constituencies"][ref_c_idx]["name"],
                "party_name": rules["parties"       ][ref_p_idx],
                "det": allocation["min_det"],
                "ratio": round(ad/float(bc), 4) if bc != 0 else None,
            }
            for v in ["a", "b", "c", "d", "ad", "bc"]:
                comparison[v] = allocation[v]
        else:
            comparison = {
                attr: None
                for attr in [
                    "const_name", "party_name", "det", "ratio",
                    "a", "b", "c", "d", "ad", "bc",
                ]
            }
        seats = allocation["seats"] if "seats" in allocation else 1
        for seat in range(seats):
            seat_number += 1
            allocation_sequence.append([
                seat_number,
                const_name,
                party_name,
                reason,
                comparison["const_name"],
                comparison["party_name"],
                comparison["ratio"],
                # comparison["det"],
                # comparison["ad"],
                # comparison["bc"],
                # comparison["a"],
                # comparison["d"],
                # comparison["b"],
                # comparison["c"],
            ])
    return header, allocation_sequence
