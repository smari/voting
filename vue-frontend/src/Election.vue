<template>
<div>
  <h1>Election</h1>

  <h2>Settings</h2>
  <b-card no-body>
    <b-tabs card>
      <b-tab v-for="(rules, rulesidx) in election_rules" :key="rulesidx">
        <div slot="title">
          <b-button size="sm" variant="link" @click="deleteElectionRules(rulesidx)">x</b-button>
          {{rulesidx}}-{{rules.name}}
        </div>
        <ElectionSettings
          :rulesidx="rulesidx"
          :rules="rules"
          @update-rules="updateElectionRules">
        </ElectionSettings>
      </b-tab>
      <template slot="tabs">
        <b-button size="sm" @click="addElectionRules"><b>+</b></b-button>
      </template>
      <div slot="empty">
        There are no electoral systems specified.
        Use the + button to create a new electoral system.
      </div>
    </b-tabs>
  </b-card>

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
  props: {
    "vote_table": { default: {} },
    "server": { default: {} },
  },
  components: {
    VoteMatrix,
    ResultMatrix,
    ElectionSettings,
    ResultChart
  },

  data: function() {
    return {
      doneCreating: false,
      election_rules: [{}],
      results: { seat_allocations: [], parties: [], constituencies: []},
    }
  },
  watch: {
    'vote_table': {
      handler: function (val, oldVal) {
        this.recalculate();
      },
      deep: true
    },
    'election_rules': {
      handler: function (val, oldVal) {
        this.recalculate();
      },
      deep: true
    },
  },
  created: function() {
    this.doneCreating = true;
  },
  methods: {
    addElectionRules: function() {
      this.election_rules.push({})
    },
    deleteElectionRules: function(idx) {
      this.election_rules.splice(idx, 1);
    },
    updateElectionRules: function(rules, idx) {
      this.$set(this.election_rules, idx, rules);
    },
    recalculate: function() {
      if (this.doneCreating
          && this.election_rules.length > 0
          && this.election_rules[0].name) {
        this.server.waitingForData = true;
        this.$http.post('/api/election/',
        {
          vote_table: this.vote_table,
          rules: this.election_rules[0],
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
      }
    },

    get_xlsx: function() {
      this.$http.post('/api/election/getxlsx/', {
        vote_table: this.vote_table,
        rules: this.election_rules[0],
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
