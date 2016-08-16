# Voting system simulator

This is a voting system simulator intended to simulate various methods used in proportional voting
systems, in particular those that use a biproportional apportionment method for allocation of
adjustment seats based on national outcomes. Such systems are common, such as in Iceland, Sweden,
and Norway.


## Usage

Example using the 2013 elections in Iceland and d'Hondt method:
```
python cli.py apportion \
	--constituencies=../data/constituencies/constituencies_iceland_2013.csv \
	--votes=../data/elections/island_2013.csv \
	--divider=dhondt
	--method=alternating-scaling --method=relative-superiority
	--show-entropy
	--output=simple
```

For help, try:
```
python cli.py --help
```

## Features

 * [x] d'Hondt method
 * [x] Sainte-Lague method
 * [x] Nordic Sainte-Lague method
 * [x] One dimensional greedy apportionment
 * [x] Constituency seat allocation
 * [x] Read constituency data files
 * [x] Read vote data files
 * [x] Threshold elimination (on matrices and vectors)
 * [x] Alternating-Scaling Algorithm (AS)
 * [x] Relative Superiority Algorithm (RS)
 * [ ] Relative Inferiority Algorithm (RI)
 * [ ] Icelandic voting law algorithm
 * [ ] Swedish voting law algorithm
 * [ ] Norwegian voting law algorithm
 * [x] Entropy measurement
 * [ ] Comparative error estimation
 * [ ] Election fuzzing
 * [ ] Monotonicty violation detection
 * [x] Basic click UI
 * [ ] Per ruleset click UI options
 * [ ] Compare multiple rulesets

## Authors

Smári McCarthy, Þorkell Helgason and Kurt Jörnsten

## Licence

Released under the terms of the Affero GNU General Public License version 3.
