
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
    "imperiali": "Imeriali method",
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
