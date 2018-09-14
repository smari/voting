<template>
  <b-container>
    <b-form>
      <b-row>
        <b-col>
          <b-form-group label="Number of simulations" description="How many simulations should be run? (Minimum 2)">
            <b-form-input type="number" v-model.number="rules.simulation_rules.simulation_count" min="2"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group label="Generating method" description="Which method should be used to generate votes?">
            <b-form-select v-model="rules.simulation_rules.gen_method" :options="rules.capabilities.generating_methods" class="mb-3"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group
            label="Distribution parameter"
            description="What parameter should be used for the standard deviation of the distribution? (must be greater than 0 and less than 0.5)">
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
      this.distribution_parameter = 0.1;
      this.doneCreating = true;
    }, response => {
      this.serverError = true;
    });
  },
}
</script>
