<template>
  <b-container fluid class="votematrix-container">
    <b-button-toolbar key-nav aria-label="Vote tools">
      <b-button-group class="mx-1">
        <b-btn @click="addConstituency()">Add constituency</b-btn>
        <b-btn @click="addParty()">Add party</b-btn>
        <b-btn @click="clearVotes()">Clear votes</b-btn>
        <b-btn @click="clearAll()">Reset everything</b-btn>
      </b-button-group>
      <b-button-group class="mx-1">
        <b-button disabled>Upload XLSX</b-button>
        <b-button disabled>Upload CSV</b-button>
        <b-button disabled>Paste input</b-button>
        <b-dropdown id="ddown1" text="Presets" size="sm">
          <b-dropdown-item v-for="(preset, presetidx) in presets" :key="preset.name" @click="setPreset(presetidx)">{{preset.name}}</b-dropdown-item>
        </b-dropdown>
      </b-button-group>
      <b-button-group class="mx-1">
        <b-button disabled>Save voteset</b-button>
      </b-button-group>
    </b-button-toolbar>
    <table class="votematrix">
      <tr class="parties">
        <th class="small-12 medium-1 topleft">
          &nbsp;
        </th>
        <th>
          <abbr title="Constituency seats"># Cons.</abbr>
        </th>
        <th>
          <abbr title="Adjustment seats"># Adj.</abbr>
        </th>
        <th v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyname">
          <b-button size="sm" variant="link" @click="deleteParty(partyidx)">×</b-button>
          <input type="text" v-model="parties[partyidx]">
        </th>
      </tr>
      <tr v-for="(constituency, conidx) in constituencies">
        <th class="small-12 medium-1 column constname">
            <b-button size="sm" variant="link" @click="deleteConstituency(conidx)">×</b-button>
            <input type="text" v-model="constituencies[conidx]"></input>
        </th>
        <td class="small-12 medium-2 column partyvotes">
          <input type="text" v-model.number="constituency_seats[conidx]"></input>
        </td>
        <td class="small-12 medium-2 column partyvotes">
          <input type="text" v-model.number="constituency_adjustment_seats[conidx]"></input>
        </td>
        <td v-for="(party, partyidx) in parties" class="small-12 medium-2 column partyvotes">
            <input type="text" v-model.number="votes[conidx][partyidx]">
            </input>
        </td>
      </tr>
    </table>
  </b-container>
</template>
<script>
export default {
  data: function () {
    return {
      constituencies: ["I", "II"],
      constituency_seats: [10, 10],
      constituency_adjustment_seats: [2, 3],
      parties: ["A", "B"],
      votes: [[1500, 2000], [2500, 1700]],
      presets: {}
    }
  },
  created: function() {
    this.$http.get('/api/presets').then(response => {
      this.presets = response.body;
    }, response => {
      this.$emit('server-error', response.body);
    });
    this.$emit('update-constituencies', this.constituencies, false);
    this.$emit('update-parties', this.parties, false);
    this.$emit('update-votes', this.votes, false);
    this.$emit('update-constituency-seats', this.constituency_seats, false);
    this.$emit('update-adjustment-seats', this.constituency_adjustment_seats, false);
  },
  watch: {
    'votes': {
      handler: function (val, oldVal) {
        this.$emit('update-votes', val);
      },
      deep: true
    },
    'parties': {
      handler: function (val, oldVal) {
        this.$emit('update-parties', val);
      },
      deep: true
    },
    'constituencies': {
      handler: function (val, oldVal) {
        this.$emit('update-constituencies', val);
      },
      deep: true
    },
    'constituency_seats': {
      handler: function (val, oldVal) {
        this.$emit('update-constituency-seats', val);
      },
      deep: true
    },
    'constituency_adjustment_seats': {
      handler: function (val, oldVal) {
        this.$emit('update-adjustment-seats', val);
      },
      deep: true
    },
  },
  methods: {
    deleteParty: function(index) {
      this.parties.splice(index, 1);
      for (let con in this.votes) {
        this.votes[con].splice(index, 1);
      }
    },
    deleteConstituency: function(index) {
      this.constituencies.splice(index, 1);
      this.votes.splice(index, 1);
      this.constituency_seats.splice(index, 1);
      this.constituency_adjustment_seats.splice(index, 1);
    },
    addParty: function() {
      this.parties.push('');
      for (let con in this.votes) {
        this.votes[con].push(0);
      }
    },
    addConstituency: function() {
      this.constituencies.push('');
      this.votes.push(Array(this.parties.length).fill(0));
      this.constituency_seats.push(1);
      this.constituency_adjustment_seats.push(1);
    },
    clearVotes: function() {
      let v = [];
      for (let con in this.votes) {
        v = Array(this.votes[con].length).fill(0);
        this.$set(this.votes, con, v);
      }
    },
    clearAll: function() {
      this.constituencies = [];
      this.constituency_seats = [];
      this.constituency_adjustment_seats = [];
      this.parties = [];
      this.votes = [];
    },
    setPreset: function(idx) {
      let el = this.presets[idx].election_rules;
      this.constituencies = el.constituency_names;
      this.parties = el.parties;
      this.constituency_seats = el.constituency_seats;
      this.constituency_adjustment_seats = el.constituency_adjustment_seats;
      this.votes = el.votes;
    }
  },
}
</script>
