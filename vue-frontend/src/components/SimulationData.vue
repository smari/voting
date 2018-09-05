<template>
  <b-container>
  <b-alert :show="methods.length == 0">
    Run simulation to get results.
  </b-alert>
  <table v-if="data.length > 0" class="simulationdata">
    <tr class="methods">
      <th class="small-12 medium-1 topleft">
      </th>
      <th colspan="2" v-for="(ruleset, idx) in data" class="small-12 medium-1 column methodname">
        <div>{{ ruleset.name }}</div>
      </th>
    </tr>
    <tr>
      <th class="small-12 medium-1 column measurename">Adjustment method</th>
      <td colspan="2" class="small-12 medium-2 column methoddata"
        v-for="(ruleset, idx) in data">{{ruleset.method}}</td>
    </tr>
    <tr>
      <th class="small-12 medium-1 topleft"></th>
      <template v-for="(ruleset, ridx) in data">
        <th class="small-12 medium-2 column methodname">Average</th>
        <th class="small-12 medium-2 column methodname">Std. deviation</th>
      </template>
    </tr>
    <tr v-for="(measure, midx) in measures">
      <th class="small-12 medium-1 column measurename">
          {{ measure }}
      </th>
      <template v-for="(ruleset, ridx) in data">
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["avg"].toFixed(4) }}
        </td>
        <td class="small-12 medium-2 column methoddata">
          {{ data[ridx]["measures"][midx]["std"].toFixed(4) }}
        </td>
      </template>
    </tr>
  </table>
</b-container>
</template>
<script>
export default {
  props: ["testnames", "measures", "methods", "data"]
}
</script>
