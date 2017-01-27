# Voting system simulator

This is a voting system simulator intended to simulate various methods used in proportional voting systems, in particular those that use a biproportional apportionment method for allocation of adjustment seats based on national outcomes. Such systems are common, such as in Iceland, Sweden, and Norway.

[M.L. Balinski and G. Demange][1] have shown that only one method, the Alternating-Scaling method, exists that upholds the five axioms for proportionality in matrices. All other methods are heuristic simplifications that approach the optimal solution to varying degrees. This software implements the Alternating-Scaling method, and various other methods for comparison, and provides mechanisms to compare them.

Biproportional allocation on matrices is a common issue that arises when you have multiple parties in multiple constituencies vying for a set number of seats which are pinned to different constituencies. The goal is to determine which parties get which seats in which constituencies.

More generally this approach could be used to allocate limited resources to factories depending on their relative importance or needs, or to solve a number of other biproportional optimization problems.


## Usage

For help, try:
```
python cli.py --help
```

A few usage examples follow below.

### Apportionment

Basic apportioning is done through the `apportion` command. For help with that command, do:
```
python cli.py apportion --help
```
The `apportion` command takes several flags, including:

 * *constituencies*: path to a CSV file describing constituencies.
 * *votes*: path to a CSV file containing votes.
 * *divider*: the name of a supported divider method.
 * *adjustment-divider*: a supported divider method to use for adjustment seats; defaults to the same as the selected divider method.
 * *adjustment-method*: a supported adjustment method to use for resolving adjustment seat apportionment. Use multiple times to compare outputs.
 * *output*: the output format to use.
 * *show-entropy*: show the calculated entropy of each method.

Example using the 2013 elections in Iceland and d'Hondt method:
```
python cli.py apportion \
	--constituencies=../data/constituencies/constituencies_iceland_2013.csv \
	--votes=../data/elections/island_2013.csv \
	--divider=dhondt \
	--adjustment-method=alternating-scaling \
	--show-entropy
```

You can get HTML, LaTeX, MediaWiki or various other types of table output, swap out the divider methods as you please, and list multiple adjustment methods to compare:
```
python cli.py apportion \
	--constituencies=../data/constituencies/constituencies_iceland_2013.csv \
	--votes=../data/elections/island_2013.csv \
	--divider=sainte-lague \
	  --adjustment-method=alternating-scaling \
	  --adjustment-method=relative-superiority \
	--output=html
```

### Simulation

This feature is incomplete.


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
 * [ ] Optimization and heuristic methods
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

### Tickets
_(updated 2017-01-04)_

 * Smári:
   * [x] Update documentation
   * [x] Refactor codebase
   * [ ] Complete Icelandic law method
   * [ ] Complete simulation basis
   * [ ] Add vote-fuzzing support

 * Þorkell:
   * [ ] Figure out algorithms for detecting violations of Balinski axioms
   * [ ] Describe algorithm for Norwegian method
   * [ ] Review Relative Inferiority method

 * Kurt:
   * [ ] Describe algorithm for Swedish method

## Authors

Smári McCarthy, Þorkell Helgason and Kurt Jörnsten

## Licence

Released under the terms of the Affero GNU General Public License version 3.


 [1]: https://hal.archives-ouvertes.fr/hal-00686748/document
