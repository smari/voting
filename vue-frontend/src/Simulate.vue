<template>
  <div>
    <h1>Simulate elections</h1>

    <h2>Reference votes</h2>
    <p>Reference votes are the votes that will be used as a reference for the statistical distribution in the simulation.</p>

    <VoteMatrix>
    </VoteMatrix>

    <h2>Quality measures</h2>
    <SimulationData>
    </SimulationData>

    <h2>Settings</h2>
    <ElectionSettings>
    </ElectionSettings>
  </div>
</template>

<script>
import VoteMatrix from './components/VoteMatrix.vue'
import ResultMatrix from './components/ResultMatrix.vue'
import ElectionSettings from './components/ElectionSettings.vue'
import SimulationData from './components/SimulationData.vue'

export default {
  components: {
    VoteMatrix,
    ResultMatrix,
    ElectionSettings,
    SimulationData,
  },
}
</script>
