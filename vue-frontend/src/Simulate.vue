<template>
  <div>
    <h2>Simulation settings</h2>
    <SimulationSettings
      :num_parties="vote_table.parties.length"
      :num_constituencies="vote_table.constituencies.length"
      @update-rules="updateSimulationRules">
    </SimulationSettings>

    <div style="text-align: center; margin-bottom: 0.7em;">
        <span v-if="simulation_done">
          <b-button
            size="lg"
            variant="success"
            :disabled="!simulation_done"
            @click="recalculate"
          >
            Start simulation
          </b-button>
        </span>
        <span v-if="!simulation_done">
          <b-button
            size="lg"
            variant="danger"
            :disabled="simulation_done"
            @click="stop_simulation"
          >
            Stop simulation
          </b-button>
        </span>
    </div>
    <div class="row" style="margin-bottom: 0.7em;">
      <b-col cols="2">
        <span v-if="!simulation_done">{{iteration_time}}s/iter</span>
      </b-col>
      <b-col cols="8">
        <b-progress
          :value="current_iteration"
          :max="simulation_rules.simulation_count"
          :animated="!simulation_done"
          :variant="simulation_done ? 'success':'primary'"
          show-value>
        </b-progress>
      </b-col>
      <b-col cols="2">

      </b-col>
    </div>

    <h2>Results</h2>
    <b-alert :show="results.data.length == 0">
      Run simulation to get results.
    </b-alert>
    <div v-if="results.data.length > 0">
      <b-button size="lg" :href="get_xlsx_url()">Download XLSX file</b-button>

      <h3>Constituency seats</h3>
      <ResultMatrix
        v-for="(ruleset, idx) in results.data"
        :key="'const-seats-' + idx"
        :constituencies="election_rules[idx].constituencies"
        :parties="vote_table.parties"
        :values="ruleset.list_measures.const_seats.avg"
        :stddev="ruleset.list_measures.const_seats.std"
        :title="ruleset.name"
        round="2">
      </ResultMatrix>

      <h3>Adjustment seats</h3>
      <ResultMatrix
        v-for="(ruleset, idx) in results.data"
        :key="'adj-seats-' + idx"
        :constituencies="election_rules[idx].constituencies"
        :parties="vote_table.parties"
        :values="ruleset.list_measures.adj_seats.avg"
        :stddev="ruleset.list_measures.adj_seats.std"
        :title="ruleset.name"
        round="2">
      </ResultMatrix>

      <h3>Total seats</h3>
      <ResultMatrix
        v-for="(ruleset, idx) in results.data"
        :key="'total-seats-' + idx"
        :constituencies="election_rules[idx].constituencies"
        :parties="vote_table.parties"
        :values="ruleset.list_measures.total_seats.avg"
        :stddev="ruleset.list_measures.total_seats.std"
        :title="ruleset.name"
        round="2">
      </ResultMatrix>

      <h3>Quality measures</h3>
      <SimulationData
        :measures="results.measures"
        :deviation_measures="results.deviation_measures"
        :standardized_measures="results.standardized_measures"
        :methods="results.methods"
        :data="results.data"
        :testnames="results.testnames">
      </SimulationData>
    </div>
  </div>
</template>

<script>
import ResultMatrix from './components/ResultMatrix.vue'
import SimulationSettings from './components/SimulationSettings.vue'
import SimulationData from './components/SimulationData.vue'

export default {
  props: {
    "vote_table": { default: {} },
    "election_rules": { default: [{}] },
    "server": { default: {} },
  },
  components: {
    ResultMatrix,
    SimulationSettings,
    SimulationData,
  },

  data: function() {
    return {
      simulation_rules: {
        simulation_count: 0,
        gen_method: "",
        distribution_parameter: 0,
      },
      simulation_done: true,
      current_iteration: 0,
      iteration_time: 0,
      inflight: 0,
      results: { measures: [], methods: [], data: [] },
    }
  },
  methods: {
    updateSimulationRules: function(rules) {
      this.simulation_rules = rules;
    },
    stop_simulation: function() {
      this.$http.post('/api/simulate/stop/',
        {
          sid: this.sid
        }).then(response => {
          if (response.body.error) {
            this.server.errormsg = response.body.error;
            this.server.waitingForData = false;
          } else {
            this.server.errormsg = '';
            this.server.error = false;
            this.simulation_done = response.body.done;
            this.current_iteration = response.body.iteration;
            this.iteration_time = response.body.iteration_time;
            this.results = response.body.results;
            this.server.waitingForData = false;
            if (this.simulation_done) {
              window.clearInterval(this.checktimer);
            }
          }
        }, response => {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    },
    checkstatus: function() {
      this.inflight++;
      this.$http.post('/api/simulate/check/',
        {
          sid: this.sid
        }).then(response => {
          this.inflight--;
          if (response.body.error) {
            this.server.errormsg = response.body.error;
            this.server.waitingForData = false;
          } else {
            this.server.errormsg = '';
            this.server.error = false;
            this.simulation_done = response.body.done;
            this.current_iteration = response.body.iteration;
            this.iteration_time = response.body.iteration_time;
            this.results = response.body.results;
            console.log(this.results);
            this.server.waitingForData = false;
            if (this.simulation_done) {
              window.clearInterval(this.checktimer);
            }
          }
        }, response => {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    },
    recalculate: function() {
      this.current_iteration = 0;
      this.results = { measures: [], methods: [], data: [] }
      this.sid = "";
      this.server.waitingForData = true;
      this.$http.post('/api/simulate/',
        {
          vote_table: this.vote_table,
          election_rules: this.election_rules,
          simulation_rules: this.simulation_rules,
        }).then(response => {
          if (response.body.error) {
            this.server.errormsg = response.body.error;
            this.server.waitingForData = false;
          } else {
            this.server.errormsg = '';
            this.server.error = false;
            this.sid = response.body.sid;
            this.simulation_done = !response.body.started;
            this.server.waitingForData = false;
            this.checktimer = window.setInterval(this.checkstatus, 300);
          }
        }, response => {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    },

    get_xlsx_url: function() {
      return "/api/simulate/getxlsx/?sid=" + this.sid;
    }
  },
}
</script>
