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
	--adjustment-method=alternating-scaling --adjustment-method=relative-superiority
	--show-entropy
	--output=simple
```

For help, try:
```
python cli.py --help
```

## Features

### Basic functionality

* [x] Read constituency data files
* [x] Read vote data files
* [x] Basic click UI
* [ ] Per ruleset click UI options

### Apportionment methods

 * [x] One dimensional greedy apportionment
   * [x] d'Hondt method
   * [x] Sainte-Lague method
   * [x] Nordic Sainte-Lague method
 * [x] Constituency seat allocation
 * [x] Threshold elimination (on matrices and vectors)
 * Optimization and heuristic methods
   * [x] Alternating-Scaling Algorithm (AS)
   * [x] Relative Superiority Algorithm (RS)
   * [ ] Relative Inferiority Algorithm (RI)
   * [ ] Icelandic voting law algorithm
   * [ ] Swedish voting law algorithm
   * [ ] Norwegian voting law algorithm

### Simulation

* [ ] Election simulation: run multiple elections with varied inputs
* [ ] Fuzz votes based on Beta, Normal, and other random distributions
* [ ] Compare multiple rulesets (e.g. different adjustment seat vs constituency seat counts)

### Evaluation of methods

 * [x] Entropy measurement
 * [ ] Comparative error estimation: count number of seat-flips from optimal
 * [ ] Monotonicity violation detection
 * [ ] Independence of Irrelevant Alternatives violation detection
 * [ ] Balinski axiom violation detection
 * [ ] Method standoff: Rank evaluations (STV/Condorcet) amongst methods after simulation

### Visualization

 * [ ] "Election TV" result animations
 * [ ] Simulation errors
   * [ ] 3D bar chart of cumulative violations in the constituency/party matrix


## Authors

Smári McCarthy, Þorkell Helgason and Kurt Jörnsten

## Licence

Released under the terms of the Affero GNU General Public License version 3.
