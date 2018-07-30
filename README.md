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

 * *constituencies*: path to a CSV or XLSX file describing constituencies.
 * *votes*: path to a CSV or XLSX file containing votes.
 * *divider*: the name of a supported divider method.
 * *adjustment-divider*: a supported divider method to use for adjustment seats; defaults to the same as the selected divider method.
 * *adjustment-method*: a supported adjustment method to use for resolving adjustment seat apportionment. Use multiple times to compare outputs.
 * *output*: the output format to use.
 * *show-entropy*: show the calculated entropy of each method.

Example using the 2013 elections in Iceland and d'Hondt method:
```
python cli.py apportion \
	--constituencies=../data/constituencies/constituencies_iceland_2013.csv \
	--votes=../data/elections/iceland_landskjorstjorn_2013.csv \
	--divider=dhondt \
	--adjustment-method=alternating-scaling \
	--show-entropy
```

You can get HTML, LaTeX, MediaWiki or various other types of table output and swap out the divider methods as you please:
```
python cli.py apportion \
	--constituencies=../data/constituencies/constituencies_iceland_2013.csv \
	--votes=../data/elections/iceland_landskjorstjorn_2013.csv \
	--divider=sainte-lague \
    --adjustment-method=monge \
	--output=html
```

### Simulation

Simulation is done through the `simulate` command. For help with that command, do:
```
python cli.py simulate --help
```
The `simulate` command takes several flags, including:

 * *constituencies*: path to a CSV or XLSX file describing constituencies.
 * *votes*: path to a CSV or XLSX file containing votes to use as reference for the simulation.
 * *test_method*: the method to be tested.
 * *num_sim*: number of simulations to run.
 * *gen_method*: a supported method to generate votes.

 Example using the 2013 elections in Iceland:
```
python cli.py simulate \
	--constituencies=../data/constituencies/constituencies_iceland_2013.csv \
	--votes=../data/elections/iceland_landskjorstjorn_2013.csv \
	--test_method=ice_law_dhondt
```

### Script mode

Because all the parameters can be confusing and sometimes you just want
to be able to work with a particular set of settings again and again,
there is a "script mode" (for lack of a better term) which allows you to
specify a set of rules which then execute:

```
python cli.py script ../data/presets/iceland2013.json
```

A script or preset is simply a JSON file that specifies what should
happen, see examples in `data/presets/`.


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

The SPA is currently being refactored using [create-react-app](https://github.com/facebookincubator/create-react-app) which is located in the [ui](https://github.com/smari/voting/tree/master/ui) directory.

## Features

### Basic functionality

* [x] Read constituency data files
* [x] Read vote data files
* [x] Basic click UI
* [x] Per ruleset click UI options
* [x] Simulation click UI options
* [x] Web server

### Apportionment methods

 * [x] One dimensional greedy apportionment
   * [x] d'Hondt method
   * [x] Sainte-Lague method
   * [x] Nordic Sainte-Lague method
 * [x] Constituency seat allocation
 * [x] Threshold elimination (on matrices and vectors)
 * [ ] Optimization and heuristic methods
   * [ ] Linear programming
   * [x] Greedy Alternating-Scaling algorithm (AS)
   * [x] Alternating-Scaling algorithm (AS)
   * [x] Relative Superiority algorithm (RS)
   * [ ] Relative Inferiority algorithm (RI)
   * [x] Nearest neighbor algorithm
   * [x] Monge algorithm
   * [x] Icelandic voting law algorithm
   * [ ] Swedish voting law algorithm
   * [x] Norwegian voting law algorithm
   * [x] Norwegian voting law algorithm adjusted for Icelandic conditions
   * [x] Kristinn Lund method

### Simulation

* [x] Generate random initial votes
	* Draw percentages for each party in each district from a beta distribution with historical mean and variance. Then normalize the percentages to add up to 100\%.
* [ ] Fuzz votes
	* Add votes, one-by-one, in support of a party list in a district
		* If a new vote doesn't gain that party list a seat, report any change in results.
		* Even if a new vote does gain that party list a seat, do report if the result change is greater than just moving a seat in the relevant constituency between parties and moving one seat in the opposite direction in another constituency.
* [x] Compare different apportionment methods

### Evaluation of methods

 * [x] Apportionment entropy
 * [x] Entropy relative to optimal entropy
 * [x] Seat deviation from optimal solution
 * [x] Seat deviation from Icelandic law
 * [x] Seat deviation from independent constituencies
 * [x] Seat deviation from single constituency country
 * [x] Seat deviation from all seats apportioned with adjustment method
 * [x] Loosemore-Hanby index
 * [x] Sainte-Lague minsum index
 * [x] d'Hondt maxmin index
 * [x] d'Hondt minsum index
 * [ ] _Monotonicity violation_: A party list losing a seat by receiving an additional vote
 * [ ] _Significant irrelevant alternative_: A new vote having side effects without without affecting the number of seats won by the party list voted for.

### Output formats

- [x] Simple text result table (Total seats) output
- [x] HTML, LaTeX, CSV, result table (Total seats) output
- [x] Excel file detailed result output
  - [x] Votes
  - [x] Vote shares
  - [x] Constituency seats
  - [x] Adjustment seats
  - [x] Total seats
  - [ ] Evaluation metrics

### Web interface

 * [x] Simple web server
 * [ ] Javascript SPA
    * [x] Configurable running of single elections
    * [x] Configurable running of simulations
    * [ ] Display results
       * [x] Votes
       * [ ] Vote shares
       * [ ] Constituency seats
       * [ ] Adjustment seats
       * [x] Total seats
       * [x] Evaluation metrics
    * [ ] Visualizations
       * [ ] "Election TV" result animations
      * [ ] Simulation errors
      * [ ] 3D bar chart of cumulative violations in the constituency/party matrix
 * [x] Configurable host/port/etc

### Tickets

See [our issue tracker on Github](https://github.com/smari/voting/issues).


## Authors

Smári McCarthy, Þorkell Helgason and Kurt Jörnsten.

Contributions from Pétur Ólafur Aðalgeirsson, Helgi Hrafn Gunnarsson and
Bjartur Thorlacius.

## Licence

Released under the terms of the Affero GNU General Public License version 3.


[1]: https://hal.archives-ouvertes.fr/hal-00686748/document
