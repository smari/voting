Vue.component('voting-votematrix', {
  data: function () {
    return {
      constituencies: ["Norðvestur", "Norðaustur", "Suður", "Suðvestur", "Reykjavík Suður", "Reykjavík Norður"],
      parties: ["B", "C", "D", "F", "M", "S", "P", "V"],
      votes: [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],],
    }
  },
  methods:{
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
<table class="votematrix">
  <tr class="parties">
    <th class="small-12 medium-1 topleft">
      <b-button size="sm" variant="outline-secondary" @click="addConstituency()">Add constituency</b-button>
      <b-button size="sm" variant="outline-secondary" @click="addParty()">Add party</b-button>
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
    <td v-for="(party, partyidx) in parties" class="small-12 medium-2 column partyvotes">
        <input type="text" v-model.number="votes[conidx][partyidx]">
        </input>
    </td>
  </tr>
</table>
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


const Election = { template: `
<div>
  <h1>Election</h1>

  <h2>Votes</h2>
  <voting-votematrix>
  </voting-votematrix>

  <h2>Results</h2>
  <voting-resultmatrix>
  </voting-resultmatrix>
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
