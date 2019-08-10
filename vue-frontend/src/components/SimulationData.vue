<template>
<b-container fluid>
  <b-alert :show="methods.length == 0">
    Run simulation to get results.
  </b-alert>
  <table v-if="data.length > 0" class="simulationdata">
    <tr class="methods">
      <th class="small-12 medium-1 topleft">
      </th>
      <th colspan="6"
        v-for="(ruleset, idx) in data"
        class="small-12 medium-1 column methodname"
      >
        <div>{{ ruleset.name }}</div>
      </th>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">Adjustment method</th>
      <td colspan="6"
        class="small-12 medium-2 column methoddata"
        v-for="(ruleset, idx) in data"
      >
        {{ruleset.method}}
      </td>
    </tr>
    <tr>
      <th class="small-12 medium-1 topleft"></th>
      <template v-for="(ruleset, ridx) in data">
        <th class="small-12 medium-2 column methodname">Average</th>
        <th class="small-12 medium-2 column methodname">Min</th>
        <th class="small-12 medium-2 column methodname">Max</th>
        <th class="small-12 medium-2 column methodname">Std. deviation</th>
        <th class="small-12 medium-2 column methodname">Skewness</th>
        <th class="small-12 medium-2 column methodname">Kurtosis</th>
      </template>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">
        <div>Comparison to other seat allocations</div>
      </th>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">
        <div>Sum of absolute differences of tested method and:</div>
      </th>
    </tr>
    <tr v-for="midx in deviation_measures">
      <td class="small-12 medium-1 column measurename">
          {{ measures[midx] }}
      </td>
      <template v-for="(ruleset, ridx) in data">
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["avg"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["min"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["max"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["std"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["skw"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["kur"].toFixed(4) }}
        </td>
      </template>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">
        <div>Quality indices (the higher the better):</div>
      </th>
    </tr>
    <tr v-for="midx in standardized_measures">
      <td class="small-12 medium-1 column measurename">
          {{ measures[midx] }}
      </td>
      <template v-for="(ruleset, ridx) in data">
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["avg"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["min"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["max"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["std"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["skw"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["kur"].toFixed(4) }}
        </td>
      </template>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">
        <div>Comparison to ideal seat shares (the lower the better):</div>
      </th>
    </tr>
    <tr v-for="midx in ideal_comparison_measures">
      <td class="small-12 medium-1 column measurename">
          {{ measures[midx] }}
      </td>
      <template v-for="(ruleset, ridx) in data">
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["avg"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["min"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["max"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["std"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["skw"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["kur"].toFixed(4) }}
        </td>
      </template>
    </tr>
  </table>
</b-container>
</template>
<script>
export default {
  props: [
    "testnames",
    "measures",
    "deviation_measures",
    "standardized_measures",
    "ideal_comparison_measures",
    "methods",
    "data"
  ]
}
</script>
