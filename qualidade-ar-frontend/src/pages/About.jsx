import Card from '../components/Card.jsx'

export default function About() {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Sobre o Projeto</h2>
      <Card title="Qualidade do Ar — 2.0">
        <p className="text-slate-600 leading-relaxed">
          Interface moderna e responsiva para visualizar medições, estações e previsões de qualidade do ar.
          Construída com <strong>React + Vite</strong> e <strong>Tailwind</strong>, pronta para integrar com sua API
          (defina <code>VITE_API_BASE_URL</code> no <code>.env</code>).
        </p>
        <ul className="list-disc pl-6 mt-4 text-slate-700">
          <li>Dashboard com métricas e gráfico de séries temporais</li>
          <li>Listagem de estações com busca</li>
          <li>Página para solicitar previsões</li>
          <li>Upload de datasets (simulado — conecte ao backend)</li>
        </ul>
      </Card>
    </div>
  )
}
