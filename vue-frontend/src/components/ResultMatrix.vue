<template>
  <b-container>
    <table class="resultmatrix" v-if="seats.length > 0">
      <tr class="parties">
        <th class="small-12 medium-1 topleft"></th>
        <th v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyname">
          {{ parties[partyidx] }}
        </th>
      </tr>
      <tr>
        <th class="small-12 medium-1 topleft"></th>
        <td v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyseats">
          {{ seatssum[partyidx] }}
        </td>
      </tr>
      <tr v-for="(constituency, conidx) in constituencies">
        <th class="small-12 medium-1 column constname">
            {{ constituencies[conidx] }}
        </th>
        <td v-for="(party, partyidx) in parties" class="small-12 medium-2 column partyseats">
            {{ seats[conidx][partyidx] }}
        </td>
      </tr>
    </table>
  </b-container>
</template>
<script>
export default {
  props: ["constituencies", "parties", "seats"],
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
