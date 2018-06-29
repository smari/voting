#coding:utf-8
import random
from backports import csv
from math import log
import sys
import tabulate
import io
import xlsxwriter
import openpyxl
from copy import deepcopy, copy

from methods import icelandic_law


def random_id(length=8):
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'
    s = "".join(random.sample(chars, length))
    return s


def read_csv(filename):
    with io.open(filename, mode="r", newline='', encoding='utf-8') as f:
        for row in csv.reader(f):
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
            assert(sum([int(x) for x in row[1:3]]) > 0)
        except:
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
            raise Exception("Constituency '%s' not found in constituency file."
                            % row[0])
        for x in row[1:]:
            try:
                r = float(x)
            except:
                r = 0
            v.append(r)

    return parties, votes

def print_steps_election(rules, election):
    print("Votes")
    header = ["Constituency"]
    header.extend(rules["parties"])
    header.append("Total")
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+election.m_votes[c]
                +[sum(election.m_votes[c])]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+election.m_votes[c]
                +[sum(election.m_votes[c])]
                for c in range(len(rules["constituency_names"]))]
    totals = [sum([data[c][p] for c in range(len(data))]) 
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Vote shares")
    shares = [["{:.1%}".format(data[c][p]/data[c][-1]) for p in range(1,len(data[c]))] for c in range(len(data))]
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+shares[c]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+shares[c]
                for c in range(len(rules["constituency_names"]))]
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Constituency seats")
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+election.m_allocations[c]
                +[sum(election.m_allocations[c])]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+election.m_allocations[c]
                +[sum(election.m_allocations[c])]
                for c in range(len(rules["constituency_names"]))]
    totals = [sum([data[c][p] for c in range(len(data))]) 
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Threshold: ", "{:.1%}".format(rules["adjustment_threshold"]))
    v_votes = [sum([c[p] for c in election.m_votes]) for p in range(len(election.m_votes[0]))]
    v_votes.append(sum(v_votes))
    data = [["Total votes"]+v_votes]
    v_elim_votes = []
    for v in election.v_votes_eliminated:
        if v > 0:
            v_elim_votes.append(v)
        else:
            v_elim_votes.append(None)
    v_elim_votes.append(sum(election.v_votes_eliminated))
    data.append(["Votes above threshold"]+v_elim_votes)
    v_elim_shares = []
    for v in v_elim_votes:
        if v is not None:
            v_elim_shares.append("{:.1%}".format(v/v_elim_votes[-1]))
        else:
            v_elim_shares.append(None)
    data.append(["Vote shares above threshold"]+v_elim_shares)
    v_const_seats = []
    for a in election.v_cur_allocations:
        if a > 0:
            v_const_seats.append(a)
        else:
            v_const_seats.append(None)
    v_const_seats.append(sum(election.v_cur_allocations))
    data.append(["Constituency seats"]+v_const_seats)
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    """
    print("Adjustment seat apportionment")
    method = ADJUSTMENT_METHODS[rules["adjustment_method"]]
    h, data = method.print_seats(rules, election)
    print(tabulate.tabulate(data, h, rules["output"]))
    print()
    """
    print("Adjustment seats")
    adj_seats = [[election.results[i][j]-election.m_allocations[i][j] for j in range(len(election.results[i]))] for i in range(len(election.results))]
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+adj_seats[c]
                +[sum(adj_seats[c])]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+adj_seats[c]
                +[sum(adj_seats[c])]
                for c in range(len(rules["constituency_names"]))]
    totals = [sum([data[c][p] for c in range(len(data))]) 
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    print(tabulate.tabulate(data, header, rules["output"]))
    print()
    print("Total seats")

def pretty_print_election(rules, election):
    header = ["Constituency"]
    header.extend(rules["parties"])
    header.append("Total")
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+election.results[c]
                +[sum(election.results[c])]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+election.results[c]
                +[sum(election.results[c])]
                for c in range(len(rules["constituency_names"]))]
    totals = [sum([data[c][p] for c in range(len(data))]) 
                for p in range(1,len(data[0]))]
    data.append(["Total"]+totals)
    print(tabulate.tabulate(data, header, rules["output"]))


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
    const_seats = deepcopy(election.m_allocations) + [[]]
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
    adj_seats = [[total_seats[i][j]-const_seats[i][j] for j in range(len(total_seats[i]))] for i in range(len(total_seats))]
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    worksheet.write('C5', 'Votes')
    worksheet.write('B6', 'Constituency')
    for i in range(len(parties)):
        worksheet.write(5, i+2, parties[i])
    r = 5
    for i in range(len(votes)):
        r += 1
        worksheet.write(r, 1, const_names[i])
        for j in range(len(votes[i])):
            worksheet.write(r, j+2, votes[i][j])
    r += 2
    worksheet.write(r, 2, 'Vote shares')
    r += 1
    worksheet.write(r, 1, 'Constituency')
    for i in range(len(parties)):
        worksheet.write(r, i+2, parties[i])
    for i in range(len(votes)):
        r += 1
        worksheet.write(r, 1, const_names[i])
        for j in range(len(votes[i])):
            share = "{:.1%}".format(votes[i][j]/sum(votes[i][:-1]))
            worksheet.write(r, j+2, share)
    r += 2
    worksheet.write(r, 2, 'Constituency seats')
    r += 1
    worksheet.write(r, 1, 'Constituency')
    for i in range(len(parties)):
        worksheet.write(r, i+2, parties[i])
    for i in range(len(const_seats)):
        r += 1
        worksheet.write(r, 1, const_names[i])
        for j in range(len(const_seats[i])):
            if const_seats[i][j] != 0:
                worksheet.write(r, j+2, const_seats[i][j])
    r += 2
    worksheet.write(r, 2, 'Adjustment seat apportionment')
    worksheet.write(r, 7, 'Threshold:')
    worksheet.write(r, 8, "{:.1%}".format(election.rules["adjustment_threshold"]))
    r += 1
    v_votes = copy(election.v_votes)
    v_votes.append(sum(v_votes))
    v_elim_votes = copy(election.v_votes_eliminated)
    v_elim_votes.append(sum(v_elim_votes))
    worksheet.write(r, 1, 'Party')
    for i in range(len(parties)):
        worksheet.write(r, i+2, parties[i])
    r += 1
    worksheet.write(r, 1, 'Total votes')
    for i in range(len(v_votes)):
        worksheet.write(r, i+2, v_votes[i])
    r += 1
    worksheet.write(r, 1, 'Votes above threshold')
    for i in range(len(v_elim_votes)):
        if v_elim_votes[i] != 0:
            worksheet.write(r, i+2, v_elim_votes[i])
    r += 1
    worksheet.write(r, 1, 'Vote shares above threshold')
    for i in range(len(v_elim_votes)):
        if v_elim_votes[i] != 0:
            share = "{:.1%}".format(v_elim_votes[i]/sum(v_elim_votes[:-1]))
            worksheet.write(r, i+2, share)
    r += 1
    v_elim_seats = []
    for i in range(len(v_elim_votes)-1):
        if v_elim_votes[i] != 0:
            v_elim_seats.append(election.v_cur_allocations[i])
        else:
            v_elim_seats.append(0)
    v_elim_seats.append(sum(v_elim_seats))
    worksheet.write(r, 1, 'Constituency seats')
    for i in range(len(v_elim_seats)):
        if v_elim_seats[i] != 0:
            worksheet.write(r, i+2, v_elim_seats[i])
    r += 2
    worksheet.write(r, 2, 'Adjustment seats')
    r += 1
    worksheet.write(r, 1, 'Constituency')
    for i in range(len(parties)):
        worksheet.write(r, i+2, parties[i])
    for i in range(len(adj_seats)):
        r += 1
        worksheet.write(r, 1, const_names[i])
        for j in range(len(adj_seats[i])):
            if adj_seats[i][j] != 0:
                worksheet.write(r, j+2, adj_seats[i][j])
    r += 2
    worksheet.write(r, 2, 'Total seats')
    r += 1
    worksheet.write(r, 1, 'Constituency')
    for i in range(len(parties)):
        worksheet.write(r, i+2, parties[i])
    for i in range(len(total_seats)):
        r += 1
        worksheet.write(r, 1, const_names[i])
        for j in range(len(total_seats[i])):
            if total_seats[i][j] != 0:
                worksheet.write(r, j+2, total_seats[i][j])
    r += 2
    worksheet.write(r, 1, 'Entropy:')
    worksheet.write(r, 2, election.entropy())

    workbook.close()

ADJUSTMENT_METHODS = {
    #"alternating-scaling": alternating_scaling,
    #"relative-superiority": relative_superiority,
    #"relative-inferiority": relative_inferiority,
    #"monge": monge,
    "icelandic-law": icelandic_law,
    #"norwegian-law": norwegian_law,
    #"norwegian-icelandic": norwegian_icelandic,
    #"opt-entropy": opt_entropy
}