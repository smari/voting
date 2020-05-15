#coding:utf-8
from copy import deepcopy
import random

def icelandic_apportionment(
    m_votes,
    v_desired_row_sums,
    v_desired_col_sums,
    m_prior_allocations,
    divisor_gen,
    adj_seat_gen,
    threshold=None,
    orig_votes=None,
    **kwargs
):
    """
    Apportion based on Icelandic law nr. 24/2000.
    """
    m_allocations = deepcopy(m_prior_allocations)

    # 2.1.
    #   (Deila skal í atkvæðatölur samtakanna með tölu kjördæmissæta þeirra,
    #   fyrst að viðbættum 1, síðan 2, þá 3 o.s.frv. Útkomutölurnar nefnast
    #   landstölur samtakanna.)
    v_seats = [sum(x) for x in zip(*m_prior_allocations)]
    v_votes = [sum(x) for x in zip(*m_votes)]
    num_allocated = sum(v_seats)
    total_seats = sum(v_desired_row_sums)

    # 2.2.
    #   (Taka skal saman skrá um þau tvö sæti hvers framboðslista sem næst
    #   komust því að fá úthlutun í kjördæmi skv. 107. gr. Við hvert
    #   þessara sæta skal skrá hlutfall útkomutölu sætisins skv. 1. tölul.
    #   107. gr. af öllum gildum atkvæðum í kjördæminu.)
    # Create list of 2 top seats on each remaining list that almost got in.


    # 2.7.
    #   (Beita skal ákvæðum 3. tölul. svo oft sem þarf þar til lokið er
    #   úthlutun allra jöfnunarsæta, sbr. 2. mgr. 8. gr.)
    invalid = []
    seats_info = []
    adj_seat = adj_seat_gen()
    while num_allocated < total_seats:
        #if all parties are either invalid or below threshold,
        #then no more seats can be allocated
        if all(p in invalid or v_votes[p] == 0 for p in range(len(v_votes))):
            raise ValueError(f"No valid recipient of seat nr. {num_allocated+1}")

        seat = next(adj_seat)
        while seat["idx"] in invalid:
            seat = next(adj_seat)
        country_num = seat["active_votes"]
        idx = seat["idx"]

        # 2.6.
        #   (Hafi allar hlutfallstölur stjórnmálasamtaka verið numdar brott
        #   skal jafnframt fella niður allar landstölur þeirra.)

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
            #   (Þegar lokið hefur verið að úthluta jöfnunarsætum í hverju
            #   kjördæmi skv. 2. mgr. 8. gr. skulu hlutfallstölur allra
            #   lista í því kjördæmi felldar niður.)
            if sum(m_allocations[const]) == v_desired_row_sums[const]:
                v_proportions[const] = 0

        # 2.3.
        #   (Finna skal hæstu landstölu skv. 1. tölul. sem hefur ekki þegar
        #   verið felld niður. Hjá þeim stjórnmálasamtökum, sem eiga þá
        #   landstölu, skal finna hæstu hlutfallstölu lista skv. 2. tölul.
        #   og úthluta jöfnunarsæti til hans. Landstalan og hlutfallstalan
        #   skulu síðan báðar felldar niður.)

        if max(v_proportions) != 0:
            const = [j for j,k in enumerate(v_proportions)
                        if k == max(v_proportions)]
            if len(const) > 1:
                # 2.4.
                #   (Nú eru tvær eða fleiri lands- eða hlutfallstölur jafnháar
                #   þegar að þeim kemur skv. 3. tölul. og skal þá hluta um röð
                #   þeirra.)
                const = [random.choice(const)]

            m_allocations[const[0]][idx] += 1
            num_allocated += 1
            seats_info.append({
                "constituency": const[0], "party": idx,
                "reason": "Highest list share",
                "country_num": country_num,
                "list_share": v_proportions[const[0]],
            })
        else:
            invalid.append(idx)
    return m_allocations, (seats_info, print_seats)


def print_seats(rules, allocation_sequence):
    # Return data to print breakdown of adjustment seat apportionment
    header = ["Adj. seat #", "Constituency", "Party",
        "Reason", "Country number", "List share"]
    data = []
    seat_number = 0
    for allocation in allocation_sequence:
        seat_number += 1
        data.append([
            seat_number,
            rules["constituencies"][allocation["constituency"]]["name"],
            rules["parties"][allocation["party"]],
            allocation["reason"],
            round(allocation["country_num"], 1),
            "{:.3%}".format(allocation["list_share"])
        ])

    return header, data
