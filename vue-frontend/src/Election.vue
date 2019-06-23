<template>
<div>
  <h2>Results</h2>
  <b-button size="lg" @click="get_xlsx">Download XLSX file</b-button>
  <b-container>
    <b-row>
      <ResultMatrix
        :constituencies="vote_table.constituencies"
        :parties="vote_table.parties"
        :values="results[activeTabIndex].seat_allocations"
        :stddev="false">
      </ResultMatrix>
    </b-row>
    <b-row>
      <ResultChart
        :parties="vote_table.parties"
        :seats="results[activeTabIndex].seat_allocations">
      </ResultChart>
    </b-row>
  </b-container>

</div>
</template>

<script>
import ResultMatrix from './components/ResultMatrix.vue'
import ResultChart from './components/ResultChart.vue'

export default {
  props: {
    "vote_table": { default: {} },
    "election_rules": { default: [{}] },
    "activeTabIndex": { default: 0 },
    "server": { default: {} },
  },
  components: {
    ResultMatrix,
    ResultChart
  },

  data: function() {
    return {
      results: [],
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
  methods: {
    recalculate: function() {
      if (this.election_rules.length > 0
          && this.election_rules[this.activeTabIndex].name) {
        this.server.waitingForData = true;
        this.$http.post('/api/election/',
        {
          vote_table: this.vote_table,
          rules: this.election_rules,
        }).then(response => {
          if (response.body.error) {
            this.server.errormsg = response.body.error;
            this.server.waitingForData = false;
          } else {
            this.server.errormsg = '';
            this.server.error = false;
            this.results = response.body;
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
        rules: [this.election_rules[this.activeTabIndex]],
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
