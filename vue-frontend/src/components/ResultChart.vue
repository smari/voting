<script>
import VueCharts from 'vue-chartjs'
import { Pie } from 'vue-chartjs'

export default {
  extends: Pie,
  mounted() {
    this.renderResultChart();
  },
  data: function () { return {
    options: {
      animation: {
        duration: 0
      }
    },
  }},
  props: ["parties", "seats"],
  methods: {
    renderResultChart: function() {
      this.renderChart(this.chartData, this.options);
    }
  },
  watch: {
    parties: function() {
      if (this._chart) this._chart.destroy();
      this.renderResultChart();
    },
    seats: function() {
      if (this._chart) this._chart.destroy();
      this.renderResultChart();
    },
  },
  computed: {
    chartData() {
      let seats = Array(this.parties.length).fill(0);
      for (let c in this.seats) {
        seats = this.seats[c].map(function (num, idx) {
          return seats[idx]+num;
        });
      }
      return {
        labels: this.parties,
        datasets: [
          {
            label: 'Results',
            backgroundColor: ["#0074D9", "#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA"],
            data: seats
          }
        ]
      }
    }
  }
}
</script>
