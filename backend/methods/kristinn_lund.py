from apportion import apportion1d
import heapq

def kristinn_lund(m_votes, v_desired_row_sums, v_desired_col_sums, m_prior_allocations,
    divisor_gen, threshold=None, orig_votes=None, **kwargs):

    v_prior_allocations = [sum([c[p] for c in m_prior_allocations])
                           for p in range(len(v_desired_col_sums))]
    # The number of adjustment seats each party should receive:
    correct_adj_seats = [v_desired_col_sums[p]-v_prior_allocations[p]
                        for p in range(len(v_desired_col_sums))]

    # Allocate adjustment seats as if they were constituency seats
    m_adj_seats = []
    for c in range(len(m_prior_allocations)):
        votes = [m_votes[c][p] if correct_adj_seats[p] > 0 else 0
                for p in range(len(m_votes[c]))]
        alloc, div = apportion1d(votes, v_desired_row_sums[c],
                    m_prior_allocations[c], divisor_gen)
        adj_seats = [alloc[p]-m_prior_allocations[c][p]
                    for p in range(len(alloc))]
        m_adj_seats.append(adj_seats)

    # Transfer adjustment seats within constituencies from parties that have
    #  too many seats to parties that have too few seats, prioritized by
    #  "sensitivity", until all parties have the correct number of seats
    #  or no more swaps can be made:

    done = False
    while not done:
        v_adj_seats = [sum([c[p] for c in m_adj_seats])
                        for p in range(len(m_adj_seats[0]))]
        diff_party = [v_adj_seats[p]-correct_adj_seats[p]
                        for p in range(len(v_adj_seats))]

        over = [i for i in range(len(diff_party)) if diff_party[i] > 0]
        under = [i for i in range(len(diff_party)) if diff_party[i] < 0]
        sensitivity = []
        for i in range(len(m_votes)):
            for j in over:
                for k in under:
                    if m_adj_seats[i][j] != 0 and m_votes[i][k] != 0:
                        gen_j = divisor_gen()
                        for x in range(m_prior_allocations[i][j]+m_adj_seats[i][j]):
                            div_j = next(gen_j)
                        gen_k = divisor_gen()
                        for x in range(m_prior_allocations[i][k]+m_adj_seats[i][k]+1):
                            div_k = next(gen_k)
                        s = (m_votes[i][j]/div_j) / (m_votes[i][k]/div_k)
                        heapq.heappush(sensitivity, (s,(i,j,k)))

        done = len(sensitivity) == 0
        if not done:
            # Find the constituency and pair of parties with the lowest
            #  sensitivity, and transfer a seat:
            i, j, k = heapq.heappop(sensitivity)[1]
            m_adj_seats[i][j] -= 1
            m_adj_seats[i][k] += 1

    m_allocations = [[m_prior_allocations[c][p]+m_adj_seats[c][p]
                        for p in range(len(m_adj_seats[c]))]
                        for c in range(len(m_adj_seats))]


    return m_allocations, None
