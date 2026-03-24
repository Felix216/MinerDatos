<template>
  <div class="container">
    <h1>Ranking de Palabras en Código</h1>
    
    <div class="controls">
      <label for="topN">Mostrar Top: {{ topN }}</label>
      <input 
        type="range" 
        id="topN" 
        min="5" 
        max="50" 
        v-model="topN" 
        @change="requestUpdate"
      >
    </div>

    <div class="chart-container">
      <Bar v-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
      <p v-else>Esperando datos del Miner...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const topN = ref(10)
const ws = ref(null)

const chartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Frecuencia de uso',
      backgroundColor: '#42b883',
      data: []
    }
  ]
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
})

const connectWebSocket = () => {
  ws.value = new WebSocket('ws://localhost:8000/ws')

  ws.value.onopen = () => {
    console.log('Conectado al servidor en tiempo real')
    requestUpdate()
  }

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    chartData.value = {
      labels: data.map(item => item.word),
      datasets: [{
        ...chartData.value.datasets[0],
        data: data.map(item => item.count)
      }]
    }
  }

  ws.value.onclose = () => {
    console.log('Desconectado. Intentando reconectar en 3s...')
    setTimeout(connectWebSocket, 3000)
  }
}

const requestUpdate = () => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({ action: 'set_top', value: topN.value }))
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) ws.value.close()
})
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  font-family: sans-serif;
  text-align: center;
}
.controls {
  margin: 20px 0;
}
.chart-container {
  height: 500px;
  position: relative;
}
</style>