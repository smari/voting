<template>
<div>
  <h1>Election</h1>
  <b-alert :show="server.waitingForData">Loading...</b-alert>
  <b-alert :show="server.error" dismissible @dismissed="server.error=false" variant="danger">Server error. Try again in a few seconds...</b-alert>
  <b-alert :show="server.errormsg != ''" dismissible @dismissed="server.errormsg=''" variant="danger">Server error. {{server.errormsg}}</b-alert>

  <h2>Votes</h2>
  <VoteMatrix @update-votes="updateVotes" @update-adjustment-seats="updateAdjustmentSeats" @update-constituency-seats="updateConstituencySeats" @update-parties="updateParties" @update-constituencies="updateConstituencies" @recalculate="recalculate" @server-error="serverError">
  </VoteMatrix>

  <h2>Settings</h2>
  <b-container>
    <ElectionSettings server="server" @update-rules="updateRules">
    </ElectionSettings>
  </b-container>

  <h2>Results</h2>
  <b-button size="lg" @click="get_xlsx">Download XLSX file</b-button>
  <b-container>
    <b-row>
      <ResultMatrix
        :constituencies="results.constituencies"
        :parties="results.parties"
        :values="results.seat_allocations"
        :stddev="false">
      </ResultMatrix>
    </b-row>
    <b-row>
      <ResultChart :parties="results.parties" :seats="results.seat_allocations">
      </ResultChart>
    </b-row>
  </b-container>

</div>
</template>

<script>
import VoteMatrix from './components/VoteMatrix.vue'
import ResultMatrix from './components/ResultMatrix.vue'
import ResultChart from './components/ResultChart.vue'
import ElectionSettings from './components/ElectionSettings.vue'

export default {
  components: {
    VoteMatrix,
    ResultMatrix,
    ElectionSettings,
    ResultChart
  },

  data: function() {
    return {
      server: {
        waitingForData: false,
        error: false,
      },
      constituency_names: [],
      parties: [],
      constituency_seats: [],
      constituency_adjustment_seats: [],
      rules: {
        adjustment_divider: "",
        primary_divider: "",
        adjustment_threshold: 0.0,
        adjustment_method: "",
      },
      votes: [],
      results: { seat_allocations: [], parties: [], constituencies: []},
    }
  },
  methods: {
    updateRules: function(rules, recalc) {
      this.rules = rules;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateVotes: function(votes, recalc) {
      this.votes = votes;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateConstituencySeats: function(seats, recalc) {
      this.constituency_seats = seats;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateAdjustmentSeats: function(seats, recalc) {
      this.constituency_adjustment_seats = seats;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateConstituencies: function(cons, recalc) {
      this.constituency_names = cons;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateParties: function(parties, recalc) {
      this.parties = parties;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    serverError: function(error) {
      this.server.errormsg = error;
    },
    recalculate: function() {
      this.server.waitingForData = true;
      this.$http.post('/api/election/',
        {
          votes: this.votes,
          rules: this.rules,
          parties: this.parties,
          constituency_names: this.constituency_names,
          constituency_seats: this.constituency_seats,
          constituency_adjustment_seats: this.constituency_adjustment_seats
        }).then(response => {
          if (response.body.error) {
            this.server.errormsg = response.body.error;
            this.server.waitingForData = false;
          } else {
            this.server.errormsg = '';
            this.server.error = false;
            this.results["constituencies"] = response.body.rules.constituency_names;
            this.results["parties"] = response.body.rules.parties;
            this.results["seat_allocations"] = response.body.seat_allocations;
            this.server.waitingForData = false;
          }
        }, response => {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    },

    get_xlsx: function() {
      this.$http.post('/api/election/getxlsx/', {
        votes: this.votes,
        rules: this.rules,
        parties: this.parties,
        constituency_names: this.constituency_names,
        constituency_seats: this.constituency_seats,
        constituency_adjustment_seats: this.constituency_adjustment_seats
      }).then(response => {
        let link = document.createElement('a')
        link.href = '/api/downloads/get?id=' + response.data.download_id
        link.click()
      }, response => {
        this.server.error = true;
      })
    }
  },
}
</script>
