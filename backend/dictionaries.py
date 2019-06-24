
from division_rules import dhondt_gen, sainte_lague_gen, \
    nordic_sainte_lague_gen, imperiali_gen, danish_gen, huntington_hill_gen

from methods.var_alt_scal import var_alt_scal
from methods.alternating_scaling import alternating_scaling
from methods.icelandic_law import icelandic_apportionment
from methods.monge import monge
from methods.nearest_neighbor import nearest_neighbor
from methods.relative_superiority import relative_superiority
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
    "imperiali": "Imperiali method",
    "danish": "Danish method",
    "huntington-hill": "Huntington-Hill method",
}

ADJUSTMENT_METHODS = {
    "var-alt-scal": var_alt_scal,
    "alternating-scaling": alternating_scaling,
    "relative-superiority": relative_superiority,
    "nearest-neighbor": nearest_neighbor,
    "monge": monge,
    "icelandic-law": icelandic_apportionment,
    "norwegian-law": norwegian_apportionment,
    "norwegian-icelandic": norw_ice_apportionment,
    "opt-entropy": opt_entropy,
    "switching": switching,
    "pure-vote-ratios": pure_vote_ratios_apportionment,
}
ADJUSTMENT_METHOD_NAMES = {
    "alternating-scaling": "Alternating-Scaling Method",
    "relative-superiority": "Relative Superiority Method",
    "nearest-neighbor": "Nearest Neighbor Method",
    "monge": "Monge algorithm",
    "icelandic-law": "Icelandic law 24/2000 (Kosningar til Alþingis)",
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

MEASURES = {
    "dev_opt":         "Allocation by the optimal method",
    "dev_law":         "Allocation by Icelandic Law",
    "adj_dev":         "Adjustment seats apportioned nationally",
    "dev_ind_const":   "Allocation as if all seats were constituency seats",
    "dev_all_adj":     "Allocation as if all seats were adjustment seats",
    "dev_one_const":   "Allocation as if all constituencies were combined into one",
    "entropy":         "Entropy (product of all seat values used)",
    "entropy_ratio":   "Relative entropy deviation from optimal solution",
    "loosemore_hanby": "Proportionality index according to Loosemore-Hanby (adjusted to biproportionality)",
    "sainte_lague":    "Scaled sum of squared deviation of list seats from biproportional seat shares (Sainte-Lague)",
    "dhondt_min":      "Mininum seat value used (d'Hondt)",
    "dhondt_sum":      "Scaled sum of positive deviation of list seats from biproportional seat shares (d'Hondt)",
}
DEVIATION_MEASURES = [
    "dev_opt",
    "dev_law",
    "adj_dev",
    "dev_ind_const",
    "dev_all_adj",
    # "dev_one_const", #skipped, because already measured by all_adj (party sums)
]
STANDARDIZED_MEASURES = [
    "entropy_ratio",
    "loosemore_hanby",
    "sainte_lague",
    "dhondt_min",
    "dhondt_sum",
]
LIST_MEASURES = {
    "const_seats":   "constituency seats",
    "adj_seats":     "adjustment seats",
    "total_seats":   "constituency and adjustment seats combined",
    "seat_shares":   "total seats scaled to a total of 1 for each constituency",
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
    "cnt": "number of elements",
    "max": "highest value",
    "min": "lowest value",
    "sum": "sum of elements",
    "sqs": "sum of squares",
    "avg": "average",
    "var": "variance",
    "std": "standard deviation"
}
