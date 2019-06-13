<template>
  <b-container>
    <b-form>
      <b-row>
        <b-col>
          <b-form-group
            label="Number of simulations"
            description="How many simulations should be run? Select 0 to use only reference data instead of any simulated data.">
            <b-form-input type="number" v-model.number="rules.simulation_rules.simulation_count" min="0"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group label="Generating method" description="Which method should be used to generate random votes?">
            <b-form-select v-model="rules.simulation_rules.gen_method" :options="rules.capabilities.generating_methods" class="mb-3"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group
            label="Stability parameter"
            description="To influence the standard deviation of the distribution, please provide a number greater than 1 (does not need to be an integer, and values close to 1 are allowed, such as 1.0001). This number represents stability, in some sense. Higher values result in lower standard deviation, and vice versa.">
            <b-input-group>
              <b-form-input type="text"
                v-model.number="distribution_parameter"/>
            </b-input-group>
          </b-form-group>
        </b-col>
      </b-row>
    </b-form>
  </b-container>
</template>

<script>
export default {
  data: function () {
    return {
      doneCreating: false,
      rules: { capabilities: {}, simulation_rules: {} },
      distribution_parameter: 0,
    }
  },
  watch: {
    'rules': {
      handler: function (val, oldVal) {
        if (this.doneCreating) {
          this.$emit('update-rules', val.simulation_rules);
        }
      },
      deep: true
    },
    'distribution_parameter': {
      handler: function (val, oldVal) {
        if (this.doneCreating) {
          this.$emit('update-parameter', val);
        }
      },
      deep: true
    }
  },
  created: function() {
    this.$http.get('/api/capabilities').then(response => {
      this.rules = response.body;
      this.distribution_parameter = 100;
      this.doneCreating = true;
    }, response => {
      this.serverError = true;
    });
  },
}
</script>
