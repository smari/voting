Vue.component('voting-votematrix', {
  data: function () {
    return {
      constituencies: ["Norðvestur", "Norðaustur", "Suður", "Suðvestur", "Reykjavík Suður", "Reykjavík Norður"],
      constituency_seats: [8, 8, 9, 11, 9, 9],
      constituency_adjustment_seats: [1, 1, 1, 2, 2, 2],
      parties: ["B", "C", "D", "F", "M", "S", "P", "V"],
      votes: [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],],
    }
  },
  watch: {
    // TODO: Also trigger recalculation on changes to other data.
    'votes': {
      handler: function (val, oldVal) {
        console.log('Sending voting-recalculate');
        this.$emit('voting-recalculate', val);
      },
      deep: true
    }
  },
  methods: {
    deleteParty: function(index) {
      this.parties.splice(index, 1);
      for (con in this.votes) {
        this.votes[con].splice(index, 1);
      }
    },
    deleteConstituency: function(index) {
      this.constituencies.splice(index, 1);
      this.votes.splice(index, 1);
    },
    addParty: function() {
      this.parties.push('');
      for (con in this.votes) {
        this.votes[con].push(0);
      }
    },
    addConstituency: function() {
      this.constituencies.push('');
      this.votes.push(Array(this.parties.length).fill(0));
    }
  },
  template:
    `
<b-container fluid class="votematrix-container">
<table class="votematrix">
  <tr class="parties">
    <th class="small-12 medium-1 topleft">
      <b-button size="sm" variant="outline-secondary" @click="addConstituency()">Add constituency</b-button>
      <b-button size="sm" variant="outline-secondary" @click="addParty()">Add party</b-button>
    </th>
    <th>
      <abbr title="Constituency seats"># Cons.</abbr>
    </th>
    <th>
      <abbr title="Adjustment seats"># Adj.</abbr>
    </th>
    <th v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyname">
      <b-button size="sm" variant="link" @click="deleteParty(partyidx)">×</b-button>
      <input type="text" v-model="parties[partyidx]">
    </th>
  </tr>
  <tr v-for="(constituency, conidx) in constituencies">
    <th class="small-12 medium-1 column constname">
        <b-button size="sm" variant="link" @click="deleteConstituency(conidx)">×</b-button>
        <input type="text" v-model="constituencies[conidx]"></input>
    </th>
    <td class="small-12 medium-2 column partyvotes">
      <input type="text" v-model.number="constituency_seats[conidx]"></input>
    </td>
    <td class="small-12 medium-2 column partyvotes">
      <input type="text" v-model.number="constituency_adjustment_seats[conidx]"></input>
    </td>
    <td v-for="(party, partyidx) in parties" class="small-12 medium-2 column partyvotes">
        <input type="text" v-model.number="votes[conidx][partyidx]">
        </input>
    </td>
  </tr>
</table>
</b-container>
`
})


Vue.component('voting-electionsettings', {
  data: function () {
    return {
      rules: { capabilities: {}, election_rules: {}, presets: {}},
    }
  },
  created: function() {
    console.log("Getting capabilities.");
    this.$http.get('/api/capabilities').then(response => {
      this.rules = response.body;
    }, response => {
      this.serverError = true;
    });
  },
  methods: {
  },
  template:
    `
<b-container>
  <b-form>
    <b-row>
      <b-col>
        <b-form-group label="Primary apportionment divider" description="Which divider rule should be used to allocate constituency seats?">
          <b-form-select v-model="rules.election_rules.primary_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
        </b-form-group>
        <b-form-group label="Adjustment apportionment divider" description="Which divider rule should be used to allocate adjustment seats?">
          <b-form-select v-model="rules.election_rules.adjustment_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
        </b-form-group>
      </b-col>
      <b-col>
        <b-form-group label="Adjustment method" description="Which method should be used to allocate adjustment seats?">
          <b-form-select v-model="rules.election_rules.adjustment_method" :options="rules.capabilities.adjustment_methods" class="mb-3"/>
        </b-form-group>
        <b-form-group label="Adjustment threshold" description="What threshold are parties required to reach to qualify for adjustment seats?">
          <b-form-input type="number" v-model="rules.election_rules.adjustment_threshold"/>
        </b-form-group>
      </b-col>
    </b-row>
  </b-form>
</b-container>
`
})

Vue.component('voting-resultmatrix', {
  data: function () {
    return {
      constituencies: ["Norðvestur", "Norðaustur", "Suður", "Suðvestur", "Reykjavík Suður", "Reykjavík Norður"],
      parties: ["B", "C", "D", "F", "M", "S", "P", "V"],
      seats: [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],],
    }
  },
  methods:{
    
  },
  template:
    `
<table class="resultmatrix"> 
  <tr class="parties">
    <th class="small-12 medium-1 topleft">
      
    </th>
    <th v-for="(party, partyidx) in parties" class="small-12 medium-1 column partyname">
      {{ parties[partyidx] }}
    </th>
  </tr>
  <tr v-for="(constituency, conidx) in constituencies">
    <th class="small-12 medium-1 column constname">8
        {{ constituencies[conidx] }}
    </th>
    <td v-for="(party, partyidx) in parties" class="small-12 medium-2 column partyseats">
        {{ seats[conidx][partyidx] }}
    </td>
  </tr>
</table>
`
})

Vue.component('voting-simulationdata', {
  data: function () {
    return {
      measures: ["Entropy", "Entropy Ratio", "Dev Opt", "Dev Law", "Dev Ind Const", "Dev One Country", "Dev Tot Eq", "LH", "StL", "dHmin", "dHsum"],
      methods: ["Alternating Scaling", "Icelandic Law", "Relative superiority"],
      numbers: [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    }
  },
  methods:{
    
  },
  template:
    `
<table class="simulationdata">
  <tr class="methods">
    <th class="small-12 medium-1 topleft">
      
    </th>
    <th v-for="(method, methodidx) in methods" class="small-12 medium-1 column methodname">
      {{ methods[methodidx] }}
    </th>
  </tr>
  <tr v-for="(measure, measureidx) in measures">
    <th class="small-12 medium-1 column measurename">
        {{ measures[measureidx] }}
    </th>
    <td v-for="(method, methodidx) in methods" class="small-12 medium-2 column methodnumbers">
        {{ numbers[measureidx][methodidx] }}
    </td>
  </tr>
</table>
`
})



const Election = {
  data: function() {
    return {
      server: {
        waitingForData: false,
        error: false,
      },
      results: {},
    }
  },
  methods: {
    recalculate: function(votes) {
      this.server.waitingForData = true;
      this.$http.post('/api/election/', { votes })
        .then(function(data, status, request) {
          console.log("Got results: ", data, status);
          this.results = data;
          this.server.waitingForData = false;
        }).catch(function(data, status, request) {
          this.server.error = true;
          this.server.waitingForData = false;
        });
    }
  },
  template: `
<div>
  <h1>Election</h1>
  <b-alert :show="server.waitingForData">Loading...</b-alert>
  <b-alert :show="server.error" dismissible @dismissed="server.error=false" variant="danger">Server error. Try again in a few seconds...</b-alert>

  <h2>Votes</h2>
  <voting-votematrix @voting-recalculate="recalculate">
  </voting-votematrix>


  <h2>Results</h2>
  <voting-resultmatrix>
  </voting-resultmatrix>

  <h2>Settings</h2>
  <voting-electionsettings server="server">
  </voting-electionsettings>
</div>
`
}

const Simulate = { template: `
<div>
  <h1>Simulate elections</h1>

  <h2>Reference votes</h2>
  <p>Reference votes are the votes that will be used as a reference for the statistical distribution in the simulation.</p>

  <voting-votematrix>
  </voting-votematrix>

  <h2>Quality measures</h2>
  <voting-simulationdata>
  </voting-simulationdata>
</div>
`
}

const routes = [
  { path: '/election', component: Election },
  { path: '/simulate', component: Simulate }
]

const router = new VueRouter({ routes })

var app = new Vue({ router, el: "#app" })
