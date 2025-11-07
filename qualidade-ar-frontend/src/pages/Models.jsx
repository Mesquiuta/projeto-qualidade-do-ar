import { useState } from 'react'
import Card from '../components/Card.jsx'

export default function Models() {
  const [form, setForm] = useState({ pollutant: "PM2.5", horizon: 24 })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    // TODO: integrate with api.predict
    await new Promise(r => setTimeout(r, 900))
    setResult({ message: "Previsão solicitada com sucesso.", jobId: Math.random().toString(36).slice(2) })
    setLoading(false)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Modelos &amp; Previsões</h2>

      <Card title="Rodar previsão">
        <form className="grid grid-cols-1 md:grid-cols-3 gap-4" onSubmit={onSubmit}>
          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Poluente</span>
            <select name="pollutant" value={form.pollutant} onChange={handleChange}
              className="rounded-xl border border-slate-300 px-3 py-2">
              <option>PM2.5</option>
              <option>PM10</option>
              <option>NO₂</option>
              <option>O₃</option>
              <option>CO</option>
              <option>SO₂</option>
            </select>
          </label>

          <label className="flex flex-col gap-1">
            <span className="text-sm text-slate-600">Horizonte (h)</span>
            <input name="horizon" type="number" min="1" max="168" value={form.horizon}
              onChange={handleChange} className="rounded-xl border border-slate-300 px-3 py-2" />
          </label>

          <div className="flex items-end">
            <button disabled={loading} className="px-4 py-2 rounded-xl bg-slate-900 text-white">
              {loading ? "Processando..." : "Solicitar previsão"}
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-4 text-sm">
            <div className="badge badge-green">ok</div> {result.message} (jobId: <code>{result.jobId}</code>)
          </div>
        )}
      </Card>
    </div>
  )
}
