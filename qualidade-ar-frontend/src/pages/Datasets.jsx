import { useState } from 'react'
import Card from '../components/Card.jsx'

export default function Datasets() {
  const [file, setFile] = useState(null)

  const onUpload = (e) => {
    e.preventDefault()
    if (!file) return
    // TODO: integrate with backend upload endpoint using FormData
    alert(`Arquivo '${file.name}' pronto para envio (simulado).`)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Datasets</h2>

      <Card title="Upload de dataset (CSV)">
        <form className="flex flex-col md:flex-row gap-3 items-center" onSubmit={onUpload}>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="rounded-xl border border-slate-300 px-3 py-2 w-full md:w-auto"
          />
          <button className="px-4 py-2 rounded-xl bg-slate-900 text-white">Enviar</button>
        </form>
        <p className="text-sm text-slate-500 mt-3">
          Integre este formulário com o endpoint de upload do seu backend (ex.: <code>POST /datasets/upload</code>).
        </p>
      </Card>
    </div>
  )
}
