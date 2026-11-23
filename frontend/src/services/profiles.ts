import axios from 'axios'

import type { TestProfile } from '../types/profile'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export async function listProfiles(
  deviceType = '',
): Promise<TestProfile[]> {
  const response = await axios.get<TestProfile[]>(`${API_BASE_URL}/profiles`, {
    params: deviceType ? { device_type: deviceType } : {},
  })
  return response.data
}

export async function updateProfile(
  profileId: string,
  payload: { is_active?: boolean },
): Promise<TestProfile> {
  const response = await axios.put<TestProfile>(
    `${API_BASE_URL}/profiles/${profileId}`,
    payload,
  )
  return response.data
}

export async function createProfile(payload: {
  name: string
  device_type: 'MOSFET' | 'Diode'
  description?: string
  is_active: boolean
  created_by: string
  parameters: Array<{
    parameter_name: string
    unit: string
    lower_limit: number | null
    upper_limit: number | null
    nominal_value: number | null
    tolerance: number | null
    required: boolean
    evaluation_method: 'RANGE'
  }>
}): Promise<TestProfile> {
  const response = await axios.post<TestProfile>(`${API_BASE_URL}/profiles`, payload)
  return response.data
}
