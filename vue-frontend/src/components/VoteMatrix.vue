<template>
  <b-container fluid class="votematrix-container">
    <b-modal size="lg" id="modalupload" title="Upload CSV or XLSX file" @ok="uploadVotes">
      <p>The file provided must be a CSV or an Excel XLSX file formatted with parties on the first row and constitution names on the first column.</p>
      <b-img rounded fluid src="/static/img/parties_xlsx.png"/>
      <p>Optionally, if the second and third columns are named 'cons' or 'adj', they will be understood to be information about the number of constituency seats and adjustment seats, respectively, in each constituency. If you leave them out, you can specify the number of seats manually.</p>
      <b-form-file v-model="uploadfile" :state="Boolean(uploadfile)" placeholder="Choose a file..."></b-form-file>
    </b-modal>

    <b-modal size="lg" id="modalpaste" title="Paste CSV" @ok="pasteCSV">
      <p>Here you can paste in comma separated values to override the current vote table.</p>
      <b-form-textarea id="id_paste_csv"
                     v-model="paste.csv"
                     placeholder="Add your vote data"
                     rows="7">
      </b-form-textarea>
      <b-form-checkbox
                     v-model="paste.has_name"
                     value="true"
                     unchecked-value="false">
      First row begins with name by which to refer to this vote table.
      </b-form-checkbox>
      <b-form-checkbox
                     v-model="paste.has_parties"
                     value="true"
                     unchecked-value="false">
      First row is a header with party names.
      </b-form-checkbox>
      <b-form-checkbox
                     v-model="paste.has_constituencies"
                     value="true"
                     unchecked-value="false">
      First column contains constituency names.
      </b-form-checkbox>
      <b-form-checkbox v-model="paste.has_constituency_seats"
                       value="true"
                       unchecked-value="false">
      Second column contains constituency seats.
      </b-form-checkbox>
      <b-form-checkbox v-model="paste.has_constituency_adjustment_seats"
                       value="true"
                       unchecked-value="false">
      Third column contains adjustment seats.
      </b-form-checkbox>
    </b-modal>

    <b-modal size="lg" id="modalpreset" ref="modalpresetref" title="Load preset" cancel-only>

      <b-table hover :items="presets" :fields="presetfields">
        <template slot="actions" slot-scope="row">
          <b-button size="sm" @click.stop="loadPreset(row.item.id); $refs.modalpresetref.hide()" class="mr-1 mt-0 mb-0">
            Load
          </b-button>
        </template>
      </b-table>
    </b-modal>

    <b-button-toolbar key-nav aria-label="Vote tools">
      <b-button-group class="mx-1">
        <b-btn @click="addConstituency()">Add constituency</b-btn>
        <b-btn @click="addParty()">Add party</b-btn>
        <b-btn @click="clearVotes()">Clear votes</b-btn>
        <b-btn @click="clearAll()">Reset everything</b-btn>
      </b-button-group>
      <b-button-group class="mx-1">
        <b-button v-b-modal.modalupload>Upload votes</b-button>
        <b-button v-b-modal.modalpaste>Paste input</b-button>
        <b-button v-b-modal.modalpreset>Load preset</b-button>
        <!--b-dropdown id="ddown1" text="Presets" size="sm">
          <b-dropdown-item v-for="(preset, presetidx) in presets" :key="preset.name" @click="setPreset(presetidx)">{{preset.name}}</b-dropdown-item>
        </b-dropdown-->
      </b-button-group>
      <b-button-group class="mx-1">
        <b-button @click="saveVotes()">Save voteset</b-button>
      </b-button-group>
    </b-button-toolbar>
    <table class="votematrix">
      <tr class="parties">
        <th class="small-12 medium-1 tablename">
          <input type="text" v-model="matrix.name">
        </th>
        <th>
          <abbr title="Constituency seats"># Cons.</abbr>
        </th>
        <th>
          <abbr title="Adjustment seats"># Adj.</abbr>
        </th>
        <th v-for="(party, partyidx) in matrix.parties" class="small-12 medium-1 column partyname">
          <b-button size="sm" variant="link" @click="deleteParty(partyidx)">×</b-button>
          <input type="text" v-model="matrix.parties[partyidx]">
        </th>
      </tr>
      <tr v-for="(constituency, conidx) in matrix.constituencies">
        <th class="small-12 medium-1 column constname">
            <b-button size="sm" variant="link" @click="deleteConstituency(conidx)">×</b-button>
            <input type="text" v-model="constituency['name']"></input>
        </th>
        <td class="small-12 medium-2 column partyvotes">
          <input type="text" v-model.number="constituency['num_const_seats']"></input>
        </td>
        <td class="small-12 medium-2 column partyvotes">
          <input type="text" v-model.number="constituency['num_adj_seats']"></input>
        </td>
        <td v-for="(party, partyidx) in matrix.parties" class="small-12 medium-2 column partyvotes">
            <input type="text" v-model.number="matrix.votes[conidx][partyidx]">
            </input>
        </td>
      </tr>
    </table>
  </b-container>
</template>
<script>
export default {
  data: function () {
    return {
      matrix: {
        name: "My reference votes",
        parties: ["A", "B"],
        votes: [[1500, 2000],
                [2500, 1700]],
        constituencies: [
          {"name": "I",  "num_const_seats": 10, "num_adj_seats": 2},
          {"name": "II", "num_const_seats": 10, "num_adj_seats": 3}
        ],
      },
      presets: [],
      presetfields: [
        { key: 'name', sortable: true },
        { key: 'year', sortable: true },
        { key: 'country', sortable: true },
        { key: 'actions' },
      ],
      uploadfile: null,
      paste: { csv: '',
               has_name: false,
               has_parties: false,
               has_constituencies: false,
               has_constituency_seats: false,
               has_constituency_adjustment_seats: false
             }
    }
  },
  created: function() {
    this.$http.get('/api/presets').then(response => {
      this.presets = response.body;
    }, response => {
      this.$emit('server-error', response.body);
    });
    this.$emit('update-vote-table', this.matrix, false);
  },
  watch: {
    'matrix': {
      handler: function (val, oldVal) {
        this.$emit('update-vote-table', val);
      },
      deep: true
    },
  },
  methods: {
    deleteParty: function(index) {
      this.matrix.parties.splice(index, 1);
      for (let con in this.matrix.votes) {
        this.matrix.votes[con].splice(index, 1);
      }
    },
    deleteConstituency: function(index) {
      this.matrix.constituencies.splice(index, 1);
      this.matrix.votes.splice(index, 1);
    },
    addParty: function() {
      this.matrix.parties.push('');
      for (let con in this.matrix.votes) {
        this.matrix.votes[con].push(0);
      }
    },
    addConstituency: function() {
      this.matrix.constituencies.push(
        {"name": '', "num_const_seats": 1, "num_adj_seats": 1});
      this.matrix.votes.push(Array(this.matrix.parties.length).fill(0));
    },
    clearVotes: function() {
      let v = [];
      for (let con in this.matrix.votes) {
        v = Array(this.matrix.votes[con].length).fill(0);
        this.$set(this.matrix.votes, con, v);
      }
    },
    clearAll: function() {
      this.matrix.name = '';
      this.matrix.constituencies = [];
      this.matrix.parties = [];
      this.matrix.votes = [];
    },
    saveVotes: function() {
      this.$http.post('/api/votes/save/', {
        vote_table: this.matrix
      }).then(response => {
        let link = document.createElement('a')
        link.href = '/api/downloads/get?id=' + response.data.download_id
        link.click()
      }, response => {
        this.server.error = true;
      })
    },
    loadPreset: function(eid) {
      this.$http.post('/api/presets/load/', {'eid': eid}).then(response => {
        this.matrix = response.data;
      })
    },
    setPreset: function(idx) {
      let el = this.presets[idx].election_rules;
      this.matrix.constituencies = el.constituencies;
      this.matrix.parties = el.parties;
      this.matrix.votes = el.votes;
    },
    uploadVotes: function(evt) {
      if (!this.uploadfile) {
        evt.preventDefault();
      }
      var formData = new FormData();
      formData.append('file', this.uploadfile, this.uploadfile.name);
      this.$http.post('/api/votes/upload/', formData).then(response => {
        this.matrix = response.data;
      });
    },
    pasteCSV: function(evt) {
      if (!this.paste.csv) {
        evt.preventDefault();
        return;
      }
      this.$http.post('/api/votes/paste/', this.paste).then(response => {
        this.matrix = response.data;
      }, response => {
        console.log("Error:", response);
          // Error?
      });
    }
  },
}
</script>
