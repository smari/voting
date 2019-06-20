<template>
<div>
  <h1>Election</h1>
  <b-alert :show="server.waitingForData">Loading...</b-alert>
  <b-alert :show="server.error" dismissible @dismissed="server.error=false" variant="danger">Server error. Try again in a few seconds...</b-alert>
  <b-alert :show="server.errormsg != ''" dismissible @dismissed="server.errormsg=''" variant="danger">Server error. {{server.errormsg}}</b-alert>

  <h2>Votes</h2>
  <VoteMatrix
    @update-table-name="updateTableName"
    @update-votes="updateVotes"
    @update-parties="updateParties"
    @update-constituencies="updateConstituencies"
    @recalculate="recalculate"
    @server-error="serverError">
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
      parties: [],
      constituencies: [],
      rules: {
        adjustment_divider: "",
        primary_divider: "",
        adjustment_threshold: 0.0,
        adjustment_method: "",
      },
      table_name: "",
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
    updateTableName: function(name) {
      this.table_name = name;
    },
    updateVotes: function(votes, recalc) {
      this.votes = votes;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateConstituencies: function(cons, recalc) {
      this.constituencies = cons;
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
          vote_table: {
            name: this.table_name,
            parties: this.parties,
            constituencies: this.constituencies,
            votes: this.votes,
          },
          rules: this.rules,
        }).then(response => {
          if (response.body.error) {
            this.server.errormsg = response.body.error;
            this.server.waitingForData = false;
          } else {
            this.server.errormsg = '';
            this.server.error = false;
            this.results["constituencies"] = response.body.rules.constituencies;
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
        vote_table: {
          name: this.table_name,
          parties: this.parties,
          constituencies: this.constituencies,
          votes: this.votes,
        },
        rules: this.rules,
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
