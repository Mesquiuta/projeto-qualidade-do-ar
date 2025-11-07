export default function Card({ title, right, children }) {
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h3 className="text-base font-semibold">{title}</h3>
        {right}
      </div>
      <div className="card-body">{children}</div>
    </div>
  )
}
