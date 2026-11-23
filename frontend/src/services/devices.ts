import axios from 'axios'

import type { Device, DeviceCreate } from '../types/device'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export async function listDevices(
  search = '',
  deviceType = '',
  limit = 100,
  offset = 0,
): Promise<Device[]> {
  const response = await axios.get<Device[]>(`${API_BASE_URL}/devices`, {
    params: {
      ...(search ? { search } : {}),
      ...(deviceType ? { device_type: deviceType } : {}),
      limit,
      offset,
    },
  })
  return response.data
}

export async function registerDevice(payload: DeviceCreate): Promise<Device> {
  const response = await axios.post<Device>(`${API_BASE_URL}/devices`, payload)
  return response.data
}

export async function updateDevice(
  deviceId: string,
  payload: Partial<DeviceCreate>,
): Promise<Device> {
  const response = await axios.put<Device>(
    `${API_BASE_URL}/devices/${deviceId}`,
    payload,
  )
  return response.data
}
