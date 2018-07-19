#coding:utf-8
from copy import deepcopy
from apportion import apportion1d
import random

def icelandic_apportionment(m_votes, v_const_seats, v_party_seats,
                            m_prior_allocations, divisor_gen, threshold=None,
                            orig_votes=None, **kwargs):
    """
    Apportion based on Icelandic law nr. 24/2000.
    """
    m_allocations = deepcopy(m_prior_allocations)

    # 2.1
    #       (Deila skal í atkvæðatölur samtakanna með tölu kjördæmissæta þeirra,
    #        fyrst að viðbættum 1, síðan 2, þá 3 o.s.frv. Útkomutölurnar nefnast
    #        landstölur samtakanna.)
    v_seats = [sum(x) for x in zip(*m_prior_allocations)]
    v_votes = [sum(x) for x in zip(*m_votes)]
    num_allocated = sum(v_seats)
    total_seats = sum(v_const_seats)

    # 2.2. Create list of 2 top seats on each remaining list that almost got in.
    #       (Taka skal saman skrá um þau tvö sæti hvers framboðslista sem næst
    #        komust því að fá úthlutun í kjördæmi skv. 107. gr. Við hvert
    #        þessara sæta skal skrá hlutfall útkomutölu sætisins skv. 1. tölul.
    #        107. gr. af öllum gildum atkvæðum í kjördæminu.)


    # 2.7.
    #       (Beita skal ákvæðum 3. tölul. svo oft sem þarf þar til lokið er
    #        úthlutun allra jöfnunarsæta, sbr. 2. mgr. 8. gr.)
    invalid = []
    v_last_alloc = deepcopy(v_seats)
    seats_info = []
    while num_allocated < total_seats:
        alloc, d = apportion1d(v_votes, num_allocated+1, v_last_alloc, divisor_gen, invalid)
        # 2.6.
        #       (Hafi allar hlutfallstölur stjórnmálasamtaka verið numdar brott
        #        skal jafnframt fella niður allar landstölur þeirra.)

        diff = [alloc[j]-v_last_alloc[j] for j in range(len(alloc))]
        idx = diff.index(1)

        v_proportions = []
        for const in range(len(m_votes)):
            const_votes = orig_votes[const]
            s = sum(const_votes)
            div = divisor_gen()
            for i in range(m_allocations[const][idx]+1):
                x = next(div)
            p = (float(const_votes[idx])/s)/x
            v_proportions.append(p)

            # 2.5.
            #       (Þegar lokið hefur verið að úthluta jöfnunarsætum í hverju
            #        kjördæmi skv. 2. mgr. 8. gr. skulu hlutfallstölur allra
            #        lista í því kjördæmi felldar niður.)
            if sum(m_allocations[const]) == v_const_seats[const]:
                v_proportions[const] = 0

        # 2.3.
        #       (Finna skal hæstu landstölu skv. 1. tölul. sem hefur ekki þegar
        #        verið felld niður. Hjá þeim stjórnmálasamtökum, sem eiga þá
        #        landstölu, skal finna hæstu hlutfallstölu lista skv. 2. tölul.
        #        og úthluta jöfnunarsæti til hans. Landstalan og hlutfallstalan
        #        skulu síðan báðar felldar niður.)

        if max(v_proportions) != 0:
            const = [j for j,k in enumerate(v_proportions) if k == max(v_proportions)]
            if len(const) > 1:
                # 2.4.
                #       (Nú eru tvær eða fleiri lands- eða hlutfallstölur jafnháar
                #        þegar að þeim kemur skv. 3. tölul. og skal þá hluta um röð
                #        þeirra.)
                const = [random.choice(const)]

            m_allocations[const[0]][idx] += 1
            num_allocated += 1
            v_last_alloc = alloc
            seats_info.append((const[0], d[2], idx,
                                v_proportions[const[0]]))
        else: 
            invalid.append(idx)
    return m_allocations, seats_info


def print_seats(rules, adj_seats_info):
    # Return data to print breakdown of adjustment seat apportionment
    header = ["Adjustment seat number", "Constituency", "Country number",
                "Party", "List share"]
    data = []
    for i in range(len(adj_seats_info)):
        data.append([i+1, rules["constituencies"][adj_seats_info[i][0]]["name"],
                    adj_seats_info[i][1], rules["parties"][adj_seats_info[i][2]],
                    "{:.3%}".format(adj_seats_info[i][3])])

    return header, data