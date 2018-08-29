<template>
  <b-container>
    <table class="resultmatrix" v-if="seats.length > 0">
      <tr class="parties">
        <th class="small-12 medium-1 topleft"></th>
        <th :colspan="variance?2:1" v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyname">
          {{ parties[partyidx] }}
        </th>
      </tr>
      <tr v-if="variance" class="parties">
        <th class="small-12 medium-1 topleft"></th>
        <template v-for="(party, partyidx) in parties">
          <td class="small-12 medium-1 column partyseats">Average</td>
          <td class="small-12 medium-1 column partyseats">Variance</td>
        </template>
      </tr>
      <tr>
        <th class="small-12 medium-1 topleft"></th>
        <template v-for="(party, partyidx) in parties">
          <td class="small-12 medium-1 column partyseats">
            {{ seatssum[partyidx].toFixed(round) }}
          </td>
          <td v-if="variance">&nbsp;</td>
        </template>
      </tr>
      <tr v-for="(constituency, conidx) in constituencies">
        <th class="small-12 medium-1 column constname">
            {{ constituencies[conidx] }}
        </th>
        <template v-for="(party, partyidx) in parties">
          <td class="small-12 medium-2 column partyseats">
              {{ seats[conidx][partyidx].toFixed(round) }}
          </td>
          <td v-if="variance" class="small-12 medium-2 column partyseats">
              {{ variance[conidx][partyidx].toFixed(round) }}
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
    "seats": { default: [] },
    "round": { default: 0 },
    "variance": { default: false }
  },
  computed: {
    seatssum: function() {
      let seats = Array(this.parties.length).fill(0);
      for (let c in this.seats) {
        seats = this.seats[c].map(function (num, idx) {
          return seats[idx]+num;
        });
      }
      return seats;
    }
  }
}
</script>
