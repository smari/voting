<template>
<div>
  <h2>Results</h2>
  <b-button size="lg" @click="get_xlsx">Download XLSX file</b-button>
  <b-container v-if="results[activeTabIndex] !== undefined">
    <b-row>
      <ResultMatrix
        :parties="vote_table.parties"
        :constituencies="results[activeTabIndex].rules.constituencies"
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
    "server": { default: {} },
    "vote_table": { default: {} },
    "election_rules": { default: [{}] },
    "activeTabIndex": { default: 0 },
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
          && this.election_rules.length > this.activeTabIndex
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

            for (var i=0; i<response.body.length; i++){
              let old_const = this.election_rules[i].constituencies;
              let new_const = response.body[i].rules.constituencies;
              let modified = false;
              if (new_const.length == old_const.length) {
                for (var j=0; j<new_const.length; j++) {
                  let old_c = old_const[j];
                  let new_c = new_const[j];
                  if (old_c.name != new_c.name
                      || old_c.num_const_seats != new_c.num_const_seats
                      || old_c.num_adj_seats != new_c.num_adj_seats) {
                    modified = true;
                  }
                }
              }
              else if (new_const.length>0) {
                modified = true;
              }
              if (modified){
                this.$emit('update-rules', response.body[i].rules, i);
              }
            }
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
        rules: this.election_rules,
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
