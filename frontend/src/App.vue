<template>
  <div class="container">
    <h1>Ranking de Palabras</h1>
    
    <div class="controls">
      <label for="topN">Top {{ topN }}</label>
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
      <p v-else class="loading">Buscando datos en GitHub...</p>
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
      label: 'Frecuencia',
      backgroundColor: '#38bdf8',
      borderRadius: 4,
      data: []
    }
  ]
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1e293b',
      titleColor: '#f8fafc',
      bodyColor: '#f8fafc',
      borderColor: '#334155',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      ticks: { color: '#94a3b8' }, 
      grid: { display: false },
      border: { display: false }
    },
    y: {
      ticks: { 
        color: '#e2e8f0', 
        font: { size: 12 }
      },
      grid: { display: false },
      border: { display: false }
    }
  }
})

const connectWebSocket = () => {
  ws.value = new WebSocket('ws://localhost:8000/ws')

  ws.value.onopen = () => {
    console.log('Conectado al servidor')
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
    setTimeout(connectWebSocket, 3000)
  }
}

const requestUpdate = () => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({ action: 'set_top', value: topN.value }))
  }
}

onMounted(() => connectWebSocket())
onUnmounted(() => { if (ws.value) ws.value.close() })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

:global(body) {
  background-color: #0f172a; 
  margin: 0;
}

.container {
  max-width: 800px;
  margin: 40px auto;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #e2e8f0; 
}

h1 {
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: #f8fafc; 
  margin-bottom: 2rem;
}

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 2rem;
  background: #1e293b; 
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid #334155; 
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

label {
  font-weight: 500;
  font-size: 0.9rem;
  color: #cbd5e1; 
}

input[type=range] {
  accent-color: #38bdf8; 
  width: 200px;
  cursor: pointer;
}

.chart-container {
  height: 60vh;
  min-height: 500px;
  position: relative;
}

.loading {
  text-align: center;
  color: #64748b; 
  font-size: 0.9rem;
  margin-top: 100px;
}
</style>