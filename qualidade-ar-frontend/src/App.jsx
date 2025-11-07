import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import Stations from './pages/Stations.jsx'
import Models from './pages/Models.jsx'
import Datasets from './pages/Datasets.jsx'
import About from './pages/About.jsx'

function Sidebar() {
  const items = [
    { to: "/", label: "Dashboard", icon: "📊", end: true },
    { to: "/stations", label: "Estações", icon: "🛰️" },
    { to: "/models", label: "Modelos", icon: "🧠" },
    { to: "/datasets", label: "Datasets", icon: "🗂️" },
    { to: "/about", label: "Sobre", icon: "ℹ️" },
  ]

  return (
    <aside className="w-64 bg-white border-r border-slate-200 p-4 hidden md:block">
      <div className="mb-6">
        <div className="text-2xl font-bold tracking-tight">Qualidade do Ar</div>
        <div className="text-slate-500 text-sm">Dashboard &amp; Previsões</div>
      </div>
      <nav className="flex flex-col gap-1">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            end={it.end}
            className={({ isActive }) =>
              `nav-link ${isActive ? "nav-link-active" : ""}`
            }
          >
            <span className="text-lg">{it.icon}</span>
            <span>{it.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

function Topbar() {
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-slate-200">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
        <div className="md:hidden font-semibold">Qualidade do Ar</div>
        <div className="flex items-center gap-3">
          <input
            placeholder="Buscar..."
            className="hidden md:block rounded-xl border border-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
          <div className="w-9 h-9 rounded-full bg-slate-200" />
        </div>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Topbar />
      <div className="mx-auto max-w-7xl grid grid-cols-1 md:grid-cols-[16rem_1fr]">
        <Sidebar />
        <main className="p-4 md:p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stations" element={<Stations />} />
            <Route path="/models" element={<Models />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
