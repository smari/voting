<template>
  <b-form>
    <b-row>
      <b-col>
        <b-form-group
          label="Name"
          description="Give this electoral system a name."
        >
          <b-form-input type="text" class="mb-3" v-model="rules.name"/>
        </b-form-group>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <fieldset>
          <legend>Allocation of constituency seats</legend>
          <b-form-group
            label="Rule"
            description="Which rule should be used to allocate constituency seats to lists within each constituency?"
          >
            <b-form-select class="mb-3"
              v-model="rules.primary_divider"
              :options="capabilities.divider_rules"/>
          </b-form-group>
          <b-form-group
            label="Threshold"
            description="What threshold are parties required to reach within a particular constituency to qualify for constituency seats?"
          >
            <b-input-group append="%">
              <b-form-input type="number" min="0" max="100"
                v-model.number="rules.constituency_threshold"/>
            </b-input-group>
          </b-form-group>
        </fieldset>
      </b-col>
      <b-col>
        <fieldset>
          <legend>Division of adjustment seats</legend>
          <b-form-group
            label="Rule"
            description="Which rule should be used to divide adjustment seats between parties nationally?"
          >
            <b-form-select class="mb-3"
              v-model="rules.adj_determine_divider"
              :options="capabilities.divider_rules"/>
          </b-form-group>
          <b-form-group
            label="Threshold"
            description="What threshold are parties required to reach nationally to qualify for adjustment seats?"
          >
            <b-input-group append="%">
              <b-form-input type="number" min="0" max="100"
                v-model.number="rules.adjustment_threshold"/>
            </b-input-group>
          </b-form-group>
        </fieldset>
      </b-col>
      <b-col>
        <fieldset>
          <legend>Allocation of adjustment seats</legend>
          <b-form-group
            label="Rule"
            description="Which rule should be used to allocate adjustment seats to individual lists?"
          >
            <b-form-select class="mb-3"
              v-model="rules.adj_alloc_divider"
              :options="capabilities.divider_rules"/>
          </b-form-group>
          <b-form-group
            label="Method"
            description="Which method should be used to allocate adjustment seats?"
          >
            <b-form-select class="mb-3"
              v-model="rules.adjustment_method"
              :options="capabilities.adjustment_methods"/>
          </b-form-group>
        </fieldset>
      </b-col>
    </b-row>
    <b-row>
      <b-col cols="5">
        <b-form-group
          label="Seat specification option"
          description="Which seat distribution should this electoral system use?"
        >
          <b-form-select class="mb-3"
            v-model="rules.seat_spec_option"
            :options="capabilities.seat_spec_options"/>
        </b-form-group>
      </b-col>
      <b-col>
        <table class="votematrix">
          <tr class="parties">
            <th class="small-12 medium-1 topleft"></th>
            <th>
              <abbr title="Constituency seats"># Cons.</abbr>
            </th>
            <th>
              <abbr title="Adjustment seats"># Adj.</abbr>
            </th>
          </tr>
          <tr v-for="(constituency, conidx) in rules.constituencies">
            <th class="small-12 medium-1 column constname">
              {{ constituency['name'] }}
            </th>
            <td class="small-12 medium-2 column partyvotes">
              <span v-if="rules.seat_spec_option != 'custom'">
                {{ constituency['num_const_seats'] }}
              </span>
              <span v-if="rules.seat_spec_option == 'custom'">
                <input type="text"
                  v-model.number="constituency['num_const_seats']">
              </span>
            </td>
            <td class="small-12 medium-2 column partyvotes">
              <span v-if="rules.seat_spec_option != 'custom'">
                {{ constituency['num_adj_seats'] }}
              </span>
              <span v-if="rules.seat_spec_option == 'custom'">
                <input type="text"
                  v-model.number="constituency['num_adj_seats']">
              </span>
            </td>
          </tr>
        </table>
      </b-col>
    </b-row>
  </b-form>
</template>

<script>
export default {
  props: [
    "rulesidx",
    "rules",
  ],
  data: function () {
    return {
      doneCreating: false,
      capabilities: {},
    }
  },
  watch: {
    'rules': {
      handler: function (val, oldVal) {
        if (this.doneCreating) {
          this.$emit('update-rules', val, this.rulesidx);
        }
      },
      deep: true
    }
  },
  created: function() {
    this.$http.get('/api/capabilities').then(response => {
      this.capabilities = response.body.capabilities;
      if (!("name" in this.rules)){
        this.$emit('update-rules', response.body.election_rules, this.rulesidx);
      }
      this.doneCreating = true;
    }, response => {
      this.serverError = true;
    });
  },
}
</script>
