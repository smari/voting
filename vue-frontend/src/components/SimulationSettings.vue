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
            label="Fair seat share scaling"
            description="Some of the quality measures require comparing the final seat allocation to an ideal 'fair seat share' matrix, where the entries are not rounded to an integer value. For that purpose, the votes are scaled such that the shares sum up to the proper total number of seats, and optionally, for each constituency or each party or both (using the specified number of seats for constituencies, and the required total number of seats for each party, as determined by the chosen rule for dividing adjustment seats). By default, both constraints are applied, in which case the shares will be scaled alternatively by rows and columns until they converge to a matrix fulfilling both constraints. This corresponds to the optimal biproportional seat allocation as found by the Alternating Scaling method. However, the user might be interested in other variations as well, for example scaling only by constituencies."
          >
            <b-form-checkbox
              v-model="rules.row_constraints"
              value="true"
              unchecked-value="false"
            >
              By constituencies
            </b-form-checkbox>
            <b-form-checkbox
              v-model="rules.col_constraints"
              value="true"
              unchecked-value="false"
            >
              By parties
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
