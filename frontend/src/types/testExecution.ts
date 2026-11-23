export type TestStatus = 'PASS' | 'FAIL' | 'REVIEW'
export type TestScenario = 'NORMAL' | 'BORDERLINE' | 'ABNORMAL' | 'INVALID'

export type MeasurementResult = {
  id: string
  test_execution_id: string
  parameter_name: string
  measured_value: number | null
  unit: string
  lower_limit: number | null
  upper_limit: number | null
  status: TestStatus
  measurement_timestamp: string
  simulation_flag: boolean
  test_conditions: string | null
}

export type TestExecution = {
  id: string
  device_id: string
  device_part_number: string
  device_category: string
  profile_id: string
  profile_version: number
  scenario: string
  simulation_mode: string
  simulator_version: string
  random_seed: number | null
  operator: string
  overall_status: TestStatus
  execution_started_at: string
  execution_completed_at: string
  duration_ms: number
  test_notes: string | null
  created_at: string
  measurements?: MeasurementResult[]
}
