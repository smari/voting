#coding:utf-8
from copy import deepcopy
from apportion import apportion1d


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
    num_missing = sum(v_const_seats) - num_allocated

    # 2.2. Create list of 2 top seats on each remaining list that almost got in.
    #       (Taka skal saman skrá um þau tvö sæti hvers framboðslista sem næst
    #        komust því að fá úthlutun í kjördæmi skv. 107. gr. Við hvert
    #        þessara sæta skal skrá hlutfall útkomutölu sætisins skv. 1. tölul.
    #        107. gr. af öllum gildum atkvæðum í kjördæminu.)


    # 2.7.
    #       (Beita skal ákvæðum 3. tölul. svo oft sem þarf þar til lokið er
    #        úthlutun allra jöfnunarsæta, sbr. 2. mgr. 8. gr.)
    v_last_alloc = deepcopy(v_seats)
    for i in range(num_allocated+1, num_allocated+num_missing+1):
        alloc, div = apportion1d(v_votes, i, v_last_alloc, divisor_gen)
        # 2.6.
        #       (Hafi allar hlutfallstölur stjórnmálasamtaka verið numdar brott
        #        skal jafnframt fella niður allar landstölur þeirra.)

        diff = [alloc[i]-v_last_alloc[i] for i in range(len(alloc))]
        idx = diff.index(1)
        v_last_alloc = alloc

        m_proportions = []
        for cons in range(len(m_votes)):
            cons_votes = orig_votes[cons]
            s = sum(cons_votes)
            proportions = []
            for party in range(len(m_votes[0])):
                d = divisor_gen()
                for j in range(m_allocations[cons][party]+1):
                    x = next(d)
                k = (float(orig_votes[cons][party])/s)/x
                proportions.append(k)

            m_proportions.append(proportions)

            # 2.5.
            #       (Þegar lokið hefur verið að úthluta jöfnunarsætum í hverju
            #        kjördæmi skv. 2. mgr. 8. gr. skulu hlutfallstölur allra
            #        lista í því kjördæmi felldar niður.)
            if sum(m_allocations[cons]) == v_const_seats[cons]:
                # print "Done allocating in constituency %d" % (cons)
                m_proportions[cons] = [0]*len(v_seats)

        # 2.3.
        #       (Finna skal hæstu landstölu skv. 1. tölul. sem hefur ekki þegar
        #        verið felld niður. Hjá þeim stjórnmálasamtökum, sem eiga þá
        #        landstölu, skal finna hæstu hlutfallstölu lista skv. 2. tölul.
        #        og úthluta jöfnunarsæti til hans. Landstalan og hlutfallstalan
        #        skulu síðan báðar felldar niður.)

        w = [m_proportions[i][idx] for i in range(len(m_proportions))]
        # print "Proportions for %d: %s" % (idx, w)
        const = [i for i,j in enumerate(w) if j == max(w)]
        if len(const) > 1:
            # 2.4.
            #       (Nú eru tvær eða fleiri lands- eða hlutfallstölur jafnháar
            #        þegar að þeim kemur skv. 3. tölul. og skal þá hluta um röð
            #        þeirra.)
            const = [random.choice(const)]

        m_allocations[const[0]][idx] += 1
    return m_allocations
