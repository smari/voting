<template>
  <div>
    <b-alert :show="server.waitingForData">Loading...</b-alert>
    <b-alert :show="server.error" dismissible @dismissed="server.error=false" variant="danger">Server error. Try again in a few seconds...</b-alert>
    <b-alert :show="server.errormsg != ''" dismissible @dismissed="server.errormsg=''" variant="danger">Server error. {{server.errormsg}}</b-alert>

    <h2>Votes</h2>
    <VoteMatrix
      @update-vote-table="updateVoteTable"
      @server-error="serverError">
    </VoteMatrix>

    <b-tabs>
      <b-tab title="Single Election" active>
        <Election
          :vote_table="vote_table"
          :server="server">
        </Election>
      </b-tab>
      <b-tab title="Simulation">
        <Simulate
          :vote_table="vote_table"
          :server="server">
        </Simulate>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
import Election from './Election.vue'
import Simulate from './Simulate.vue'
import VoteMatrix from './components/VoteMatrix.vue'

export default {
  components: {
    VoteMatrix,
    Election,
    Simulate,
  },

  data: function() {
    return {
      server: {
        waitingForData: false,
        error: false,
      },
      vote_table: {
        name: "",
        parties: [],
        constituencies: [],
        votes: [],
      },
      election_rules: [{
        name: "",
        adjustment_divider: "",
        primary_divider: "",
        adjustment_threshold: 0.0,
        adjustment_method: "",
      }],
      simulation_rules: {
        simulation_count: 0,
        gen_method: "",
        distribution_parameter: 0,
      },
      simulation_results: {
        done: true,
        current_iteration: 0,
        iteration_time: 0,
        inflight: 0,
      },
      //results: { measures: [], methods: [], data: [] },
    }
  },
  methods: {
    updateVoteTable: function(table) {
      this.vote_table = table;
    },
    serverError: function(error) {
      this.server.errormsg = error;
    },
  }
}
</script>
