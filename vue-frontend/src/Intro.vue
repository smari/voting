<template>
<b-container>
  <h1>Voting system simulator</h1>

  <p>
  Hello! This is a voting system simulator. Above, you can choose between two modes: <b><a href="#/election">Single Election</a></b> and <b><a href="#/simulate">Simulate</a></b>.
  </p>

  <h2>Single Election</h2>

  <p>
    <b><a href="#/election">Single Election</a></b> allows you to calculate the results of a single election. You need to provide <b>election rules</b> along with information about the <b>constituencies</b> in the country, the <b>parties</b> running in the election, and the <b>votes</b> each party got in each constituency.
  </p>
  <p>
    As you update these values, the result will be automatically calculated and the results displayed below.
  </p>
  <p>
    When choosing the <i>election rules</i>, you have a lot of different options to choose from ─ for a deeper understanding of these, you should read our guides on <b><a href="#/dividers">divider rules</a></b> and <b><a href="#/adjustmentmethods">adjustment methods</a></b>.
  </p>

  <h2>Simulate</h2>

  <p>
    The <b><a href="#/simulate">Simulate</a></b> function allows you to run hundreds or even thousands of elections, each differing slightly from the last, in order to gain insights into the behaviour of different <i>voting systems</i>.
  </p>

  <p>
    By setting up several different systems, you can <i>compare</i> the statistical behaviour to see which systems do best under certain test conditions. The results are displayed in the form of several different <b><a href="#/qualitymeasures">quality measures</a></b>, each with their own interpretation.
  </p>

  <p>
    As with running a single election, you must provide information about the <b>constituencies</b> in the country, the <b>parties</b> running in the election, and the <b>votes</b> each party got in each constituency.
  </p>

  <p>
    In addition to this, you must provide at least one set of <b>election rules</b> to be considered, but you can have as many rules as you'd like.
  </p>

  <p>
    When choosing the <i>election rules</i>, you have a lot of different options to choose from ─ for a deeper understanding of these, you should read our guides on <b><a href="#/dividers">divider rules</a></b> and <b><a href="#/adjustmentmethods">adjustment methods</a></b>.
  </p>

</b-container>
</template>
