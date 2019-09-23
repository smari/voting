
from division_rules import dhondt_gen, sainte_lague_gen, \
    nordic_sainte_lague_gen, imperiali_gen, danish_gen, huntington_hill_gen
from division_rules import droop, hare

from methods.var_alt_scal import var_alt_scal
from methods.alternating_scaling import alternating_scaling
from methods.icelandic_law import icelandic_apportionment
from methods.icelandic_law_based_on_shares import icelandic_share_apportionment
from methods.monge import monge
from methods.nearest_neighbor import nearest_neighbor
from methods.relative_superiority import relative_superiority
from methods.relative_superiority_simple import relative_superiority_simple
from methods.norwegian_law import norwegian_apportionment
from methods.norwegian_icelandic import norw_ice_apportionment
from methods.pure_vote_ratios import pure_vote_ratios_apportionment
from methods.opt_entropy import opt_entropy
from methods.switching import switching

from distributions.beta_distribution import beta_distribution

DIVIDER_RULES = {
    "dhondt": dhondt_gen,
    "sainte-lague": sainte_lague_gen,
    "nordic": nordic_sainte_lague_gen,
    "imperiali": imperiali_gen,
    "danish": danish_gen,
    "huntington-hill": huntington_hill_gen,
}
DIVIDER_RULE_NAMES = {
    "dhondt": "D'Hondt's method",
    "sainte-lague": "Sainte-Laguë method",
    "nordic": "Nordic Sainte-Laguë variant",
    #"imperiali": "Imperiali method",
    "danish": "Danish method",
    "huntington-hill": "Huntington-Hill method",
}
QUOTA_RULES = {
    "droop": droop,
    "hare": hare,
}
RULE_NAMES = {
    "dhondt": "D'Hondt's method",
    "sainte-lague": "Sainte-Laguë method",
    "nordic": "Nordic Sainte-Laguë variant",
    #"imperiali": "Imperiali method",
    "danish": "Danish method",
    "huntington-hill": "Huntington-Hill method",
    "droop": "Droop quota",
    "hare": "Hare quota",
}

ADJUSTMENT_METHODS = {
    "var-alt-scal": var_alt_scal,
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "relative-superiority-simple": relative_superiority_simple,
    "nearest-neighbor": nearest_neighbor,
    "monge": monge,
    "icelandic-law": icelandic_apportionment,
    "ice-shares": icelandic_share_apportionment,
    "norwegian-law": norwegian_apportionment,
    "norwegian-icelandic": norw_ice_apportionment,
    "opt-entropy": opt_entropy,
    "switching": switching,
    "pure-vote-ratios": pure_vote_ratios_apportionment,
}
ADJUSTMENT_METHOD_NAMES = {
    "alternating-scaling": "Optimal method (Alternating-Scaling)",
    "relative-superiority": "Relative Superiority Method",
    "relative-superiority-simple": "Relative Superiority Method - Simple version",
    "nearest-neighbor": "Nearest Neighbor Method",
    "monge": "Monge algorithm",
    "icelandic-law": "Icelandic law 24/2000 (Kosningar til Alþingis)",
    "ice-shares": "Icelandic law modified to use seat shares",
    "norwegian-law": "Norwegian law",
    "norwegian-icelandic": "Norwegian-Icelandic variant",
    "switching": "Switching Method",
    "pure-vote-ratios": "Pure Vote Ratios"
}

GENERATING_METHODS = {
    "beta": beta_distribution
}
GENERATING_METHOD_NAMES = {
    "beta": "Beta distribution"
}

SEAT_SPECIFICATION_OPTIONS = {
    "refer":     "Refer to vote table",
    "all_const": "Make all seats constituency seats",
    "all_adj":   "Make all seats adjustment seats",
    "one_const": "Combine all constituencies into one",
    "custom":    "Specify seat distribution manually for this particular electoral system",
}

MEASURES = {
    "dev_opt":         "Allocation by the optimal method",
    "dev_opt_totals":  "Allocation by the optimal method",
    "dev_law":         "Allocation by Icelandic Law",
    "dev_law_totals":  "Allocation by Icelandic Law",
    "dev_all_adj":     "Allocation as if all seats were adjustment seats",
    "dev_all_adj_totals":
                       "Allocation as if all seats were adjustment seats",
    "dev_ind_const":   "Allocation as if all seats were constituency seats",
    "dev_ind_const_totals":
                       "Allocation as if all seats were constituency seats",
    "adj_dev":         "Desired apportionment of adjustment seats",
    "dev_one_const":   "Allocation as if all constituencies were combined into one",
    "entropy":         "Entropy (product of all seat values used)",
    "entropy_ratio":   "Entropy relative to optimal value",
    "min_seat_value":  "Mininum seat value used (based on ideal seat shares)",
    "sum_abs":         "Sum of absolute differences",
    "sum_pos":         "Sum of relative positive differences",
    "sum_sq":          "Sum of relative squared differences",
}
LIST_DEVIATION_MEASURES = [
    "dev_opt",
    "dev_law",
    "dev_all_adj",
    "dev_ind_const",
    # "dev_one_const", #skipped, because already measured by all_adj (party sums)
]
TOTALS_DEVIATION_MEASURES = [
    #"dev_opt_totals",
    #"dev_law_totals",
    "dev_all_adj_totals",
    "dev_ind_const_totals",
    "adj_dev",
]
STANDARDIZED_MEASURES = [
    "entropy_ratio",
    "min_seat_value",
]
IDEAL_COMPARISON_MEASURES = [
    "sum_abs",
    "sum_pos",
    "sum_sq",
]
LIST_MEASURES = {
    "const_seats":   "constituency seats",
    "adj_seats":     "adjustment seats",
    "total_seats":   "constituency and adjustment seats combined",
    "seat_shares":   "total seats normalized within each constituency",
    "ideal_seats":   "ideal seat shares",
    # "dev_opt":       "deviation from optimal solution",
    # "dev_law":       "deviation from official law method",
    # "dev_ind_const": "deviation from Independent Constituencies",
    # "dev_one_const": "deviation from Single Constituency",
    # "dev_all_adj":   "deviation from All Adjustment Seats"
}
VOTE_MEASURES = {
    "sim_votes":  "votes in simulations",
    "sim_shares": "shares in simulations",
}
AGGREGATES = {
    "cnt": "Number of elements",
    "max": "Max",
    "min": "Min",
    "sum": "Sum of elements",
    "sm2": "Sum of squares",
    "sm3": "Sum of cubes",
    "sm4": "Sum of fourth powers",
    "avg": "Average",
    "var": "Variance",
    "std": "Std. dev",
    "skw": "Skewness",
    "kur": "Kurtosis",
}
