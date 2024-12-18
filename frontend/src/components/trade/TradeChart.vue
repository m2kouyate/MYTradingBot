<template>
  <div class="trade-chart">
    <h3 class="chart-title">{{ title }}</h3>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import Chart from 'chart.js/auto';

export default defineComponent({
  name: 'TradeChart',
  props: {
    title: {
      type: String,
      default: 'Trade Chart',
    },
    data: {
      type: Object,
      required: true, // Данные графика
    },
    options: {
      type: Object,
      default: () => ({}), // Опции графика
    },
  },
  setup(props) {
    const chartCanvas = ref<HTMLCanvasElement | null>(null);
    let chartInstance: Chart | null = null;

    onMounted(() => {
      if (chartCanvas.value) {
        chartInstance = new Chart(chartCanvas.value, {
          type: 'line', // Тип графика: line, bar, etc.
          data: props.data,
          options: props.options,
        });
      }
    });

    return {
      chartCanvas,
    };
  },
});
</script>

<style scoped>
.trade-chart {
  width: 100%;
  max-width: 600px;
  margin: auto;
}

.chart-title {
  text-align: center;
  margin-bottom: 10px;
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
