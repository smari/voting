<template>
  <b-form>
    <b-row v-if="rulesidx !== undefined">
      <b-col>
        <b-form-group
          label="Name"
          description="Give this electoral system a name.">
          <b-form-input type="text" class="mb-3"
            v-model="rules.name"/>
        </b-form-group>
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <b-form-group
          label="Rule for allocating constituency seats"
          description="Which rule should be used to allocate constituency seats to lists within each constituency?">
          <b-form-select class="mb-3"
            v-model="rules.primary_divider"
            :options="capabilities.divider_rules"/>
        </b-form-group>
        <b-form-group
          label="Rule for dividing adjustment seats"
          description="Which rule should be used to divide adjustment seats between parties?">
          <b-form-select class="mb-3"
            v-model="rules.adj_determine_divider"
            :options="capabilities.divider_rules"/>
        </b-form-group>
        <b-form-group
          label="Rule for allocating adjustment seats"
          description="Which rule should be used to allocate adjustment seats to individual lists?">
          <b-form-select class="mb-3"
            v-model="rules.adj_alloc_divider"
            :options="capabilities.divider_rules"/>
        </b-form-group>
      </b-col>
      <b-col>
        <b-form-group
          label="Adjustment method"
          description="Which method should be used to allocate adjustment seats?">
          <b-form-select class="mb-3"
            v-model="rules.adjustment_method"
            :options="capabilities.adjustment_methods"/>
        </b-form-group>
        <b-form-group
          label="Adjustment threshold"
          description="What threshold are parties required to reach to qualify for adjustment seats?">
          <b-input-group append="%">
            <b-form-input type="number" min="0" max="100"
              v-model.number="rules.adjustment_threshold"/>
          </b-input-group>
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
      rules: { },
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
      this.rules = response.body.election_rules;
      this.capabilities = response.body.capabilities;
      this.doneCreating = true;
    }, response => {
      this.serverError = true;
    });
  },
}
</script>
