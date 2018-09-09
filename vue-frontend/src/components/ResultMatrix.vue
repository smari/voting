<template>
  <b-container>
    <table class="resultmatrix" v-if="values.length > 0">
      <tr v-if="title">
        <th class="small-12 medium-1 topleft"></th>
        <th :colspan="stddev?2*parties.length:parties.length">
          {{title}}
        </th>
      </tr>
      <tr class="parties">
        <th class="small-12 medium-1 topleft"></th>
        <th :colspan="stddev?2:1" v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyname">
          {{ parties[partyidx] }}
        </th>
      </tr>
      <tr v-if="stddev" class="parties">
        <th class="small-12 medium-1 topleft"></th>
        <template v-for="(party, partyidx) in parties">
          <td class="small-12 medium-1 column partyseats">Average</td>
          <td class="small-12 medium-1 column partyseats">Stddev</td>
        </template>
      </tr>
      <tr v-for="(constituency, conidx) in constituencies">
        <th class="small-12 medium-1 column constname">
          {{ constituencies[conidx] }}
        </th>
        <template v-for="(party, partyidx) in parties">
          <td class="small-12 medium-2 column partyseats">
            {{ values[conidx][partyidx].toFixed(round) }}
          </td>
          <td v-if="stddev" class="small-12 medium-2 column partyseats">
            {{ stddev[conidx][partyidx].toFixed(round) }}
          </td>
        </template>
      </tr>
      <tr>
        <th class="small-12 medium-1 column bottomleft">Total</th>
        <template v-for="(party, partyidx) in parties">
          <td class="small-12 medium-1 column partyseats">
            {{ values[constituencies.length][partyidx].toFixed(round) }}
          </td>
          <td v-if="stddev" class="small-12 medium-1 column partyseats">
            {{ stddev[constituencies.length][partyidx].toFixed(round) }}
          </td>
        </template>
      </tr>
    </table>
  </b-container>
</template>
<script>
export default {
  props: {
    "constituencies": { default: [] },
    "parties": { default: [] },
    "values": { default: [] },
    "round": { default: 0 },
    "stddev": { default: false },
    "title": { default: "" },
  }
}
</script>
