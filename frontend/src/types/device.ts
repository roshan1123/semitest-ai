export type DeviceType = 'MOSFET' | 'Diode'
export type DeviceStatus = 'Active' | 'Inactive'

export type Device = {
  id: string
  part_number: string
  device_type: DeviceType
  manufacturer: string | null
  description: string | null
  package_type: string | null
  datasheet_reference: string | null
  rated_voltage: number | null
  rated_current: number | null
  status: DeviceStatus
  created_at: string
  updated_at: string
}

export type DeviceCreate = {
  part_number: string
  device_type: DeviceType
  manufacturer?: string
  description?: string
  package_type?: string
  datasheet_reference?: string
  rated_voltage?: number
  rated_current?: number
  status: DeviceStatus
}
