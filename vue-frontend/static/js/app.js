Vue.component('voting-votematrix-constituency', {

})


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


var app = new Vue({
  el: "#app",

  data: {
    name: ''
  },

  computed: {
    showAlert() {
      return this.name.length > 4 ? true : false;
    }
  }
})
