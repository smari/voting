
import xlsxwriter
from datetime import datetime

from util import ADJUSTMENT_METHODS
from table_util import matrix_subtraction, add_totals, find_xtd_shares
from dictionaries import ADJUSTMENT_METHOD_NAMES as AMN, \
                         DIVIDER_RULE_NAMES as DRN, \
                         GENERATING_METHOD_NAMES as GMN

def prepare_formats(workbook):
    formats = {}
    formats["cell"] = workbook.add_format()
    formats["cell"].set_align('right')

    formats["share"] = workbook.add_format()
    formats["share"].set_num_format('0.0%')

    formats["h"] = workbook.add_format()
    formats["h"].set_align('center')
    formats["h"].set_bold()
    formats["h"].set_font_size(14)

    formats["time"] = workbook.add_format()
    formats["time"].set_num_format('d mmm yyyy hh:mm')
    formats["time"].set_align('left')

    formats["basic"] = workbook.add_format()
    formats["basic"].set_align('left')

    formats["basic_h"] = workbook.add_format()
    formats["basic_h"].set_align('right')
    formats["basic_h"].set_bold()
    formats["basic_h"].set_font_size(12)

    formats["inter_h"] = workbook.add_format()
    formats["inter_h"].set_align('right')
    formats["inter_h"].set_bold()
    formats["inter_h"].set_italic()
    formats["inter_h"].set_font_size(13)

    #simulations
    formats["r"] = workbook.add_format()
    formats["r"].set_rotation(90)
    formats["r"].set_align('center')
    formats["r"].set_align('vcenter')
    formats["r"].set_text_wrap()
    formats["r"].set_bold()
    formats["r"].set_font_size(12)

    formats["base"] = workbook.add_format()
    formats["base"].set_num_format('#,##0')

    formats["sim"] = workbook.add_format()
    formats["sim"].set_num_format('#,##0.000')

    return formats

def write_matrix(worksheet, startrow, startcol, matrix, cformat, display_zeroes=False):
    for c in range(len(matrix)):
        for p in range(len(matrix[c])):
            if matrix[c][p] != 0 or display_zeroes:
                try:
                    worksheet.write(startrow+c, startcol+p, matrix[c][p],
                                    cformat[c])
                except TypeError:
                    worksheet.write(startrow+c, startcol+p, matrix[c][p],
                                    cformat)

def elections_to_xlsx(elections, filename):
    raise NotImplementedError

def election_to_xlsx(election, filename):
    """Write detailed information about a single election to an xlsx file."""
    const_names = [c["name"] for c in election.rules["constituencies"]]
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
    fmt = prepare_formats(workbook)
    worksheet = workbook.add_worksheet()

    worksheet.set_column('B:B', 20)

    def draw_block(worksheet, row, col,
        heading, xheaders, yheaders,
        matrix,
        topleft="Constituency",
        cformat=fmt["cell"]
    ):
        if heading.endswith("shares"):
            cformat = fmt["share"]
        worksheet.merge_range(
            row, col+1,
            row, col+len(xheaders),
            heading, fmt["h"]
        )
        worksheet.write(row+1, col, topleft, fmt["cell"])
        worksheet.write_row(row+1, col+1, xheaders, fmt["cell"])
        worksheet.write_column(row+2, col, yheaders, fmt["cell"])
        write_matrix(worksheet, row+2, col+1, matrix, cformat)

    startcol = 1

    toprow=0
    c1=1
    left_span=2
    c2=c1+left_span
    worksheet.merge_range(toprow,c1,toprow,c2-1,"Date:",fmt["basic_h"])
    worksheet.merge_range(toprow,c2,toprow,c2+1,datetime.now(),fmt["time"])
    toprow+=1
    worksheet.merge_range(toprow,c1,toprow,c2-1,"Test name:",fmt["basic_h"])
    worksheet.write(toprow,c2,election.name,fmt["basic"])

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
    formats = [fmt["cell"], fmt["share"], fmt["share"],
               fmt["cell"], fmt["share"], fmt["cell"]]
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
            "Step-by-step demonstration", fmt["h"]
        )
        worksheet.write_row(startrow+1, 1, h, fmt["cell"])
        for i in range(len(data)):
            worksheet.write_row(startrow+2+i, 1, data[i], fmt["cell"])
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

    worksheet.write(startrow, startcol, 'Entropy:', fmt["h"])
    worksheet.write(startrow, startcol+1, election.entropy(), fmt["cell"])

    workbook.close()


def simulation_to_xlsx(simulation, filename):
    """Write detailed information about a simulation to an xlsx file."""
    workbook = xlsxwriter.Workbook(filename)
    fmt = prepare_formats(workbook)

    def draw_block(worksheet, row, col,
        heading, xheaders, yheaders,
        matrix,
        cformat=fmt["cell"]
    ):
        if heading.endswith("shares"):
            cformat = fmt["share"]
        if heading.lower().startswith("ideal"):
            cformat = fmt["cell"]
        if heading == "Votes":
            cformat = fmt["base"]
        worksheet.merge_range(
            row, col, row, col+len(xheaders), heading, fmt["h"])
        worksheet.write_row(row+1, col+1, xheaders, fmt["cell"])
        worksheet.write_column(row+2, col, yheaders, fmt["cell"])
        write_matrix(worksheet, row+2, col+1, matrix, cformat)

    def present_measures(worksheet, row, col, xheaders,
        deviation_measures, ideal_comparison_measures, normalized_measures
    ):
        worksheet.write(row, col, "Quality measures", fmt["h"])
        row += 1
        worksheet.write_row(row, col+2, xheaders, fmt["basic_h"])
        row += 1
        worksheet.write(row, col+1,
            "Comparison to other seat allocations", fmt["inter_h"])
        row += 1
        worksheet.write(row, col,
            "Sum of absolute differences of tested method and:", fmt["inter_h"])
        row += 1
        worksheet.write_column(row, col,
            deviation_measures["headers"], fmt["basic_h"])
        write_matrix(worksheet, row, col+2,
            deviation_measures["matrix"], fmt["cell"], True)
        row += len(deviation_measures["headers"])
        worksheet.write(row, col+1,
            "Quality indices (the higher the better)", fmt["inter_h"])
        row += 1
        worksheet.write_column(row, col,
            normalized_measures["headers"], fmt["basic_h"])
        write_matrix(worksheet, row, col+2,
            normalized_measures["matrix"], fmt["cell"], True)
        row += len(normalized_measures["headers"])
        worksheet.write(row, col+1,
            "Comparison to ideal seat shares (the lower the better)",
            fmt["inter_h"])
        row += 1
        worksheet.write_column(row, col,
            ideal_comparison_measures["headers"], fmt["basic_h"])
        write_matrix(worksheet, row, col+2,
            ideal_comparison_measures["matrix"], fmt["cell"], True)
        row += len(ideal_comparison_measures["headers"])

    categories = [
        {"abbr": "base", "cell_format": fmt["base"],
         "heading": "Reference data"},
        {"abbr": "avg",  "cell_format": fmt["sim"],
         "heading": "Averages"},
        {"abbr": "max",  "cell_format": fmt["sim"],
         "heading": "Maximum values"},
        {"abbr": "min",  "cell_format": fmt["sim"],
         "heading": "Minimum values"},
        {"abbr": "std",  "cell_format": fmt["sim"],
         "heading": "Standard deviations"},
    ]
    tables = [
        {"abbr": "v",  "heading": "Votes"             },
        {"abbr": "vs", "heading": "Vote shares"       },
        {"abbr": "id", "heading": "Ideal seat shares" },
        {"abbr": "cs", "heading": "Constituency seats"},
        {"abbr": "as", "heading": "Adjustment seats"  },
        {"abbr": "ts", "heading": "Total seats"       },
        {"abbr": "ss", "heading": "Seat shares"       },
    ]
    base_const_names = [const["name"] for const in simulation.constituencies]\
                        + ["Total"]

    for r in range(len(simulation.e_rules)):
        sheet_name  = f'{r+1}-{simulation.e_rules[r]["name"]}'
        worksheet   = workbook.add_worksheet(sheet_name[:31])
        const_names = [
            const["name"] for const in simulation.e_rules[r]["constituencies"]
        ] + ["Total"]
        parties = simulation.e_rules[r]["parties"] + ["Total"]

        data_matrix = {
            "base": {
                "v" : simulation.xtd_votes,
                "vs": simulation.xtd_vote_shares,
                "cs": simulation.base_allocations[r]["xtd_const_seats"],
                "as": simulation.base_allocations[r]["xtd_adj_seats"],
                "ts": simulation.base_allocations[r]["xtd_total_seats"],
                "ss": simulation.base_allocations[r]["xtd_seat_shares"],
                "id": simulation.base_allocations[r]["xtd_ideal_seats"],
            },
            "avg": {
                "v" : simulation.list_data[-1]["sim_votes"  ]["avg"],
                "vs": simulation.list_data[-1]["sim_shares" ]["avg"],
                "cs": simulation.list_data[ r]["const_seats"]["avg"],
                "as": simulation.list_data[ r]["adj_seats"  ]["avg"],
                "ts": simulation.list_data[ r]["total_seats"]["avg"],
                "ss": simulation.list_data[ r]["seat_shares"]["avg"],
                "id": simulation.list_data[ r]["ideal_seats"]["avg"],
            },
            "std": {
                "v" : simulation.list_data[-1]["sim_votes"  ]["std"],
                "vs": simulation.list_data[-1]["sim_shares" ]["std"],
                "cs": simulation.list_data[ r]["const_seats"]["std"],
                "as": simulation.list_data[ r]["adj_seats"  ]["std"],
                "ts": simulation.list_data[ r]["total_seats"]["std"],
                "ss": simulation.list_data[ r]["seat_shares"]["std"],
                "id": simulation.list_data[ r]["ideal_seats"]["std"],
            },
            "min": {
                "v" : simulation.list_data[-1]["sim_votes"  ]["min"],
                "vs": simulation.list_data[-1]["sim_shares" ]["min"],
                "cs": simulation.list_data[ r]["const_seats"]["min"],
                "as": simulation.list_data[ r]["adj_seats"  ]["min"],
                "ts": simulation.list_data[ r]["total_seats"]["min"],
                "ss": simulation.list_data[ r]["seat_shares"]["min"],
                "id": simulation.list_data[ r]["ideal_seats"]["min"],
            },
            "max": {
                "v" : simulation.list_data[-1]["sim_votes"  ]["max"],
                "vs": simulation.list_data[-1]["sim_shares" ]["max"],
                "cs": simulation.list_data[ r]["const_seats"]["max"],
                "as": simulation.list_data[ r]["adj_seats"  ]["max"],
                "ts": simulation.list_data[ r]["total_seats"]["max"],
                "ss": simulation.list_data[ r]["seat_shares"]["max"],
                "id": simulation.list_data[ r]["ideal_seats"]["max"],
            },
        }

        date_label = "Date:"
        row_constraints = simulation.sim_rules["row_constraints"] and simulation.num_parties > 1
        col_constraints = simulation.sim_rules["col_constraints"] and simulation.num_constituencies > 1
        info_groups = [
            {"left_span": 2, "right_span": 3, "info": [
                {"label": date_label,
                    "data": datetime.now()},
                {"label": "Reference votes:",
                    "data": simulation.vote_table["name"]},
                {"label": "Electoral system:",
                    "data": simulation.e_rules[r]["name"]},
            ]},
            {"left_span": 5, "right_span": 3, "info": [
                {"label": "Threshold for constituency seats:",
                    "data": simulation.e_rules[r]["constituency_threshold"]},
                {"label": "Rule for allocating constituency seats:",
                    "data": DRN[simulation.e_rules[r]["primary_divider"]]},
                {"label": "Threshold for adjustment seats:",
                    "data": simulation.e_rules[r]["adjustment_threshold"]},
                {"label": "Rule for dividing adjustment seats:",
                    "data": DRN[simulation.e_rules[r]["adj_determine_divider"]]},
                {"label": "Method for allocating adjustment seats:",
                    "data": AMN[simulation.e_rules[r]["adjustment_method"]]},
                {"label": "Rule for allocating adjustment seats:",
                    "data": DRN[simulation.e_rules[r]["adj_alloc_divider"]]},
            ]},
            {"left_span": 5, "right_span": 3, "info": [
                {"label": "Number of simulations run:",
                    "data": simulation.iteration},
                {"label": "Generating method:",
                    "data": GMN[simulation.variate]},
                {"label": "Stability parameter:",
                    "data": simulation.stbl_param},
                {"label": "Ideal seat shares scaled by constituencies:",
                    "data": "Yes" if row_constraints else "No"},
                {"label": "Ideal seat shares scaled by parties:",
                    "data": "Yes" if col_constraints else "No"},
            ]},
        ]

        toprow = 0
        bottomrow = toprow
        c1=1
        #Basic info
        for group in info_groups:
            row = toprow
            c2 = c1 + group["left_span"]
            for info in group["info"]:
                worksheet.merge_range(row,c1,row,c2-1,info["label"],fmt["basic_h"])
                if info["label"] == date_label:
                    worksheet.merge_range(row,c2,row,c2+1,info["data"],fmt["time"])
                else:
                    worksheet.write(row,c2,info["data"],fmt["basic"])
                row += 1
            bottomrow = max(row, bottomrow)
            c1 = c2 + group["right_span"]

        draw_block(worksheet, row=toprow, col=c1+1,
            heading="Required number of seats",
            xheaders=["Const.", "Adj.", "Total"],
            yheaders=const_names,
            matrix=add_totals([
                [const["num_const_seats"],const["num_adj_seats"]]
                for const in simulation.e_rules[r]["constituencies"]])
        )
        bottomrow = max(2+len(const_names), bottomrow)
        toprow = bottomrow+2

        #Election tables
        for category in categories:
            worksheet.merge_range(toprow, 0, toprow+1+len(const_names), 0,
                category["heading"], fmt["r"])
            col = 2
            for table in tables:
                is_vote_table = table["heading"].startswith("Vote")
                draw_block(worksheet, row=toprow, col=col,
                    heading=table["heading"],
                    xheaders=parties,
                    yheaders=base_const_names if is_vote_table else const_names,
                    matrix=data_matrix[category["abbr"]][table["abbr"]],
                    cformat=category["cell_format"]
                )
                col += len(parties)+2
            toprow += len(const_names)+3

        #Measures
        results = simulation.get_results_dict()
        DEVIATION_MEASURES = results["deviation_measures"]
        STANDARDIZED_MEASURES = results["standardized_measures"]
        IDEAL_COMPARISON_MEASURES = results["ideal_comparison_measures"]
        MEASURES = results["measures"]
        aggregates = ["avg", "min", "max", "std"]
        aggregate_names = [results["aggregates"][aggr] for aggr in aggregates]
        present_measures(worksheet, row=toprow, col=9,
            xheaders=aggregate_names,
            deviation_measures={
                "headers": [MEASURES[key] for key in DEVIATION_MEASURES],
                "matrix": [
                    [simulation.data[r][measure][aggr] for aggr in aggregates]
                    for measure in DEVIATION_MEASURES
                ]
            },
            ideal_comparison_measures={
                "headers": [MEASURES[key] for key in IDEAL_COMPARISON_MEASURES],
                "matrix": [
                    [simulation.data[r][measure][aggr] for aggr in aggregates]
                    for measure in IDEAL_COMPARISON_MEASURES
                ]
            },
            normalized_measures={
                "headers": [MEASURES[key] for key in STANDARDIZED_MEASURES],
                "matrix": [
                    [simulation.data[r][measure][aggr] for aggr in aggregates]
                    for measure in STANDARDIZED_MEASURES
                ]
            }
        )

    workbook.close()

def save_votes_to_xlsx(matrix, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    fmt = prepare_formats(workbook)
    write_matrix(worksheet=worksheet, startrow=0, startcol=0,
        matrix=matrix, cformat=fmt["cell"])
    workbook.close()
