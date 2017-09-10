#coding:utf-8

def relative_superiority(m_votes, v_const_seats, v_party_seats,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """Apportion by Þorkell Helgason's Relative Superiority method"""

    m_allocations = deepcopy(m_prior_allocations)
    num_preallocated_seats = sum([sum(x) for x in m_allocations])
    num_total_seats = sum(v_const_seats)
    for n in range(num_total_seats-num_preallocated_seats):
        m_votes = threshold_elimination_constituencies(m_votes, 0.0, v_party_seats, m_allocations)
        superiority = []
        firstin = []
        for j in range(len(m_votes)):
            seats_left = v_const_seats[j] - sum(m_allocations[j])
            if not seats_left:
                superiority.append(0)
                firstin.append(0)
                continue

            next_alloc_num = sum(m_allocations[j]) + 1
            app_next = apportion1d(m_votes[j], next_alloc_num,
                                   m_allocations[j], divisor_gen)
            change = [0 if app_next[0][i] == m_allocations[j][i] else 1
                      for i in range(len(m_votes[j]))]
            nextin = change.index(1)
            new_votes = copy(m_votes[j])
            new_votes[nextin] = app_next[0][2]
            firstin.append(nextin)
            # Create a provisional allocation where nextin gets the seat:
            v_prov_allocations = copy(m_allocations[j])
            v_prov_allocations[nextin] += 1
            # Calculate continuation:
            app_after = apportion1d(new_votes, v_const_seats[j]+1, v_prov_allocations, divisor_gen)

            # Calculate relative superiority
            try:
                rs = float(app_next[1][2])/app_after[1][2]
            except ZeroDivisionError:
                rs = 0
            superiority.append(rs)

        greatest = max(superiority)
        idx = superiority.index(greatest)
        m_allocations[idx][firstin[idx]] += 1

    return m_allocations
