

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Erro ${res.status} - ${text || res.statusText}`)
  }
  const contentType = res.headers.get("content-type") || ""
  if (contentType.includes("application/json")) return res.json()
  return res.text()
}

// Example endpoints (customize to your backend)
export const api = {
  health: () => request("/health"),
  listStations: () => request("/stations"),
  stationDetail: (id) => request(`/stations/${id}`),
  latestReadings: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/readings/latest${q ? `?${q}` : ""}`)
  },
  predict: (payload) => request("/predict", { method: "POST", body: JSON.stringify(payload) }),
  analyzeLLM: (stationId) => request(`/analyze-llm?station_id=${stationId}`),
}
