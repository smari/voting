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
    }
  },
  created: function() {
    this.$http.get('/api/capabilities').then(response => {
      this.rules = response.body;
      this.doneCreating = true;
    }, response => {
      this.serverError = true;
    });
  },
}
</script>
