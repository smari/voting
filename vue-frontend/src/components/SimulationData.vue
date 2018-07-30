<template>
  <b-container>
  <b-alert :show="measures.length==0">No quality measures found.</b-alert>
  <table class="simulationdata">
    <tr class="methods">
      <th class="small-12 medium-1 topleft">
      </th>
      <th v-for="(method, methodidx) in methods" class="small-12 medium-1 column methodname">
        {{ methods[methodidx] }}
      </th>
    </tr>
    <tr v-for="(measure, measureidx) in measures">
      <th class="small-12 medium-1 column measurename">
          {{ measures[measureidx] }}
      </th>
      <td v-for="(method, methodidx) in methods" class="small-12 medium-2 column methodnumbers">
          {{ numbers[measureidx] }}
      </td>
    </tr>
  </table>
</b-container>
</template>
<script>
export default {
  props: ["measures", "methods", "numbers"]
}
</script>
