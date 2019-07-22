<template>
  <b-container fluid v-if="table.steps.length > 0">
    <h3>Step-by-step demonstration of adjustment seat allocations</h3>
    <table class="demomatrix">
      <tr>
        <th v-for="header in table.headers">
          {{ header }}
        </th>
      </tr>
      <tr v-for="(step, stepidx) in table.steps">
        <template v-for="(col, colidx) in step">
          <td>
            {{ col }}
          </td>
        </template>
      </tr>
    </table>
  </b-container>
</template>
<script>
export default {
  props: {
    "table": { default: { "headers": [], "steps": [] } },
  }
}
</script>
