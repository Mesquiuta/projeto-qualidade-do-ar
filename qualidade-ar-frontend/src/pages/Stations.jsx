import { useState } from 'react'
import Card from '../components/Card.jsx'

const MOCK = [
  { id: "CENTRO", name: "Estação Centro", city: "Cabreúva", status: "online", metrics: ["PM2.5","PM10","O₃"] },
  { id: "PARQUE", name: "Estação Parque", city: "Jundiaí", status: "online", metrics: ["PM2.5","NO₂"] },
  { id: "IND", name: "Estação Industrial", city: "Itupeva", status: "offline", metrics: ["PM10","SO₂"] },
]

export default function Stations() {
  const [query, setQuery] = useState("")

  const filtered = MOCK.filter(s =>
    s.name.toLowerCase().includes(query.toLowerCase()) ||
    s.city.toLowerCase().includes(query.toLowerCase()) ||
    s.id.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
        <h2 className="text-xl font-semibold">Estações</h2>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Buscar por nome, cidade, ID..."
          className="rounded-xl border border-slate-300 px-3 py-2 w-full md:w-80"
        />
      </div>

      <Card title="Lista de Estações">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-2">ID</th>
                <th className="py-2">Nome</th>
                <th className="py-2">Cidade</th>
                <th className="py-2">Status</th>
                <th className="py-2">Métricas</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="py-3 font-mono">{s.id}</td>
                  <td className="py-3">{s.name}</td>
                  <td className="py-3">{s.city}</td>
                  <td className="py-3">
                    <span className={`badge ${s.status === "online" ? "badge-green" : "badge-amber"}`}>
                      {s.status}
                    </span>
                  </td>
                  <td className="py-3">{s.metrics.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
