<template>
  <b-container>
  <b-alert :show="methods.length == 0">
    Run simulation to get results.
  </b-alert>
  <table v-if="data.length > 0" class="simulationdata">
    <tr class="methods">
      <th class="small-12 medium-1 topleft">
      </th>
      <th colspan="2" v-for="(measure, idx) in data" class="small-12 medium-1 column methodname">
        <div>{{ measure.name }}</div>
      </th>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">Adjustment method</th>
      <td colspan="2" class="small-12 medium-2 column methoddata" v-for="(measure, idx) in data">{{measure.name}}</td>
    </tr>
    <tr>
      <th class="small-12 medium-1 topleft"></th>
      <template v-for="(test, tidx) in data">
        <th class="small-12 medium-2 column methodname">Average</th>
        <th class="small-12 medium-2 column methodname">Variance</th>
      </template>
    </tr>
    <tr v-for="(measure, midx) in measures">
      <th class="small-12 medium-1 column measurename">
          {{ measure }}
      </th>
      <td v-for="(test, testidx) in data" class="small-12 medium-2 column methoddata">
        {{ data[testidx]["measures"][midx]["avg"].toFixed(4) }}
      </td>
      <td v-for="(test, testidx) in data" class="small-12 medium-2 column methoddata">
        {{ data[testidx]["measures"][midx]["var"].toFixed(4) }}
      </td>
    </tr>
  </table>
</b-container>
</template>
<script>
export default {
  props: ["testnames", "measures", "methods", "data"]
}
</script>
