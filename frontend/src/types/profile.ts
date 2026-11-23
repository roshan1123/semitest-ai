export type ProfileDeviceType = 'MOSFET' | 'Diode'

export type TestParameter = {
  id: string
  parameter_name: string
  unit: string
  lower_limit: number | null
  upper_limit: number | null
  nominal_value: number | null
  tolerance: number | null
  required: boolean
  evaluation_method: 'RANGE'
  created_at: string
  updated_at: string
}

export type TestProfile = {
  id: string
  name: string
  device_type: ProfileDeviceType
  version: number
  description: string | null
  is_active: boolean
  created_by: string
  created_at: string
  updated_at: string
  parameters: TestParameter[]
}
