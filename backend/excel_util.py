
import xlsxwriter
from datetime import datetime

from util import ADJUSTMENT_METHODS
from table_util import matrix_subtraction, add_totals, find_xtd_shares



def election_to_xlsx(election, filename):
    """Write detailed information about a single election to an xlsx file."""
    if "constituencies" in election.rules:
        const_names = [c["name"] for c in election.rules["constituencies"]]
    else:
        const_names = election.rules["constituency_names"]
    const_names.append("Total")
    parties = election.rules["parties"] + ["Total"]
    xtd_votes = add_totals(election.m_votes)
    xtd_shares = find_xtd_shares(xtd_votes)
    xtd_const_seats = add_totals(election.m_const_seats_alloc)
    xtd_total_seats = add_totals(election.results)
    xtd_adj_seats = matrix_subtraction(xtd_total_seats, xtd_const_seats)
    xtd_seat_shares = find_xtd_shares(xtd_total_seats)
    threshold = 0.01*election.rules["adjustment_threshold"]
    xtd_final_votes = add_totals([election.v_votes_eliminated])[0]
    xtd_final_shares = find_xtd_shares([xtd_final_votes])[0]

    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format()
    cell_format.set_align('right')
    share_format = workbook.add_format()
    share_format.set_num_format('0.0%')
    h_format = workbook.add_format()
    h_format.set_align('center')
    h_format.set_bold()
    h_format.set_font_size(14)

    time_format = workbook.add_format()
    time_format.set_num_format('d mmm yyyy hh:mm')

    worksheet.set_column('B:B', 20)

    def write_matrix(worksheet, startrow, startcol, matrix, cformat):
        for c in range(len(matrix)):
            for p in range(len(matrix[c])):
                if matrix[c][p] != 0:
                    try:
                        worksheet.write(startrow+c, startcol+p, matrix[c][p],
                                        cformat[c])
                    except TypeError:
                        worksheet.write(startrow+c, startcol+p, matrix[c][p],
                                        cformat)

    def draw_block(worksheet, row, col,
        heading, xheaders, yheaders,
        matrix,
        topleft="Constituency",
        cformat=cell_format
    ):
        if heading.endswith("shares"):
            cformat = share_format
        worksheet.merge_range(
            row, col+1,
            row, col+len(xheaders),
            heading, h_format
        )
        worksheet.write(row+1, col, topleft, cell_format)
        worksheet.write_row(row+1, col+1, xheaders, cell_format)
        worksheet.write_column(row+2, col, yheaders, cell_format)
        write_matrix(worksheet, row+2, col+1, matrix, cformat)

    startcol = 1

    toprow=0
    worksheet.merge_range(toprow,0,toprow,1,"Test name:",h_format)
    worksheet.merge_range(toprow,2,toprow,3,"My electoral system",cell_format)
    worksheet.merge_range(toprow+1,0,toprow+1,1,"Date:",h_format)
    worksheet.merge_range(toprow+1,2,toprow+1,3,datetime.now(),time_format)

    startrow = 4
    tables_before = [
        {"heading": "Votes",              "matrix": xtd_votes      },
        {"heading": "Vote shares",        "matrix": xtd_shares     },
        {"heading": "Constituency seats", "matrix": xtd_const_seats},
    ]
    for table in tables_before:
        draw_block(worksheet, row=startrow, col=startcol,
            heading=table["heading"], xheaders=parties, yheaders=const_names,
            matrix=table["matrix"]
        )
        startrow += 3 + len(const_names)

    row_headers = ['Total votes', 'Vote shares', 'Threshold',
                   'Votes above threshold',
                   'Vote shares above threshold', 'Constituency seats']
    matrix = [xtd_votes[-1],   xtd_shares[-1],   [threshold],
              xtd_final_votes, xtd_final_shares, xtd_const_seats[-1]]
    formats = [cell_format, share_format, share_format,
               cell_format, share_format, cell_format]
    draw_block(worksheet, row=startrow, col=startcol,
        heading="Adjustment seat apportionment", topleft="Party",
        xheaders=parties, yheaders=row_headers,
        matrix=matrix, cformat=formats
    )
    startrow += 3 + len(row_headers)

    method = ADJUSTMENT_METHODS[election.rules["adjustment_method"]]
    try:
        h, data = method.print_seats(election.rules, election.adj_seats_info)
        worksheet.merge_range(
            startrow, startcol+1,
            startrow, startcol+len(parties),
            "Step-by-step demonstration", h_format
        )
        worksheet.write_row(startrow+1, 1, h, cell_format)
        for i in range(len(data)):
            worksheet.write_row(startrow+2+i, 1, data[i], cell_format)
        startrow += 3 + len(data)
    except AttributeError:
        pass

    tables_after = [
        {"heading": "Adjustment seats", "matrix": xtd_adj_seats  },
        {"heading": "Total seats",      "matrix": xtd_total_seats},
        {"heading": "Seat shares",      "matrix": xtd_seat_shares},
    ]
    for table in tables_after:
        draw_block(worksheet, row=startrow, col=startcol,
            heading=table["heading"], xheaders=parties, yheaders=const_names,
            matrix=table["matrix"]
        )
        startrow += 3 + len(const_names)

    worksheet.write(startrow, startcol, 'Entropy:', h_format)
    worksheet.write(startrow, startcol+1, election.entropy(), cell_format)

    workbook.close()


def simulation_to_xlsx(simulation, filename):
    """Write detailed information about a simulation to an xlsx file."""
    workbook = xlsxwriter.Workbook(filename)

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

    base_format = workbook.add_format()
    base_format.set_num_format('#,##0')

    sim_format = workbook.add_format()
    sim_format.set_num_format('#,##0.000')

    share_format = workbook.add_format()
    share_format.set_num_format('0.0%')

    time_format = workbook.add_format()
    time_format.set_num_format('d mmm yyyy hh:mm')
    time_format.set_align('left')

    basic_format = workbook.add_format()
    basic_format.set_align('left')


    def write_matrix(worksheet, startrow, startcol, matrix, cformat):
        for c in range(len(matrix)):
            for p in range(len(matrix[c])):
                if matrix[c][p] != 0:
                    worksheet.write(startrow+c, startcol+p, matrix[c][p],
                                    cformat)

    def draw_block(worksheet, row, col,
        heading, xheaders, yheaders,
        matrix,
        cformat=cell_format
    ):
        if heading.endswith("shares"):
            cformat = share_format
        if heading == "Votes":
            cformat = base_format
        worksheet.merge_range(
            row, col, row, col+len(xheaders), heading, h_format)
        worksheet.write_row(row+1, col+1, xheaders, cell_format)
        worksheet.write_column(row+2, col, yheaders, cell_format)
        write_matrix(worksheet, row+2, col+1, matrix, cformat)

    categories = [
        {"abbr": "base", "cell_format": base_format,
         "heading": "Reference data"                     },
        {"abbr": "avg",  "cell_format": sim_format,
         "heading": "Averages from simulation"           },
        {"abbr": "std",  "cell_format": sim_format,
         "heading": "Standard deviations from simulation"},
    ]
    tables = [
        {"abbr": "v",  "heading": "Votes"             },
        {"abbr": "vs", "heading": "Vote shares"       },
        {"abbr": "cs", "heading": "Constituency seats"},
        {"abbr": "as", "heading": "Adjustment seats"  },
        {"abbr": "ts", "heading": "Total seats"       },
        {"abbr": "ss", "heading": "Seat shares"       },
    ]

    for r in range(len(simulation.e_rules)):
        sheet_name  = f'{r+1}-{simulation.e_rules[r]["name"]}'
        worksheet   = workbook.add_worksheet(sheet_name)
        const_names = simulation.e_rules[r]["constituency_names"] + ["Total"]
        parties     = simulation.e_rules[r]["parties"           ] + ["Total"]

        data_matrix = {
            "base": {
                "v" : simulation.xtd_votes,
                "vs": simulation.xtd_vote_shares,
                "cs": simulation.base_allocations[r]["xtd_const_seats"],
                "as": simulation.base_allocations[r]["xtd_adj_seats"],
                "ts": simulation.base_allocations[r]["xtd_total_seats"],
                "ss": simulation.base_allocations[r]["xtd_seat_shares"],
            },
            "avg": {
                "v" : simulation.list_data[-1]["sim_votes"  ]["avg"],
                "vs": simulation.list_data[-1]["sim_shares" ]["avg"],
                "cs": simulation.list_data[ r]["const_seats"]["avg"],
                "as": simulation.list_data[ r]["adj_seats"  ]["avg"],
                "ts": simulation.list_data[ r]["total_seats"]["avg"],
                "ss": simulation.list_data[ r]["seat_shares"]["avg"],
            },
            "std": {
                "v" : simulation.list_data[-1]["sim_votes"  ]["std"],
                "vs": simulation.list_data[-1]["sim_shares" ]["std"],
                "cs": simulation.list_data[ r]["const_seats"]["std"],
                "as": simulation.list_data[ r]["adj_seats"  ]["std"],
                "ts": simulation.list_data[ r]["total_seats"]["std"],
                "ss": simulation.list_data[ r]["seat_shares"]["std"],
            },
        }
        toprow = 0
        #Basic info
        row=toprow
        col=0
        cr=col+2
        worksheet.merge_range(row,col,row,col+1,"Date:",h_format)
        worksheet.merge_range(row,cr,row,cr+1,datetime.now(),time_format)
        row += 1
        worksheet.merge_range(row,col,row,col+1,"Vote name:",h_format)
        worksheet.write(row,cr,simulation.vote_table_name,basic_format)
        row += 1
        worksheet.merge_range(row,col,row,col+1,"Test name:",h_format)
        worksheet.write(row,cr,simulation.e_rules[r]["name"],basic_format)
        row += 1
        worksheet.merge_range(row,col,row,col+1,"Adjustment method",h_format)
        worksheet.write(row,cr,simulation.e_rules[r]["adjustment_method"],basic_format)

        col=8
        row=toprow
        worksheet.write(row,col,"Primary division rule",h_format)
        worksheet.write(row,col+1,simulation.e_rules[r]["primary_divider"],basic_format)
        row += 1
        worksheet.write(row,col,"Adjustment determination division rule",h_format)
        worksheet.write(row,col+1,simulation.e_rules[r]["adj_determine_divider"],basic_format)
        row += 1
        worksheet.write(row,col,"Adjustment allocation division rule",h_format)
        worksheet.write(row,col+1,simulation.e_rules[r]["adj_alloc_divider"],basic_format)
        row += 1
        worksheet.write(row,col,"Adjustment threshold",h_format)
        worksheet.write(row,col+1,simulation.e_rules[r]["adjustment_threshold"],cell_format)

        padding=2
        toprow += 4+padding

        #Election tables
        for category in categories:
            worksheet.merge_range(toprow, 0, toprow+1+len(const_names), 0,
                category["heading"], r_format)
            col = 2
            for table in tables:
                draw_block(worksheet, row=toprow, col=col,
                    heading=table["heading"],
                    xheaders=parties,
                    yheaders=const_names,
                    matrix=data_matrix[category["abbr"]][table["abbr"]],
                    cformat=category["cell_format"]
                )
                col += len(parties)+2
            toprow += len(const_names)+3

        #Measures
        results = simulation.get_results_dict()
        DEVIATION_MEASURES = results["deviation_measures"]
        STANDARDIZED_MEASURES = results["standardized_measures"]
        MEASURES = results["measures"]
        mkeys = DEVIATION_MEASURES + STANDARDIZED_MEASURES
        measure_names = [MEASURES[key] for key in mkeys]
        aggregates = ["avg", "std"]
        aggregate_names = [results["aggregates"][aggr] for aggr in aggregates]
        measure_table = [
            [simulation.data[r][measure][aggr] for aggr in aggregates]
            for measure in mkeys
        ]
        draw_block(worksheet, row=toprow, col=9,
            heading="Summary measures",
            xheaders=aggregate_names,
            yheaders=measure_names,
            matrix=measure_table,
            cformat=sim_format
        )

    workbook.close()
