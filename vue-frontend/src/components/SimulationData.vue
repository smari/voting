<template>
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
          {{ numbers[measureidx][methodidx] }}
      </td>
    </tr>
  </table>
</template>
<script>
export default {
  data: function () {
    return {
      measures: ["Entropy", "Entropy Ratio", "Dev Opt", "Dev Law", "Dev Ind Const", "Dev One Country", "Dev Tot Eq", "LH", "StL", "dHmin", "dHsum"],
      methods: ["Alternating Scaling", "Icelandic Law", "Relative superiority"],
      numbers: [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    }
  },
}
</script>
