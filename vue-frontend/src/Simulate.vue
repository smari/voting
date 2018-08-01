<template>
  <div>
    <h1>Simulate elections</h1>

    <h2>Settings</h2>
    <ElectionSettings server="server" @update-rules="updateElectionRules">
    </ElectionSettings>

    <SimulationSettings @update-rules="updateSimulationRules">
    </SimulationSettings>

    <h2>Reference votes</h2>
    <p>Reference votes are the votes that will be used as a reference for the statistical distribution in the simulation.</p>
    <VoteMatrix @update-votes="updateVotes" @update-adjustment-seats="updateAdjustmentSeats" @update-constituency-seats="updateConstituencySeats" @update-parties="updateParties" @update-constituencies="updateConstituencies" @server-error="serverError">
    </VoteMatrix>

    <div class="row">
      <div class="col-sm-4">
        <span v-if="simulation_done">
          <b-button :disabled="!simulation_done" @click="recalculate">Simulate</b-button>
        </span>
        <span v-if="!simulation_done">
          <b-button :disabled="simulation_done" @click="stop_simulation">Stop simulation</b-button>
        </span>
      </div>
      <div class="col-sm-2">
        <span v-if="!simulation_done">{{iteration_time}}s/iter</span>
      </div>
      <div class="col-sm-6" v-if="!simulation_done">
        <b-progress :value="current_iteration" :max="simulation_rules.simulation_count" show-progress animated></b-progress>
      </div>
    </div>

    <h2>Quality measures</h2>
    <SimulationData :measures="results.measures" :methods="results.methods" :data="results.data">
    </SimulationData>

  </div>
</template>

<script>
import VoteMatrix from './components/VoteMatrix.vue'
import ResultMatrix from './components/ResultMatrix.vue'
import ElectionSettings from './components/ElectionSettings.vue'
import SimulationSettings from './components/SimulationSettings.vue'
import SimulationData from './components/SimulationData.vue'

export default {
  components: {
    VoteMatrix,
    ResultMatrix,
    ElectionSettings,
    SimulationSettings,
    SimulationData,
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
      election_rules: {
        adjustment_divider: "",
        primary_divider: "",
        adjustment_threshold: 0.0,
        adjustment_method: "",
      },
      simulation_rules: {
        simulation_count: 0,
        gen_method: "",
      },
      simulation_done: true,
      current_iteration: 0,
      inflight: 0,
      ref_votes: [],
      results: { measures: [], methods: [], data: []},
    }
  },
  methods: {
    updateElectionRules: function(rules, recalc) {
      this.election_rules = rules;
    },
    updateSimulationRules: function(rules, recalc) {
      this.simulation_rules = rules;
    },
    updateVotes: function(votes, recalc) {
      this.ref_votes = votes;
    },
    updateConstituencySeats: function(seats, recalc) {
      this.constituency_seats = seats;
    },
    updateAdjustmentSeats: function(seats, recalc) {
      this.constituency_adjustment_seats = seats;
    },
    updateConstituencies: function(cons, recalc) {
      this.constituency_names = cons;
    },
    updateParties: function(parties, recalc) {
      this.parties = parties;
    },
    serverError: function(error) {
      this.server.errormsg = error;
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
            this.iteration_time = response.body.iteration_time
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
    recalculate: function() {
      this.current_iteration = 0;
      this.results = { measures: [], methods: [], data: []}
      this.sid = "";
      this.server.waitingForData = true;
      this.$http.post('/api/simulate/',
        {
          ref_votes: this.ref_votes,
          election_rules: this.election_rules,
          simulation_rules: this.simulation_rules,
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
            this.sid = response.body.sid;
            this.simulation_done = !response.body.started;
            this.server.waitingForData = false;
            this.checktimer = window.setInterval(this.checkstatus, 300);
          }
        }, response => {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    }
  },
}
</script>
