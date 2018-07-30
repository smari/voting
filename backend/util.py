#coding:utf-8
import random
from backports import csv
from math import log, sqrt
import sys #??????
import tabulate
import io
import xlsxwriter
import openpyxl
from copy import deepcopy, copy
import configparser

from methods import var_alt_scal, alternating_scaling, icelandic_law
from methods import monge, relative_inferiority, relative_superiority
from methods import norwegian_law, norwegian_icelandic
from methods import opt_entropy, kristinn_lund

#??????
def random_id(length=8):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'
    s = "".join(random.sample(chars, length))
    return s


def read_csv(filename):
    with io.open(filename, mode="r", newline='', encoding='utf-8') as f:
        for row in csv.reader(f, skipinitialspace=True):
            yield [cell for cell in row]

def read_xlsx(filename):
    book = openpyxl.load_workbook(filename)
    sheet = book.active
    m_votes = []
    for row in sheet.rows:
        yield [cell.value for cell in row]

def load_constituencies(confile):
    if confile.endswith("csv"):
        reader = read_csv(confile)
    else:
        reader = read_xlsx(confile)
    cons = []
    for row in reader:
        try:
            assert(sum([int(x) for x in row[1:3]]) >= 0)
        except Exception as e:
            print(row[1:3])
            raise Exception("Error loading constituency file: "
                            "constituency seats and adjustment seats "
                            "must add to a nonzero number.")
        cons.append({
            "name": row[0],
            "num_constituency_seats": int(row[1]),
            "num_adjustment_seats": int(row[2]),
            "num_total_seats": int(row[1])+int(row[2])})
    return cons

def load_votes(votefile, consts):
    if votefile.endswith("csv"):
        reader = read_csv(votefile)
    else:
        reader = read_xlsx(votefile)
    parties = next(reader)[1:]
    votes = [[] for i in range(len(consts))]
    c_names = [x["name"] for x in consts]

    for row in reader:
        try:
            v = votes[c_names.index(row[0])]
        except:
            print(row)
            raise Exception("Constituency '%s' not found in constituency file"
                            % row[0])
        for x in row[1:]:
            try:
                r = float(x)
            except:
                r = 0
            v.append(r)

    return parties, votes

def print_steps_election(election):
    rules = election.rules
    header = ["Constituency"]
    header.extend(rules["parties"])
    header.append("Total")
    if "constituencies" in rules:
        const_names = [c["name"] for c in rules["constituencies"]]
    else:
        const_names = rules["constituency_names"]
    print("Votes")
    data = [[const_names[c]]+election.m_votes[c]
            +[sum(election.m_votes[c])]
            for c in range(len(const_names))]
    v_votes = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+v_votes)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Vote shares")
    shares = [["{:.1%}".format(d/c[-1]) if d is not None else None for d in c[1:]] for c in data]
    data = [[data[c][0]]+shares[c] for c in range(len(data))]
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Constituency seats")
    data = [[const_names[c]]+election.const_seats_alloc[c]
            +[sum(election.const_seats_alloc[c])]
            for c in range(len(const_names))]
    totals = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Adjustment seat apportionment")
    print("Threshold: ", "{:.1%}".format(rules["adjustment_threshold"]))
    data = [["Total votes"]+v_votes]
    v_elim_votes = [v if v > 0 else None for v in election.v_votes_eliminated]
    v_elim_votes.append(sum(election.v_votes_eliminated))
    data.append(["Votes above threshold"]+v_elim_votes)
    v_elim_shares = ["{:.1%}".format(v/v_elim_votes[-1]) if v is not None
                        else None for v in v_elim_votes]
    data.append(["Vote shares above threshold"]+v_elim_shares)
    v_const_seats = [a if a > 0 else None for a in election.v_cur_allocations]
    data.append(["Constituency seats"]+v_const_seats
        +[sum(election.v_cur_allocations)])
    print(tabulate.tabulate(data, header[1:], rules["output"]))
    print()
    method = ADJUSTMENT_METHODS[rules["adjustment_method"]]
    try:
        h, data = method.print_seats(rules, election.adj_seats_info)
        print(tabulate.tabulate(data, h, rules["output"]))
        print()
    except AttributeError:
        pass
    print("Adjustment seats")
    adj_seats = [[election.results[i][j]-election.const_seats_alloc[i][j]
                    for j in range(len(election.results[i]))]
                    for i in range(len(election.results))]
    data = [[const_names[c]]+adj_seats[c]
            +[sum(adj_seats[c])]
            for c in range(len(const_names))]
    totals = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Total seats")

def pretty_print_election(election):
    rules = election.rules
    header = ["Constituency"]
    header.extend(rules["parties"])
    header.append("Total")
    if "constituencies" in rules:
        const_names = [c["name"] for c in rules["constituencies"]]
    else:
        const_names = rules["constituency_names"]
    data = [[const_names[c]]+election.results[c]+[sum(election.results[c])]
            for c in range(len(const_names))]
    totals = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, header, rules["output"]))


def entropy(votes, allocations, divisor_gen):
    """
    Calculate entropy of the election, taking into account votes and
     allocations.
     $\\sum_i \\sum_j \\sum_k \\log{v_{ij}/d_k}$, more or less.
    """
    assert(type(votes) == list)
    assert(all(type(v) == list for v in votes))
    assert(type(allocations) == list)
    assert(all(type(a) == list for a in allocations))

    e = 0
    for i in range(len(votes)):
        divisor_gens = [divisor_gen() for x in range(len(votes[0]))]
        for j in range(len(votes[0])):
            for k in range(allocations[i][j]):
                dk = next(divisor_gens[j])
                e += log(votes[i][j]/dk)
    return e


def write_to_xlsx(election, filename):
    const_names = election.rules["constituency_names"]
    parties = election.rules["parties"]
    votes = election.m_votes
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Constituency')
    for i in range(len(parties)):
      worksheet.write(0, i+1, parties[i])
    for i in range(1, len(votes)+1):
      worksheet.write(i, 0, const_names[i-1])
      for j in range(1, len(votes[i-1])+1):
        worksheet.write(i, j, votes[i-1][j-1])

    workbook.close()

def election_to_xlsx(election, filename):
    const_names = copy(election.rules["constituency_names"]) + ["Total"]
    parties = copy(election.rules["parties"]) + ["Total"]
    votes = deepcopy(election.m_votes) + [[]]
    const_seats = deepcopy(election.const_seats_alloc) + [[]]
    total_seats = deepcopy(election.results) + [[]]
    for i in range(len(votes)-1):
        votes[i].append(sum(votes[i]))
        const_seats[i].append(sum(const_seats[i]))
        total_seats[i].append(sum(total_seats[i]))
    for j in range(len(votes[0])):
        p_votes = [c[j] for c in votes[:-1]]
        votes[-1].append(sum(p_votes))
        p_const_seats = [c[j] for c in const_seats[:-1]]
        const_seats[-1].append(sum(p_const_seats))
        p_total_seats = [c[j] for c in total_seats[:-1]]
        total_seats[-1].append(sum(p_total_seats))
    adj_seats = [[total_seats[i][j]-const_seats[i][j]
                    for j in range(len(total_seats[i]))]
                    for i in range(len(total_seats))]
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format()
    cell_format.set_align('right')
    worksheet.set_column('B:B', 20)
    worksheet.write('C5', 'Votes', cell_format)
    worksheet.write('B6', 'Constituency', cell_format)
    worksheet.write_row(5, 2, parties, cell_format)
    r = 5
    worksheet.write_column(6, 1, const_names, cell_format)
    for i in range(len(votes)):
        r += 1
        worksheet.write_row(r, 2, votes[i], cell_format)
    r += 2
    worksheet.write(r, 2, 'Vote shares', cell_format)
    r += 1
    worksheet.write(r, 1, 'Constituency', cell_format)
    worksheet.write_row(r, 2, parties, cell_format)
    worksheet.write_column(r+1, 1, const_names, cell_format)
    for i in range(len(votes)):
        r += 1
        shares = ["{:.1%}".format(votes[i][j]/sum(votes[i][:-1]))
                    for j in range(len(votes[i]))]
        worksheet.write_row(r, 2, shares, cell_format)
    r += 2
    worksheet.write(r, 2, 'Constituency seats', cell_format)
    r += 1
    worksheet.write(r, 1, 'Constituency', cell_format)
    worksheet.write_row(r, 2, parties, cell_format)
    worksheet.write_column(r+1, 1, const_names, cell_format)
    for i in range(len(const_seats)):
        r += 1
        for j in range(len(const_seats[i])):
            if const_seats[i][j] != 0:
                worksheet.write(r, j+2, const_seats[i][j], cell_format)
    r += 2
    worksheet.write(r, 2, 'Adjustment seat apportionment', cell_format)
    worksheet.write(r, 7, 'Threshold:', cell_format)
    worksheet.write(r, 8,
                    "{:.1%}".format(election.rules["adjustment_threshold"]),
                    cell_format)
    r += 1
    v_votes = copy(election.v_votes)
    v_votes.append(sum(v_votes))
    v_elim_votes = copy(election.v_votes_eliminated)
    v_elim_votes.append(sum(v_elim_votes))
    worksheet.write(r, 1, 'Party', cell_format)
    worksheet.write_row(r, 2, parties, cell_format)
    r += 1
    worksheet.write(r, 1, 'Total votes', cell_format)
    worksheet.write_row(r, 2, v_votes, cell_format)
    r += 1
    worksheet.write(r, 1, 'Votes above threshold', cell_format)
    for i in range(len(v_elim_votes)):
        if v_elim_votes[i] != 0:
            worksheet.write(r, i+2, v_elim_votes[i], cell_format)
    r += 1
    worksheet.write(r, 1, 'Vote shares above threshold', cell_format)
    for i in range(len(v_elim_votes)):
        if v_elim_votes[i] != 0:
            share = "{:.1%}".format(v_elim_votes[i]/sum(v_elim_votes[:-1]))
            worksheet.write(r, i+2, share, cell_format)
    r += 1
    v_elim_seats = []
    for i in range(len(v_elim_votes)-1):
        if v_elim_votes[i] != 0:
            v_elim_seats.append(election.v_cur_allocations[i])
        else:
            v_elim_seats.append(0)
    v_elim_seats.append(sum(v_elim_seats))
    worksheet.write(r, 1, 'Constituency seats', cell_format)
    for i in range(len(v_elim_seats)):
        if v_elim_seats[i] != 0:
            worksheet.write(r, i+2, v_elim_seats[i], cell_format)
    r += 2
    method = ADJUSTMENT_METHODS[election.rules["adjustment_method"]]
    try:
        h, data = method.print_seats(election.rules, election.adj_seats_info)
        worksheet.write_row(r, 1, h, cell_format)
        for i in range(len(data)):
            r += 1
            worksheet.write_row(r, 1, data[i], cell_format)
    except AttributeError:
        pass
    r += 2
    worksheet.write(r, 2, 'Adjustment seats', cell_format)
    r += 1
    worksheet.write(r, 1, 'Constituency', cell_format)
    worksheet.write_row(r, 2, parties, cell_format)
    worksheet.write_column(r+1, 1, const_names, cell_format)
    for i in range(len(adj_seats)):
        r += 1
        for j in range(len(adj_seats[i])):
            if adj_seats[i][j] != 0:
                worksheet.write(r, j+2, adj_seats[i][j], cell_format)
    r += 2
    worksheet.write(r, 2, 'Total seats', cell_format)
    r += 1
    worksheet.write(r, 1, 'Constituency', cell_format)
    worksheet.write_row(r, 2, parties, cell_format)
    worksheet.write_column(r+1, 1, const_names, cell_format)
    for i in range(len(total_seats)):
        r += 1
        for j in range(len(total_seats[i])):
            if total_seats[i][j] != 0:
                worksheet.write(r, j+2, total_seats[i][j], cell_format)
    r += 2
    worksheet.write(r, 1, 'Entropy:', cell_format)
    worksheet.write(r, 2, election.entropy(), cell_format)

    workbook.close()

def sim_election_rules(rs, test_method):
    config = configparser.ConfigParser()
    config.read("../data/presets/methods.ini")

    if test_method in config:
        rs.update(config[test_method])
    else:
        raise ValueError("%s is not a known apportionment method" % test_method)
    rs["adjustment_threshold"] = float(rs["adjustment_threshold"])

    return rs

def print_simulation(simulation):
    election = simulation.election
    rules = election.rules
    h = ["Constituency"]
    h.extend(rules["parties"]+["Total"])
    if "constituencies" in rules:
        const_names = [c["name"] for c in rules["constituencies"]]
    else:
        const_names = rules["constituency_names"]
    const_names.append("Total")
    print("Reference")
    print("\nVotes")
    data = [[const_names[c]]+simulation.ref_votes[c]
                for c in range(len(const_names))]
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nVote shares")
    data = [[const_names[c]]+simulation.ref_shares[c][:-1]
                for c in range(len(const_names))]
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h[:-1], rules["output"]))
    print("\nConstituency seats")
    data = [[const_names[c]]+election.const_seats_alloc[c]
            +[sum(election.const_seats_alloc[c])]
            for c in range(len(const_names)-1)]
    totals = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nAdjustment seats")
    adj_seats = [[election.results[i][j]-election.const_seats_alloc[i][j]
                    for j in range(len(election.results[i]))]
                    for i in range(len(election.results))]
    data = [[const_names[c]]+adj_seats[c]+[sum(adj_seats[c])]
            for c in range(len(const_names)-1)]
    totals = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nTotal seats")
    data = [[const_names[c]]+election.results[c]+[sum(election.results[c])]
            for c in range(len(const_names)-1)]
    totals = [sum([data[c][p] for c in range(len(data))])
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nSeat shares")
    data = [[c[0]]+["{:.1%}".format(s/c[-1]) if s is not None else None
            for s in c[1:-1]] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))

    print("\nAverages from simulation")
    print("\nVotes")
    data = [[const_names[c]]+simulation.avg_simul_votes[c]
            for c in range(len(simulation.avg_simul_votes))]
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nVote shares")
    shares = [["{:.1%}".format(s) if s != 0 else None for s in c[:-1]]
                for c in simulation.avg_simul_shares]
    data = [[const_names[c]]+shares[c] for c in range(len(const_names))]
    print(tabulate.tabulate(data, h[:-1], rules["output"]))
    print("\nConstituency seats")
    data = [[const_names[c]]+simulation.avg_const_seats[c]
            for c in range(len(const_names))]
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nAdjustment seats")
    data = [[const_names[c]]+simulation.avg_adj_seats[c]
            for c in range(len(const_names))]
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nTotal seats")
    data = [[const_names[c]]+simulation.avg_total_seats[c]
            for c in range(len(const_names))]
    data = [[d if d != 0 else None for d in c] for c in data]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nSeat shares")
    shares = [["{:.1%}".format(s) if s != 0 else None for s in c[:-1]]
                for c in simulation.avg_seat_shares]
    data = [[const_names[c]]+shares[c] for c in range(len(const_names))]
    print(tabulate.tabulate(data, h[:-1], rules["output"]))

    print("\nStandard deviations from simulation")
    print("\nVotes")
    sdev_votes = [[round(sqrt(v),3) for v in c]
                    for c in simulation.var_simul_votes]
    sdev_vote_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]]
                        for c in simulation.var_simul_shares]
    sdev_const_seats = [[round(sqrt(s),3) for s in c]
                        for c in simulation.var_const_seats]
    sdev_adj_seats = [[round(sqrt(s),3) for s in c]
                        for c in simulation.var_adj_seats]
    sdev_total_seats = [[round(sqrt(s),3) for s in c]
                        for c in simulation.var_total_seats]
    sdev_seat_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]]
                        for c in simulation.var_seat_shares]

    data = [[const_names[c]]+sdev_votes[c] for c in range(len(sdev_votes))]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nVote shares")
    data = [[const_names[c]]+sdev_vote_shares[c]
            for c in range(len(sdev_vote_shares))]
    print(tabulate.tabulate(data, h[:-1], rules["output"]))
    print("\nConstituency seats")
    data = [[const_names[c]]+sdev_const_seats[c]
            for c in range(len(const_names))]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nAdjustment seats")
    data = [[const_names[c]]+sdev_adj_seats[c]
            for c in range(len(const_names))]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nTotal seats")
    data = [[const_names[c]]+sdev_total_seats[c]
            for c in range(len(const_names))]
    print(tabulate.tabulate(data, h, rules["output"]))
    print("\nSeat shares")
    data = [[const_names[c]]+sdev_seat_shares[c]
            for c in range(len(const_names))]
    print(tabulate.tabulate(data, h[:-1], rules["output"]))

    print("\nVotes added to change results")
    v = simulation.votes_to_change
    data = [[const_names[c]]+v[c] for c in range(len(const_names)-1)]
    print(tabulate.tabulate(data, h[:-1], rules["output"]))


def simulation_to_xlsx(simulation, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    r_format = workbook.add_format()
    r_format.set_rotation(90)
    r_format.set_align('center')
    r_format.set_align('vcenter')
    r_format.set_text_wrap()
    r_format.set_bold()
    r_format.set_font_size(12)
    h_format = workbook.add_format()
    h_format.set_align('center')
    h_format.set_bold()
    h_format.set_font_size(14)
    cell_format = workbook.add_format()
    cell_format.set_align('right')
    election = simulation.election
    const_names = copy(election.rules["constituency_names"]) + ["Total"]
    parties = copy(election.rules["parties"]) + ["Total"]

    # Reference data:
    ref_votes = simulation.ref_votes
    ref_const_seats = deepcopy(election.const_seats_alloc) + [[]]
    ref_total_seats = deepcopy(election.results) + [[]]
    for i in range(len(ref_votes)-1):
        ref_const_seats[i].append(sum(ref_const_seats[i]))
        ref_total_seats[i].append(sum(ref_total_seats[i]))
    for j in range(len(ref_votes[0])):
        p_const_seats = [c[j] for c in ref_const_seats[:-1]]
        ref_const_seats[-1].append(sum(p_const_seats))
        p_total_seats = [c[j] for c in ref_total_seats[:-1]]
        ref_total_seats[-1].append(sum(p_total_seats))
    ref_adj_seats = [[ref_total_seats[i][j]-ref_const_seats[i][j]
                    for j in range(len(ref_total_seats[i]))]
                    for i in range(len(ref_total_seats))]

    toprow = 3
    r = copy(toprow)
    c = 2
    worksheet.merge_range(r+1, 0, len(const_names)+r+1, 0 ,"Reference data",
                            r_format)
    worksheet.merge_range(r, c, r, c+len(parties), "Votes", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_votes in ref_votes:
        worksheet.write_row(r, c+1, const_votes, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties)-1, "Vote shares", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties[:-1], cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_votes in ref_votes:
        shares = ["{:.1%}".format(v/const_votes[-1])
                    for v in const_votes[:-1]]
        worksheet.write_row(r, c+1, shares, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+1
    worksheet.merge_range(r, c, r, c+len(parties), "Constituency seats",
                            h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in ref_const_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties), "Adjustment seats",
                            h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in ref_adj_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties), "Total seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in ref_total_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties)-1, "Seat shares",
                            h_format)
    r += 1
    worksheet.write_row(r, c+1, parties[:-1], cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in ref_total_seats:
        seat_shares = ["{:.1%}".format(s/seats[-1]) for s in seats[:-1]]
        worksheet.write_row(r, c+1, seat_shares, cell_format)
        r += 1

    # Averages:
    toprow += len(const_names)+3
    r = copy(toprow)
    c = 2
    worksheet.merge_range(r+1, 0, len(const_names)+r+1, 0 ,"Averages from simulation", r_format)
    worksheet.merge_range(r, c, r, c+len(parties), "Votes", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_votes in simulation.avg_simul_votes:
        worksheet.write_row(r, c+1, const_votes, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties)-1, "Vote shares", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties[:-1], cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_shares in simulation.avg_simul_shares:
        shares = ["{:.1%}".format(s) for s in const_shares[:-1]]
        worksheet.write_row(r, c+1, shares, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+1
    worksheet.merge_range(r, c, r, c+len(parties), "Constituency seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in simulation.avg_const_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties), "Adjustment seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in simulation.avg_adj_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties), "Total seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in simulation.avg_total_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties)-1, "Seat shares", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties[:-1], cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_shares in simulation.avg_seat_shares:
        shares = ["{:.1%}".format(s) for s in const_shares[:-1]]
        worksheet.write_row(r, c+1, shares, cell_format)
        r += 1

    # Standard deviations:
    sdev_votes = [[round(sqrt(v),3) for v in c] for c in simulation.var_simul_votes]
    sdev_vote_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]] for c in simulation.var_simul_shares]
    sdev_const_seats = [[round(sqrt(v),3) for v in c] for c in simulation.var_const_seats]
    sdev_adj_seats = [[round(sqrt(v),3) for v in c] for c in simulation.var_adj_seats]
    sdev_total_seats = [[round(sqrt(v),3) for v in c] for c in simulation.var_total_seats]
    sdev_seat_shares = [["{:.1%}".format(sqrt(s)) for s in c[:-1]] for c in simulation.var_seat_shares]

    toprow += len(const_names)+3
    r = copy(toprow)
    c = 2
    worksheet.merge_range(r+1, 0, len(const_names)+r+1, 0 ,"Standard deviations from simulation", r_format)
    worksheet.merge_range(r, c, r, c+len(parties), "Votes", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_votes in sdev_votes:
        worksheet.write_row(r, c+1, const_votes, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties)-1, "Vote shares", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties[:-1], cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for const_vote_shares in sdev_vote_shares:
        worksheet.write_row(r, c+1, const_vote_shares, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+1
    worksheet.merge_range(r, c, r, c+len(parties), "Constituency seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in sdev_const_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties), "Adjustment seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in sdev_adj_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties), "Total seats", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties, cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for seats in sdev_total_seats:
        worksheet.write_row(r, c+1, seats, cell_format)
        r += 1
    r = copy(toprow)
    c += len(parties)+2
    worksheet.merge_range(r, c, r, c+len(parties)-1, "Seat shares", h_format)
    r += 1
    worksheet.write_row(r, c+1, parties[:-1], cell_format)
    r += 1
    worksheet.write_column(r, c, const_names, cell_format)
    for shares in sdev_seat_shares:
        worksheet.write_row(r, c+1, shares, cell_format)
        r += 1


    workbook.close()

ADJUSTMENT_METHODS = {
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "relative-inferiority": relative_inferiority,
    "monge": monge,
    "icelandic-law": icelandic_law,
    "norwegian-law": norwegian_law,
    "norwegian-icelandic": norwegian_icelandic,
    "opt-entropy": opt_entropy,
    "lund": kristinn_lund,
    "var-alt-scal": var_alt_scal
}
