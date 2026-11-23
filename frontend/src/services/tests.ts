import axios from 'axios'

import type { TestExecution, TestScenario } from '../types/testExecution'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export async function executeTest(payload: {
  device_id: string
  profile_id: string
  scenario: TestScenario
  random_seed: number | null
  operator: string
  test_notes?: string
}): Promise<TestExecution> {
  const response = await axios.post<TestExecution>(
    `${API_BASE_URL}/tests/execute`,
    payload,
  )
  return response.data
}

export async function listTests(): Promise<TestExecution[]> {
  const response = await axios.get<TestExecution[]>(`${API_BASE_URL}/tests`)
  return response.data
}

export async function getTest(testId: string): Promise<TestExecution> {
  const response = await axios.get<TestExecution>(`${API_BASE_URL}/tests/${testId}`)
  return response.data
}
