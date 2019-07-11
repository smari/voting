<template>
  <b-container>
    <b-form>
      <b-row>
        <b-col>
          <b-form-group
            label="Number of simulations"
            description="How many simulations should be run? Select 0 to use only reference data instead of any simulated data."
          >
            <b-form-input
              type="number"
              v-model.number="rules.simulation_count"
              min="0"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group
            label="Generating method"
            description="Which method should be used to generate random votes (based on the supplied vote table)?"
          >
            <b-form-select
              v-model="rules.gen_method"
              :options="capabilities.generating_methods"
              class="mb-3"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group
            label="Stability parameter"
            description="To influence the standard deviation of the distribution, please provide a number greater than 1 (does not need to be an integer, and values close to 1 are allowed, such as 1.0001). This number represents stability, in some sense. Higher values result in lower standard deviation, and vice versa."
          >
            <b-input-group>
              <b-form-input
                type="text"
                v-model.number="rules.distribution_parameter"/>
            </b-input-group>
          </b-form-group>
        </b-col>
      </b-row>
      <b-row v-if="num_parties>1 && num_constituencies>1">
        <b-col>
          <b-form-group
            label="Fair share constraints"
            description="Some of the measures we apply compare the resulting seat allocation to an ideal 'fair share' matrix, where the number of seats for each list is not restricted to an integer value. These fair shares can be calculated simply by scaling the vote matrix as a whole, so that each list gets exactly the same portion of the total seats as it has of the total votes. In general, this would mean that the rows and columns don't necessarily sum to an integer, let alone the same number that has been determined as a required total number of seats for the given row (specified number of seats for each constituency) or column (determined number of seats for each party, as calculated with the chosen rule for dividing adjustment seats). Alternatively, the fair shares can be calculated in such a way as to make sure the rows and/or columns sum to the correct total. These alternatives are only relevant in case there are at least 2 of both constituencies and parties."
          >
            <b-form-checkbox
              v-model="rules.row_constraints"
              value="true"
              unchecked-value="false"
            >
              On constituencies
            </b-form-checkbox>
            <b-form-checkbox
              v-model="rules.col_constraints"
              value="true"
              unchecked-value="false"
            >
              On parties
            </b-form-checkbox>
          </b-form-group>
        </b-col>
      </b-row>
    </b-form>
  </b-container>
</template>

<script>
export default {
  props: [
    "num_parties",
    "num_constituencies",
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
          this.$emit('update-rules', val);
        }
      },
      deep: true
    },
  },
  created: function() {
    this.$http.get('/api/capabilities').then(response => {
      this.capabilities = response.body.capabilities;
      this.$emit('update-rules', response.body.simulation_rules);
      this.doneCreating = true;
    }, response => {
      this.serverError = true;
    });
  },
}
</script>
