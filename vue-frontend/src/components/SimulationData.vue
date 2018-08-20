<template>
  <b-container>
  <b-alert :show="methods.length == 0">
    Run simulation to get results.
  </b-alert>
  <table v-if="methods.length != 0" class="simulationdata">
    <tr class="methods">
      <th class="small-12 medium-1 topleft">
      </th>
      <th v-for="(testname, idx) in testnames" class="small-12 medium-1 column methodname">
        <div>{{ testname }}</div>
      </th>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">Adjustment method</th>
      <td class="small-12 medium-2 column methoddata" v-for="(method, methodidx) in methods">{{method}}</td>
    </tr>
    <tr v-for="(measure, measureidx) in measures">
      <th class="small-12 medium-1 column measurename">
          {{ measures[measureidx] }}
      </th>
      <td v-for="(method, methodidx) in methods" class="small-12 medium-2 column methoddata">
          {{ data[measureidx][methodidx].toFixed(2) }}
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
