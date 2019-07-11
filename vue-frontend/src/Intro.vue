<template>
<b-container>
  <h1>Voting system simulator</h1>

  <span>
    Version: 1.1.6 Time of release: 2019.07.11-21:15 (GMT)
  </span>

  <p>
    Hello! This is a voting system simulator.
    Above, you can go to <b><a href="#/calc">Calculator</a></b>.
    For instructions on how to use it, read below.
  </p>

  <h2>About</h2>
  <p>
    The aim of this software is to help people understand
    how certain types of electoral systems work under various conditions.
    It provides tools to calculate election results for certain systems
    and review various metrics for these systems under simulation.
  </p>
  <p>
    This software is free to use for experimental purposes,
    and is free/open source software,
    available from <a href="https://github.com/smari/voting/">Github</a>.
    If you are using it for commercial or political reasons,
    please contact us to discuss supporting our project financially.
  <p>
    The voting system simulator is made by:
  </p>
  <ul>
    <li>Smári McCarthy (smarim@althingi.is)</li>
    <li>Þorkell Helgason (thorkellhelga@gmail.com)</li>
    <li>Martha Guðrún Bjarnadóttir</li>
    <li>Pétur Ólafur Aðalgeirsson</li>
    <li>Helgi Hrafn Gunnarsson</li>
    <li>Bjartur Thorlacius</li>
  </ul>

  <h2>How to use the calculator</h2>

  <p>
    The calculator has two modes: Single election and Simulation.
    But both modes share some common settings.
    You need to specify <b>electoral system settings</b>
    along with information about the <b>constituencies</b> in the country,
    the <b>parties</b> running in the election,
    and the <b>votes</b> each party got in each constituency.
  </p>
  <p>
    When specifying an <i>electoral system</i>,
    you have a lot of different options to choose from ─
    for a deeper understanding of these,
    you should read our guides on
    <b><a title="Coming soon." data-href="#/dividers">
      divider rules
    </a></b>
    and
    <b><a title="Coming soon." data-href="#/adjustmentmethods">
      adjustment methods
    </a></b>
    once we finish adding those.
  </p>
  <p>
    You can manually edit the vote table,
    adding or removing rows for constituencies and columns for parties,
    naming the constituencies and parties
    (and giving the table itself a name while you're at it,
    to help you distinguish results of one table from the next),
    specifying how many constituency seats or adjustment seats
    should be allocated to each constituency
    and last but not least,
    supplying the vote counts to base the calculations on.
    You can save your specified vote table to a file
    to reuse at a later time,
    so you won't have to pick this in every time.
  </p>
  <p>
    Alternatively, you can upload a file
    to automatically populate the vote table,
    for example from a previously saved vote table.
    In addition, you can choose from among some
    predefined vote tables to load.
    For your convenience, we have supplied results
    from all Icelandic elections of the current century.
  </p>

  <h3>Single Election</h3>

  <p>
    <b>Single Election</b> allows you
    to calculate the results of a single election.
  </p>
  <p>
    As you update the <b>electoral system settings</b> and <b>vote table</b>,
    the result will be automatically calculated
    and the results displayed below.
  </p>
  <p>
    You can also download an .xlsx file with the results.
  </p>

  <h3>Simulation</h3>

  <p>
    The <b>Simulation</b> function allows you
    to run hundreds or even thousands of elections,
    each differing slightly from the last,
    in order to gain insights into the behaviour
    of different <i>electoral systems</i>.
  </p>
  <p>
    You must provide at least one <b>electoral system</b> to be considered,
    but you can have as many as you'd like.
    By setting up several different systems,
    you can <i>compare</i> the statistical behaviour
    to see which systems do best under certain test conditions.
    The results are displayed in the form of
    several different <b><a href="#/qualitymeasures">quality measures</a></b>,
    each with their own interpretation.
  </p>
  <p>
    The <b>vote table</b> you supply will be used
    as a reference on which to base
    the statistical distribution of the randomly generated votes
    for each round of the simulation.
    At the moment, the only implemented distribution is the beta distribution,
    in which case the simulation votes are generated
    by adding a random fluctuation to the votes for each candidate list,
    such that the average will tend to coincide with
    the votes from the supplied vote table.
  </p>
  <p>
    In addition to this,
    you must decide how many rounds of simulation to run.
    A high number will take more time to calculate,
    but provide more significance to the statistics.
    For the beta distribution,
    you can also specify how widely the random generated votes should fluctuate.
  </p>
  <p>
    Once you start the simulation,
    the results will be displayed below,
    as well as some quality measures.
  </p>
  <p>
    You can also download an .xlsx file with the results,
    even while the simulation is still running
    (it will just contain statistics on the simulation so far).
  </p>

  <h2>Documentation</h2>
  <ul>
    <li><a href="https://github.com/smari/voting/raw/master/doc/2018-09-10-kosningakerfishermir-kynning.pdf">Presentation at Reykjavík University 2018-09-10. (In Icelandic)</a></li>
  </ul>

</b-container>
</template>
