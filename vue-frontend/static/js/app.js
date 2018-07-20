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
`
})


const Election = { template: `
<div>
  <h1>Election</h1>

  <h2>Votes</h2>
  <voting-votematrix>
  </voting-votematrix>
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
</div>
`
}

const routes = [
  { path: '/election', component: Election },
  { path: '/simulate', component: Simulate }
]

const router = new VueRouter({ routes })

var app = new Vue({ router, el: "#app" })
