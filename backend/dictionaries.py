
from division_rules import dhondt_gen, sainte_lague_gen, \
    nordic_sainte_lague_gen, imperiali_gen, danish_gen, huntington_hill_gen



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
