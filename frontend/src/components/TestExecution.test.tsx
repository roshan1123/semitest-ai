import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { TestExecution } from './TestExecution'

vi.mock('../services/devices', () => ({
  listDevices: vi.fn().mockResolvedValue([
    {
      id: 'device-1',
      part_number: 'MOS-TEST',
      device_type: 'MOSFET',
      manufacturer: null,
      description: null,
      package_type: null,
      datasheet_reference: null,
      rated_voltage: null,
      rated_current: null,
      status: 'Active',
      created_at: '2026-11-23T16:53:36Z',
      updated_at: '2026-11-23T16:53:36Z',
    },
  ]),
}))

vi.mock('../services/profiles', () => ({
  listProfiles: vi.fn().mockResolvedValue([
    {
      id: 'profile-1',
      name: 'Illustrative MOSFET Profile',
      device_type: 'MOSFET',
      version: 1,
      description: null,
      is_active: true,
      created_by: 'Administrator',
      created_at: '2026-11-23T16:53:36Z',
      updated_at: '2026-11-23T16:53:36Z',
      parameters: [],
    },
  ]),
}))

vi.mock('../services/tests', () => ({
  executeTest: vi.fn(),
  listTests: vi.fn().mockResolvedValue([
    {
      id: 'test-1',
      device_id: 'device-1',
      device_part_number: 'MOS-TEST',
      device_category: 'MOSFET',
      profile_id: 'profile-1',
      profile_version: 1,
      scenario: 'NORMAL',
      simulation_mode: 'SIMULATION_ONLY',
      simulator_version: 'simulation-engine-1.0',
      random_seed: 123,
      operator: 'Operator',
      overall_status: 'PASS',
      execution_started_at: '2026-11-23T16:53:36Z',
      execution_completed_at: '2026-11-23T16:53:36Z',
      duration_ms: 1,
      test_notes: null,
      created_at: '2026-11-23T16:53:36Z',
    },
  ]),
}))

describe('Simulated test workflow', () => {
  it('renders execution controls and empty history', async () => {
    render(<TestExecution />)

    expect(await screen.findByText('Execute Simulated Test')).toBeInTheDocument()
    expect((await screen.findAllByText('MOS-TEST')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('PDF').length).toBeGreaterThan(0)
    expect(screen.getAllByText('CSV').length).toBeGreaterThan(0)
    expect(screen.getAllByText('NORMAL').length).toBeGreaterThan(0)
  })
})
