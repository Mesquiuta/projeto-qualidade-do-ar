import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

export default function LineChart({ labels = [], series = [], title }) {
  const data = {
    labels,
    datasets: series.map((s, i) => ({
      label: s.label,
      data: s.data,
      tension: 0.35,
    })),
  }
  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: title ? { display: true, text: title } : undefined,
    },
    interaction: { mode: 'index', intersect: false },
    scales: {
      x: { ticks: { autoSkip: true, maxTicksLimit: 12 } },
      y: { beginAtZero: true }
    }
  }
  return <Line data={data} options={options} />
}
