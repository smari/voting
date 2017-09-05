#coding:utf-8
"""
This module contains the core voting system logic.
"""
import random
import json
from copy import copy, deepcopy
from math import log
from tabulate import tabulate
from util import load_votes, load_constituencies
from rules import Rules
from simulate import SimulationRules # TODO: This belongs elsewhere.

def dhondt_gen():
    """Generate a d'Hondt divider sequence: 1, 2, 3..."""
    n = 1
    while True:
        yield n
        n += 1

def sainte_lague_gen():
    """Generate a Sainte-Lague divider sequence: 1, 3, 5..."""
    n = 1
    while True:
        yield n
        n += 2

def swedish_sainte_lague_gen():
    """Generate a Swedish/Nordic Sainte-Lague divide sequence: 1.4, 3, 5..."""
    yield 1.4
    n = 3
    while True:
        yield n
        n += 2

DIVIDER_RULES = {
    "dhondt": dhondt_gen,
    "sainte-lague": sainte_lague_gen,
    "swedish": swedish_sainte_lague_gen
}

DIVIDER_RULE_NAMES = {
    "dhondt": "D'Hondt's method",
    "sainte-lague": "Sainte-Laguë method",
    "swedish": "Nordic Sainte-Laguë variant"
}


class ElectionRules(Rules):
    """A set of rules for an election or a simulation to follow."""

    def __init__(self):
        super(ElectionRules, self).__init__()
        self.value_rules = {
            "primary_divider": DIVIDER_RULES.keys(),
            "adjustment_divider": DIVIDER_RULES.keys(),
            "adjustment_method": ADJUSTMENT_METHODS.keys(),
            "simulation_variate": SIMULATION_VARIATES.keys(),
        }
        self.range_rules = {
            "adjustment_threshold": [0.0, 1.0]
        }
        self.list_rules = [
            "constituency_seats", "constituency_adjustment_seats",
            "constituency_names", "parties"
        ]

        # Election rules
        self["primary_divider"] = "dhondt"
        self["adjustment_divider"] = "dhondt"
        self["adjustment_threshold"] = 0.05
        self["adjustment_method"] = "icelandic-law"
        self["constituency_seats"] = []
        self["constituency_adjustment_seats"] = []
        self["constituency_names"] = []
        self["parties"] = []

        # Display rules
        self["debug"] = False
        self["show_entropy"] = False
        self["output"] = "simple"

    def __setitem__(self, key, value):
        if key == "constituencies":
            value = load_constituencies(value)
            self["constituency_names"] = [x["name"] for x in value]
            self["constituency_seats"] = [x["num_constituency_seats"]
                                          for x in value]
            self["constituency_adjustment_seats"] = [x["num_adjustment_seats"]
                                                     for x in value]

        super(ElectionRules, self).__setitem__(key, value)

    def get_generator(self, div):
        """Fetch a generator from divider rules."""
        method = self[div]
        if method in DIVIDER_RULES.keys():
            return DIVIDER_RULES[method]
        else:
            raise ValueError("%s is not a known divider" % div)


class Election:
    """A single election."""
    def __init__(self, rules, votes=None):
        self.m_votes = votes
        self.rules = rules
        self.order = []
        self.log = []

    def set_votes(self, votes):
        assert(len(votes) == len(self.rules["constituencies"]))
        assert(all([len(votes[x]) == len(self.rules["parties"])
                    for x in votes]))
        self.m_votes = votes

    def load_votes(self, votesfile):
        parties, votes = load_votes(votesfile)
        self.rules["parties"] = parties
        assert(len(votes) == len(self.rules["constituencies"]))
        assert(all([len(votes[x]) == len(self.rules["parties"])
                    for x in votes]))
        self.m_votes = votes
        self.v_parties = parties

    def get_results_dict(self):
        return {
            "rules": self.rules,
            "seat_allocations": self.results,
        }

    def run(self):
        """Run an election based on current rules and votes."""
        # How many seats does each party get in each constituency:
        self.m_allocations = []
        # Which seats does each party get in each constituency:
        self.m_seats = []
        # Determine total seats (const + adjustment) in each constituency:
        self.v_total_seats = [sum(x) for x in
                              zip(self.rules["constituency_seats"],
                                  self.rules["constituency_adjustment_seats"])
                             ]
        # Determine total seats in play:
        self.total_seats = sum(self.v_total_seats)

        self.run_primary_apportionment()
        self.run_threshold_elimination()
        self.run_determine_adjustment_seats()
        self.run_adjustment_apportionment()
        return self.results

    def run_primary_apportionment(self):
        """Conduct primary apportionment"""
        if self.rules["debug"]:
            print(" + Primary apportionment")
        m_allocations, v_seatcount = self.primary_apportionment(self.m_votes)
        self.m_allocations = m_allocations
        self.v_cur_allocations = v_seatcount

    def run_threshold_elimination(self):
        if self.rules["debug"]:
            print(" + Threshold elimination")
        threshold = self.rules["adjustment_threshold"]
        v_elim_votes = threshold_elimination_totals(self.m_votes, threshold)
        m_elim_votes = threshold_elimination_constituencies(self.m_votes,
                                                            threshold)
        self.v_votes_eliminated = v_elim_votes
        self.m_votes_eliminated = m_elim_votes

    def run_determine_adjustment_seats(self):
        """
        Calculate the number of adjusment seats each party gets.
        """
        if self.rules["debug"]:
            print(" + Determine adjustment seats")
        v_votes = self.v_votes_eliminated
        gen = self.rules.get_generator("adjustment_divider")
        v_priors = self.v_cur_allocations
        v_seats, divs = apportion1d(v_votes, self.total_seats, v_priors, gen)
        self.v_adjustment_seats = v_seats
        return v_seats

    def run_adjustment_apportionment(self):
        if self.rules["debug"]:
            print(" + Apportion adjustment seats")
        method = ADJUSTMENT_METHODS[self.rules["adjustment_method"]]
        gen = self.rules.get_generator("adjustment_divider")

        results = method(self.m_votes_eliminated,
                         self.v_total_seats,
                         self.v_adjustment_seats,
                         self.m_allocations,
                         gen,
                         self.rules["adjustment_threshold"],
                         orig_votes=self.m_votes)

        self.results = results

        # header = ["Constituency"]
        # header.extend(self.rules["parties"])
        # print "\n=== %s ===" %
        #    (ADJUSTMENT_METHOD_NAMES[self.rules["adjustment_method"]])
        # data = [[self.rules["constituency_names"][c]]+results[c] for c in
        #         range(len(self.rules["constituency_names"]))]
        # print tabulate(data, header, "simple")

        if self.rules["show_entropy"]:
            ent = entropy(self.m_votes, results, gen)
            print("\nEntropy: ", ent)

    def primary_apportionment(self, m_votes):
        """Do primary allocation of seats for all constituencies"""
        gen = self.rules.get_generator("primary_divider")
        const = self.rules["constituency_seats"]
        parties = self.rules["parties"]

        m_allocations = []
        for i in range(len(const)):
            num_seats = const[i]
            rounds, seats = constituency_seat_allocation(m_votes[i], num_seats,
                                                         gen)
            v_allocations = [seats.count(p) for p in range(len(parties))]
            m_allocations.append(v_allocations)
            self.order.append(seats)

        # Useful:
        # print tabulate([[parties[x] for x in y] for y in self.order])

        v_seatcount = [sum([x[i] for x in m_allocations]) for i in range(len(parties))]

        return m_allocations, v_seatcount


def primary_seat_allocation(m_votes, const, parties, gen):
    """Do primary allocation of seats for all constituencies"""
    m_allocations = []
    for i in range(len(const)):
        s = const[i]["num_constituency_seats"]
        rounds, seats = constituency_seat_allocation(m_votes[i], s, gen)
        named_seats = [parties[x] for x in seats]
        v_allocations = [seats.count(p) for p in range(len(parties))]
        # print "%-20s: %s" % (const[i]["name"], ", ".join(named_seats))
        m_allocations.append(v_allocations)

    v_seatcount = [sum([x[i] for x in m_allocations]) for i in range(len(parties))]

    return m_allocations, v_seatcount


def constituency_seat_allocation(v_votes, num_seats, gen):
    """Do primary seat allocation for one constituency"""
    # FIXME: This should use apportion1d() instead
    rounds = []
    seats = []
    alloc_votes = copy(v_votes)
    gens = [gen() for x in range(len(v_votes))]
    divisors = [next(x) for x in gens]

    for i in range(num_seats):
        maxval = max(alloc_votes)
        idx = alloc_votes.index(maxval)
        res = {
            "maxval": maxval,
            "votes": alloc_votes,
            "winner": idx,
            "divisor": divisors[idx]
        }
        seats.append(idx)
        rounds.append(res)
        divisors[idx] = next(gens[idx])
        alloc_votes[idx] = v_votes[idx] / divisors[idx]

    return rounds, seats


def threshold_elimination_constituencies(votes, threshold, party_seats=None, priors=None):
    """
    Eliminate parties that don't reach national threshold.
    Optionally, eliminate parties that have already gotten all their
    calculated seats.

    Inputs:
        - votes: Matrix of votes.
        - threshold: Real value between 0.0 and 1.0 with the cutoff threshold.
        - [party_seats]: seats that should be allocated to each party
        - [priors]: a matrix of prior allocations to each party per constituency
    Returns: Matrix of votes with eliminated parties zeroed out.
    """
    N = len(votes[0])
    totals = [sum([x[i] for x in votes]) for i in range(N)]
    country_total = sum(totals)
    percent = [float(t)/country_total for t in totals]
    m_votes = []

    for c in votes:
        cons = []
        for i in range(N):
            if percent[i] > threshold:
                v = c[i]
            else:
                v = 0
            cons.append(v)
        m_votes.append(cons)

    if not (priors and party_seats):
        return m_votes

    for j in range(N):
        if party_seats[j] == sum([m[j] for m in priors]):
            for i in range(len(votes)):
                m_votes[i][j] = 0

    return m_votes

def threshold_elimination_totals(votes, threshold):
    """
    Eliminate parties that do not reach the threshold proportion of
    national votes. Replaces such parties with zeroes.
    """
    N = len(votes[0])
    totals = [sum([x[i] for x in votes]) for i in range(N)]
    country_total = sum(totals)
    percent = [float(t)/country_total for t in totals]
    cutoff = [totals[i] if percent[i] > threshold else 0 for i in range(len(totals))]

    return cutoff


def apportion1d(v_votes, num_total_seats, prior_allocations, divisor_gen):
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
    N = len(v_votes)
    divisor_gens = [divisor_gen() for x in range(N)]
    divisors = []
    for n in range(N):
        for j in range(prior_allocations[n]+1):
            x = next(divisor_gens[n])
        divisors.append(x)

    allocations = copy(prior_allocations)

    num_preallocated_seats = sum(prior_allocations)
    min_used = 1000000
    for j in range(num_total_seats-num_preallocated_seats):
        divided_votes = [float(v_votes[i])/divisors[i]
                         if v_votes[i] is not None else None
                         for i in range(N)]
        maxvote = max(divided_votes)
        min_used = maxvote
        maxparty = divided_votes.index(maxvote)
        divisors[maxparty] = next(divisor_gens[maxparty])
        allocations[maxparty] += 1

    return allocations, (divisors, divisor_gens, min_used)


def alternating_scaling(m_votes, v_const_seats, v_party_seats,
                        m_prior_allocations, divisor_gen, threshold, **kwargs):
    """
    # Implementation of the Alternating-Scaling algorithm.

    Inputs:
        - m_votes_orig: A matrix of votes (rows: constituencies, columns:
          parties)
        - v_const_seats: A vector of constituency seats
        - v_party_seats: A vector of seats allocated to parties
        - m_prior_allocations: A matrix of where parties have previously gotten
          seats
        - divisor_gen: A generator function generating divisors, e.g. d'Hondt
        - threshold: A cutoff threshold for participation.
    """

    def const_step(v_votes, const_id, v_const_multipliers, v_party_multipliers):
        num_total_seats = v_const_seats[const_id]
        cm = const_multiplier = v_const_multipliers[const_id]
        # See IV.3.5 in paper:
        v_scaled_votes = [a/(b*cm) if b*cm != 0 else 0
                          for a, b in zip(v_votes, v_party_multipliers)]

        v_priors = m_prior_allocations[const_id]

        alloc, div = apportion1d(v_scaled_votes, num_total_seats,
                                 v_priors, divisor_gen)

        # See IV.3.9 in paper:
        minval = div[2] # apportion1d gives us the last used value, which is min
        maxval = max([float(a)/b if a is not 0 and a is not None else 0
                      for a, b in zip(v_scaled_votes, div[0])])
        const_multiplier = (minval+maxval)/2

        # TODO: Make pretty-print intermediate tables on --debug
        # Results -- kind of
        #print "Constituency %d" % (const_id)
        #print " - Divisors: ", div[0]
        #print " - Scaled: ", v_scaled_votes
        #print " - Min: ", minval
        #print " - Max: ", maxval
        #print " - New const multiplier: ", const_multiplier
        #print " - Allocations: ", alloc
        return alloc, const_multiplier

    def party_step(v_votes, party_id, v_const_multipliers, v_party_multipliers):
        num_total_seats = v_party_seats[party_id]
        pm = party_multiplier = v_party_multipliers[party_id]
        #
        v_scaled_votes = [a/(b*pm) if b != 0 else None
                          for a, b in zip(v_votes, v_const_multipliers)]

        v_priors = [m_prior_allocations[x][party_id]
                    for x in range(len(m_prior_allocations))]

        alloc, div = apportion1d(v_scaled_votes, num_total_seats, v_priors,
                                 divisor_gen)

        minval = div[2]
        maxval = max([float(a)/b if a is not None else 0
                      for a, b in zip(v_scaled_votes, div[0])])
        party_multiplier = (minval+maxval)/2

        # TODO: Make pretty-print intermediate tables on --debug
        #print "Party %d" % (party_id)
        #print " - Divisors: ", div[0]
        #print " - Scaled: ", v_scaled_votes
        #print " - Min: ", minval
        #print " - Max: ", maxval
        #print " - New const multiplier: ", party_multiplier
        #print " - Allocations: ", alloc

        return alloc, party_multiplier

    num_constituencies = len(m_votes)
    num_parties = len(m_votes[0])
    const_multipliers = [1] * num_constituencies
    party_multipliers = [1] * num_parties
    step = 0

    const_done = False
    party_done = False
    while step < 200:
        step += 1
        if step % 2 == 1:
            #Constituency step:
            muls = []
            for c in range(num_constituencies):
                alloc, mul = const_step(m_votes[c], c, const_multipliers,
                                        party_multipliers)
                const_multipliers[c] *= mul
                muls.append(mul)
            const_done = all([round(x, 5) == 1.0 or x == 500000 for x in muls])
        else:
            # print "== Party step %d ==" % step
            muls = []
            for p in range(num_parties):
                vp = [v[p] for v in m_votes]
                alloc, mul = party_step(vp, p, const_multipliers, party_multipliers)
                party_multipliers[p] *= mul
                muls.append(mul)
            party_done = all([round(x, 5) == 1.0 or x == 500000 for x in muls])

        if const_done and party_done:
            break

    # Finally, use party_multipliers and const_multipliers to arrive at
    #  final apportionment:
    results = []
    for c in range(num_constituencies):
        num_total_seats = v_const_seats[c]
        cm = const_multipliers[c]
        v_scaled_votes = [a/(b*cm) if b != 0 else None
                          for a, b in zip(m_votes[c], party_multipliers)]
        v_priors = m_prior_allocations[c]
        alloc, div = apportion1d(v_scaled_votes, num_total_seats,
                                 v_priors, divisor_gen)
        results.append(alloc)

    return results


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


def relative_inferiority(m_votes, v_const_seats, v_party_seats,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """
    Apportion by Þorkell Helgason's Relative Inferiority method.
    This method is incomplete.
    """
    m_allocations = copy(m_prior_allocations)
    m_max_seats = [[min(Ci, Pj) for Pj in v_party_seats]
                   for Ci in v_const_seats]
    # Probably not needed:
    const_filled = [False] * len(v_const_seats)
    party_filled = [False] * len(v_party_seats)

    # num_allocated =
    for i in range(10):
        for i in range(len(v_const_seats)):
            app = apportion1d(m_votes[i], 10, m_allocations[i], divisor_gen)

    return m_allocations

def monge(m_votes, v_constituency_seats,
                         m_prior_allocations, divisor_gen, threshold=None,
                         **kwargs):
    """Apportion by Monge algorithm"""

    def divided_vote(m_votes, m_prior_allocations, constituency, party, divisor_gen):
        gen = divisor_gen()
        for seat in range(1+sum([v_constituency_allocations[party]
                                for v_constituency_allocations in m_prior_allocations])):
            divisor = next(gen)
        return float(m_votes[constituency][party])/divisor

    m_allocations = deepcopy(m_prior_allocations)
    total_seats = sum(v_constituency_seats)
    allocated_seats = sum([sum(x) for x in m_allocations])
    for seat in range(total_seats - allocated_seats):
        #calculate max_Monge_ratio
        max_Monge_ratio = 0
        for constituency in range(len(m_votes)):
            for party in range(len(m_votes[0])):
                a = divided_vote(m_votes, m_allocations, constituency, party, divisor_gen)
                min_ratio = 1
                none_found = True
                for other_constituency in range(len(m_votes)):
                    if other_constituency == constituency:
                        continue
                    for other_party in range(len(m_votes[0])):
                        if other_party == party:
                            continue
                        d = divided_vote(m_votes, m_allocations, other_constituency, other_party, divisor_gen)
                        b = divided_vote(m_votes, m_allocations, constituency, other_party, divisor_gen)
                        c = divided_vote(m_votes, m_allocations, other_constituency, party, divisor_gen)
                        ratio = (a*d)/(b*c)
                        if none_found or ratio < min_ratio:
                            min_ratio = ratio
                            reference_constituency = other_constituency
                            reference_party = other_party
                            none_found = False
                if min_ratio > max_Monge_ratio:
                    max_Monge_ratio = min_ratio
                    max_constituency = constituency
                    max_party = party

        #allocate seat based on Monge ratio
        m_allocations[max_constituency][max_party] += 1

    return m_allocations

def entropy(votes, allocations, divisor_gen):
    """
    Calculate entropy of the election, taking into account votes and
     allocations.
     $\\sum_i \\sum_j \\sum_k \\log{v_{ij}/d_k}$, more or less.
    """
    e = 0
    for i in range(len(votes)):
        divisor_gens = [divisor_gen() for x in range(len(votes[0]))]
        for j in range(len(votes[0])):
            for k in range(allocations[i][j]):
                dk = next(divisor_gens[j])
                e += log(votes[i][j]/dk)
    return e


ADJUSTMENT_METHODS = {
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "relative-inferiority": relative_inferiority,
    "monge": monge,
    "icelandic-law": icelandic_apportionment,
}

ADJUSTMENT_METHOD_NAMES = {
    "alternating-scaling": "Alternating-Scaling Method",
    "relative-superiority": "Relative Superiority Method",
    "relative-inferiority": "Relative Inferiority Method",
    "monge": "Monge algorithm",
    "icelandic-law": "Icelandic law 24/2000 (Kosningar til Alþingis)"
}

class Variate:
    def __init__(self, election):
        self.election = election

    def step(index):
        pass


class VariateBeta(Variate):
    pass


class VariateBruteforce(Variate):
    pass


SIMULATION_VARIATES = {
    "beta": VariateBeta,
    "bruteforce": VariateBruteforce,
}

# TODO: These functions should be elsewhere.

def get_capabilities_dict():
    return {
        "election_rules": ElectionRules(),
        "simulation_rules": SimulationRules(),
        "capabilities": {
            "divider_rules": DIVIDER_RULE_NAMES,
            "adjustment_methods": ADJUSTMENT_METHOD_NAMES,
        },
        "presets": get_presets()
    }

def get_presets():
    from os import listdir
    from os.path import isfile, join
    presetsdir = "../data/presets/"
    try:
        files = [f for f in listdir(presetsdir) if isfile(join(presetsdir, f))]
    except Exception as e:
        print("Presets directory read failure: %s" % (e))
        files = []
    pr = []
    for f in files:
        # TODO: Needs sanity checking!
        pr.append(io.open(presetsdir+f).read())
    return pr

def run_script(rules):
    if type(rules) != dict:
        return {"error": "Incorrect script format."}

    if rules["action"] not in ["simulation", "election"]:
        return {"error": "Script action must be election or simulation."}

    if rules["action"] == "election":
        rs = ElectionRules()
        if "election_rules" not in rules:
            return {"error": "No election rules supplied."}

        rs.update(rules["election_rules"])

        if not "votes" in rs:
            return {"error": "No votes supplied"}

        election = Election(rs, rs["votes"])
        election.run()

        return election

    else:
        return {"error": "Not implemented."}


if __name__ == "__main__":
    pass
