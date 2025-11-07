import { useMemo } from 'react'
import Card from '../components/Card.jsx'
import Metric from '../components/Metric.jsx'
import LineChart from '../components/LineChart.jsx'
import { api } from '../services/api.js'
import { useApi } from '../hooks/useApi.js'
import { useState } from 'react'

export default function Dashboard() {
  const [llmAnalysis, setLlmAnalysis] = useState("Clique no botão para gerar a análise LLM.")
  const [llmLoading, setLlmLoading] = useState(false)
  
  const handleLlmAnalysis = async () => {
    setLlmLoading(true)
    try {
      // Usar a Estação Centro (ID 1) como exemplo
      const result = await api.analyzeLLM(1)
      setLlmAnalysis(result)
    } catch (error) {
      setLlmAnalysis(`Erro ao buscar análise LLM: ${error.message}`)
    } finally {
      setLlmLoading(false)
    }
  }
  
  // Example: const { data, loading, error } = useApi(() => api.latestReadings({ pollutant: "PM2.5" }), [])
  // For now, show mock data for the chart:
  const labels = useMemo(() => Array.from({ length: 24 }, (_, i) => `${i}:00`), [])
  const series = [
    { label: "PM2.5 (µg/m³)", data: [8,7,6,10,9,12,15,20,18,16,14,12,11,10,9,8,7,6,8,10,12,14,16,13] },
    { label: "PM10 (µg/m³)", data: [15,14,13,16,15,19,22,25,24,22,20,19,18,17,16,15,14,13,15,17,19,21,23,20] }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Metric label="Estações ativas" value="12" hint="Cadastradas no sistema" />
        <Metric label="Métricas monitoradas" value="6" hint="PM2.5, PM10, NO₂, O₃, CO, SO₂" />
        <Metric label="Previsões hoje" value="128" hint="Últimas 24h" />
        <Metric label="Status API" value="OK" hint="latência &lt; 120ms" />
      </div>

      <Card title="Séries temporais — Últimas 24h">
        <LineChart labels={labels} series={series} />
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card title="Alertas">
          <ul className="space-y-2">
            <li className="flex items-center justify-between">
              <span>PM2.5 alto na Estação Centro</span>
              <span className="badge badge-amber">atenção</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Comunicação instável — Estação Parque</span>
              <span className="badge badge-slate">observação</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Previsão de O₃ acima do normal</span>
              <span className="badge badge-green">monitorar</span>
            </li>
          </ul>
        </Card>

        <Card title="Ações rápidas">
          <div className="flex gap-3 flex-wrap">
            <button className="px-4 py-2 rounded-xl bg-slate-900 text-white">Atualizar previsões</button>
            <button className="px-4 py-2 rounded-xl border border-slate-300">Exportar CSV</button>
            <button className="px-4 py-2 rounded-xl border border-slate-300">Sincronizar estações</button>
          </div>
        </Card>
        
        <Card title="Análise LLM (Estação Centro)">
          <div className="flex flex-col gap-3">
            <pre className="whitespace-pre-wrap text-sm bg-slate-50 p-3 rounded-lg">{llmAnalysis}</pre>
            <button 
              className="px-4 py-2 rounded-xl bg-indigo-600 text-white disabled:bg-indigo-300"
              onClick={handleLlmAnalysis}
              disabled={llmLoading}
            >
              {llmLoading ? "Analisando..." : "Gerar Análise LLM (Últimas 24h)"}
            </button>
          </div>
        </Card>
      </div>
    </div>
  )
}
