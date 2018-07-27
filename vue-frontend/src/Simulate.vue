<template>
  <div>
    <h1>Simulate elections</h1>

    <h2>Reference votes</h2>
    <p>Reference votes are the votes that will be used as a reference for the statistical distribution in the simulation.</p>
    <VoteMatrix @update-votes="updateVotes" @update-adjustment-seats="updateAdjustmentSeats" @update-constituency-seats="updateConstituencySeats" @update-parties="updateParties" @update-constituencies="updateConstituencies" @recalculate="recalculate" @server-error="serverError">
    </VoteMatrix>

    <h2>Settings</h2>
    <ElectionSettings server="server" @update-rules="updateElectionRules">
    </ElectionSettings>

    <SimulationSettings @update-rules="updateSimulationRules">
    </SimulationSettings>

    <h2>Quality measures</h2>
    <SimulationData :measures="results.measures" :methods="results.methods" :numbers="results.numbers">
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
      ref_votes: [],
      results: { measures: [], methods: [], numbers: []},
    }
  },
  methods: {
    updateElectionRules: function(rules, recalc) {
      this.election_rules = rules;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateSimulationRules: function(rules, recalc) {
      this.simulation_rules = rules;
      if (recalc === true || recalc === undefined) {
        this.recalculate();
      }
    },
    updateVotes: function(votes, recalc) {
      this.ref_votes = votes;
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
            this.results["measures"] = response.body.measures;
            this.results["methods"] = response.body.methods;
            this.results["numbers"] = response.body.numbers;
            this.server.waitingForData = false;
          }
        }, response => {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    }
  },
}
</script>
