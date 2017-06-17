# Voting system simulator

This is a voting system simulator intended to simulate various methods used in proportional voting systems, in particular those that use a biproportional apportionment method for allocation of adjustment seats based on national outcomes. Such systems are common, such as in Iceland, Sweden, and Norway.

[M.L. Balinski and G. Demange][1] have shown that only one method, the Alternating-Scaling method, exists that upholds the five axioms for proportionality in matrices. All other methods are heuristic simplifications that approach the optimal solution to varying degrees. This software implements the Alternating-Scaling method, and various other methods for comparison, and provides mechanisms to compare them.

Biproportional allocation on matrices is a common issue that arises when you have multiple parties in multiple constituencies vying for a set number of seats which are pinned to different constituencies. The goal is to determine which parties get which seats in which constituencies.

More generally this approach could be used to allocate limited resources to factories depending on their relative importance or needs, or to solve a number of other biproportional optimization problems.


## Command Line Interface

The basic interaction mode. You feed it some data files, it feeds you some results.

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

### Script mode

Because all the parameters can be confusing and sometimes you just want
to be able to work with a particular set of settings again and again,
there is a "script mode" (for lack of a better term) which allows you to
specify a set of rules which then execute:

```
python cli.py script ../data/rulesets/iceland2013.json
```

A script or ruleset is simply a JSON file that specifies what should
happen, see examples in `data/rulesets/`.


## Web Interface

The web interface can be started by:

```
python web.py
```

Then direct a browser to `http://localhost:5000/` and start having fun.

### Design

The web interface involves a Javascript Single Page App (SPA) which acts as a
visual editor for data that is then passed to the backend for calculations. As
such, the SPA is the source of truth, and the backend is "dumb", merely reacting
to the frontend. The backend is made with Flask.

The SPA's data model should be the same as the backend's script-mode input model.

The SPA is built using React and Bootstrap. It contains a bit of JQuery glue
that should go away eventually.


## Features

### Basic functionality

* [x] Read constituency data files
* [x] Read vote data files
* [x] Basic click UI
* [x] Per ruleset click UI options

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
   * [x] Icelandic voting law algorithm
   * [ ] Swedish voting law algorithm
   * [ ] Norwegian voting law algorithm

### Simulation

* [ ] Generate random initial votes
	* Draw percentages for each party in each district from a beta distribution with historical mean and variance. Then normalize the percentages to add up to 100\%.
* [ ] Fuzz votes
	* Add votes, one-by-one, in support of a party list in a district
		* If a new vote doesn't gain that party list a seat, report any change in results.
		* Even if a new vote does gain that party list a seat, do report if the result change is greater than just moving a seat in the relevant constituency between parties and moving one seat in the opposite direction in another constituency.
* [ ] Resolve ties
* [ ] Compare different methods

### Evaluation of methods

 * [x] Entropy measurement
 * [ ] _Comparative error estimation_: count number of seat-flips from optimal
 * [ ] _Monotonicity violation_: A party list losing a seat by receiving an additional vote
 * [ ] _Significant irrelevant alternative_: A new vote having side effects without without affecting the number of seats won by the party list voted for.

### Web interface

 * [x] Simple web server
 * [x] Javascript SPA
 * [ ] Configurable host/port/etc

### Visualization

 * [ ] "Election TV" result animations
 * [ ] Simulation errors
   * [ ] 3D bar chart of cumulative violations in the constituency/party matrix

### Tickets
_(updated 2017-06-17)_

 * Smári:
   * [x] Update documentation
   * [x] Refactor codebase
   * [x] Complete Icelandic law method
   * [x] Complete simulation basis
   * [ ] Get JS-SPA to feature-complete

 * Þorkell:
   * [ ] Figure out algorithms for detecting violations of Balinski axioms
   * [x] Describe algorithm for Norwegian method
   * [ ] Review Relative Inferiority method

 * Kurt:
   * [ ] Describe algorithm for Swedish method

 * Bjartur:
   * [ ] Generate random votes

## Authors

Smári McCarthy, Þorkell Helgason and Kurt Jörnsten.

Contributions from Pétur Ólafur Aðalgeirsson, Helgi Hrafn Gunnarsson and
Bjartur Thorlacius.

## Licence

Released under the terms of the Affero GNU General Public License version 3.


 [1]: https://hal.archives-ouvertes.fr/hal-00686748/document
