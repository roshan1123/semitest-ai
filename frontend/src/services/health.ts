import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export type HealthStatus = {
  status: 'healthy'
  app_name: string
  environment: string
  simulation_mode: 'SIMULATION_ONLY'
  timestamp: string
}

export async function getBackendHealth(): Promise<HealthStatus> {
  const response = await axios.get<HealthStatus>(`${API_BASE_URL}/health`, {
    timeout: 5000,
  })
  return response.data
}
