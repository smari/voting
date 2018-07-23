<template>
  <b-container>
    <b-form>
      <b-row>
        <b-col>
          <b-form-group label="Primary apportionment divider" description="Which divider rule should be used to allocate constituency seats?">
            <b-form-select v-model="rules.election_rules.primary_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
          </b-form-group>
          <b-form-group label="Adjustment apportionment divider" description="Which divider rule should be used to allocate adjustment seats?">
            <b-form-select v-model="rules.election_rules.adjustment_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
          </b-form-group>
        </b-col>
        <b-col>
          <b-form-group label="Adjustment method" description="Which method should be used to allocate adjustment seats?">
            <b-form-select v-model="rules.election_rules.adjustment_method" :options="rules.capabilities.adjustment_methods" class="mb-3"/>
          </b-form-group>
          <b-form-group label="Adjustment threshold" description="What threshold are parties required to reach to qualify for adjustment seats?">
            <b-form-input type="number" v-model="rules.election_rules.adjustment_threshold"/>
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
      rules: { capabilities: {}, election_rules: {} },
    }
  },
  watch: {
    'rules': {
      handler: function (val, oldVal) {
        if (this.doneCreating) {
          this.$emit('update-rules', val.election_rules);
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
