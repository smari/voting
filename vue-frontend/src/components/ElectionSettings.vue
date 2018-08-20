<template>
  <b-form>
    <b-row v-if="rulesidx !== undefined">
      <b-col>
        <b-form-group label="Name" description="Give this rule set a name.">
          <b-form-input v-model="rules.election_rules.name" type="text"   class="mb-3"/>
        </b-form-group>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <b-form-group label="Primary apportionment divider" description="Which divider rule should be used to allocate constituency seats?">
          <b-form-select v-model="rules.election_rules.primary_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
        </b-form-group>
        <b-form-group label="Adjustment determination divider" description="Which divider rule should be used to determine how many adjustment seats a party gets?">
          <b-form-select v-model="rules.election_rules.adj_determine_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
        </b-form-group>
        <b-form-group label="Adjustment apportionment divider" description="Which divider rule should be used to decide adjustment seats?">
          <b-form-select v-model="rules.election_rules.adj_alloc_divider" :options="rules.capabilities.divider_rules" class="mb-3"/>
        </b-form-group>
      </b-col>
      <b-col>
        <b-form-group label="Adjustment method" description="Which method should be used to allocate adjustment seats?">
          <b-form-select v-model="rules.election_rules.adjustment_method" :options="rules.capabilities.adjustment_methods" class="mb-3"/>
        </b-form-group>
        <b-form-group label="Adjustment threshold" description="What threshold are parties required to reach to qualify for adjustment seats?">
          <b-form-input type="number" v-model.number="rules.election_rules.adjustment_threshold"/>
        </b-form-group>
      </b-col>
    </b-row>
  </b-form>
</template>

<script>
export default {
  props: [ "rulesidx" ],
  data: function () {
    return {
      doneCreating: false,
      rules: { capabilities: {}, election_rules: { } },
    }
  },
  watch: {
    'rules': {
      handler: function (val, oldVal) {
        if (this.doneCreating) {
          this.$emit('update-rules', val.election_rules, this.rulesidx);
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
