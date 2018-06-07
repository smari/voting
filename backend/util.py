#coding:utf-8
import random
from backports import csv
from math import log
import sys
import tabulate
import io
import xlsxwriter
import openpyxl


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

def pretty_print_election(rules, election):
    header = ["Constituency"]
    header.extend(rules["parties"])
    if "constituencies" in rules:
        data = [[rules["constituencies"][c]["name"]]+election.results[c]
                for c in range(len(rules["constituencies"]))]
    else:
        data = [[rules["constituency_names"][c]]+election.results[c]
                for c in range(len(rules["constituency_names"]))]
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
