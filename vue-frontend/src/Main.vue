<template>
  <div>
    <b-alert :show="server.waitingForData">Loading...</b-alert>
    <b-alert :show="server.error" dismissible @dismissed="server.error=false" variant="danger">Server error. Try again in a few seconds...</b-alert>
    <b-alert :show="server.errormsg != ''" dismissible @dismissed="server.errormsg=''" variant="danger">Server error. {{server.errormsg}}</b-alert>

    <h2>Electoral system settings</h2>
    <b-card no-body>
      <b-tabs v-model="activeTabIndex" card>
        <b-tab v-for="(rules, rulesidx) in election_rules" :key="rulesidx">
          <div slot="title">
            <b-button
              size="sm"
              variant="link"
              @click="deleteElectionRules(rulesidx)"
            >
              x
            </b-button>
            {{rulesidx+1}}-{{rules.name}}
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
          Use the <b>+</b> button to create a new electoral system.
        </div>
      </b-tabs>
    </b-card>

    <h2>Votes</h2>
    <VoteMatrix
      @update-vote-table="updateVoteTable"
      @server-error="serverError">
    </VoteMatrix>

    <b-tabs style="margin-top:10px">
      <b-tab title="Single Election" active>
        <Election
          :server="server"
          :vote_table="vote_table"
          :election_rules="election_rules"
          :activeTabIndex="activeTabIndex"
          @update-rules="updateElectionRules">
        </Election>
      </b-tab>
      <b-tab title="Simulation">
        <Simulate
          :server="server"
          :vote_table="vote_table"
          :election_rules="election_rules">
        </Simulate>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
import Election from './Election.vue'
import Simulate from './Simulate.vue'
import VoteMatrix from './components/VoteMatrix.vue'
import ElectionSettings from './components/ElectionSettings.vue'

export default {
  components: {
    VoteMatrix,
    ElectionSettings,
    Election,
    Simulate,
  },

  data: function() {
    return {
      server: {
        waitingForData: false,
        errormsg: '',
        error: false,
      },
      vote_table: {
        name: "",
        parties: [],
        constituencies: [],
        votes: [],
      },
      election_rules: [{}],
      activeTabIndex: 0,
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
    serverError: function(error) {
      this.server.errormsg = error;
    },
    addElectionRules: function() {
      this.election_rules.push({})
    },
    deleteElectionRules: function(idx) {
      this.election_rules.splice(idx, 1);
    },
    updateElectionRules: function(rules, idx) {
      this.$set(this.election_rules, idx, rules);
      //this works too: this.election_rules.splice(idx, 1, rules);
    },
    updateVoteTable: function(table) {
      this.vote_table = table;
    },
  }
}
</script>
