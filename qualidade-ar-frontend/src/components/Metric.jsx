export default function Metric({ label, value, hint }) {
  return (
    <div className="card">
      <div className="card-body">
        <div className="text-sm text-slate-500">{label}</div>
        <div className="text-3xl font-bold leading-tight">{value}</div>
        {hint && <div className="text-xs text-slate-500 mt-1">{hint}</div>}
      </div>
    </div>
  )
}
