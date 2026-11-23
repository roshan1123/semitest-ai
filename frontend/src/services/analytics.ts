import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export type AnalyticsSummary = {
  total_registered_devices: number
  total_test_executions: number
  pass_count: number
  fail_count: number
  review_count: number
  pass_percentage: number
}

export type TrendPoint = {
  date: string
  executions: number
  PASS: number
  FAIL: number
  REVIEW: number
}

export type FailurePoint = {
  parameter_name: string
  failure_count: number
  failure_percentage: number
}

export type DeviceStatistic = {
  device_part_number: string
  device_category: string
  total: number
  PASS: number
  FAIL: number
  REVIEW: number
}

async function get<T>(path: string): Promise<T> {
  const response = await axios.get<T>(`${API_BASE_URL}/analytics/${path}`)
  return response.data
}

export const getAnalyticsSummary = () => get<AnalyticsSummary>('summary')
export const getAnalyticsTrends = () => get<TrendPoint[]>('trends')
export const getAnalyticsFailures = () => get<FailurePoint[]>('failures')
export const getAnalyticsDevices = () => get<DeviceStatistic[]>('devices')
