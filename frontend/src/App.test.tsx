import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import App from './App'

vi.mock('./services/health', () => ({
  getBackendHealth: vi.fn().mockResolvedValue({
    status: 'healthy',
    app_name: 'SemiTest AI',
    environment: 'test',
    simulation_mode: 'SIMULATION_ONLY',
    timestamp: '2026-11-23T16:53:36Z',
  }),
}))

vi.mock('./services/devices', () => ({
  listDevices: vi.fn().mockResolvedValue([
    {
      id: 'device-1',
      part_number: 'MOS-TEST',
      device_type: 'MOSFET',
      manufacturer: 'Illustrative Semiconductor',
      description: null,
      package_type: 'TO-220',
      datasheet_reference: null,
      rated_voltage: 100,
      rated_current: 33,
      status: 'Active',
      created_at: '2026-11-23T16:53:36Z',
      updated_at: '2026-11-23T16:53:36Z',
    },
  ]),
  registerDevice: vi.fn(),
  updateDevice: vi.fn(),
}))

vi.mock('./services/profiles', () => ({
  listProfiles: vi.fn().mockResolvedValue([
    {
      id: 'profile-1',
      name: 'Illustrative MOSFET Profile',
      device_type: 'MOSFET',
      version: 1,
      description: 'Illustrative limits for prototype simulation only.',
      is_active: true,
      created_by: 'Administrator',
      created_at: '2026-11-23T16:53:36Z',
      updated_at: '2026-11-23T16:53:36Z',
      parameters: [
        {
          id: 'parameter-1',
          parameter_name: 'VGS Threshold',
          unit: 'V',
          lower_limit: 1.5,
          upper_limit: 4.5,
          nominal_value: 3,
          tolerance: 0.5,
          required: true,
          evaluation_method: 'RANGE',
          created_at: '2026-11-23T16:53:36Z',
          updated_at: '2026-11-23T16:53:36Z',
        },
      ],
    },
  ]),
  createProfile: vi.fn(),
  updateProfile: vi.fn(),
}))

vi.mock('./services/tests', () => ({
  executeTest: vi.fn(),
  listTests: vi.fn().mockResolvedValue([]),
  getTest: vi.fn(),
}))

vi.mock('./services/analytics', () => ({
  getAnalyticsSummary: vi.fn().mockResolvedValue({
    total_registered_devices: 2,
    total_test_executions: 0,
    pass_count: 0,
    fail_count: 0,
    review_count: 0,
    pass_percentage: 0,
  }),
  getAnalyticsTrends: vi.fn().mockResolvedValue([]),
  getAnalyticsFailures: vi.fn().mockResolvedValue([]),
  getAnalyticsDevices: vi.fn().mockResolvedValue([]),
}))

vi.mock('./services/inspections', () => ({
  analyzeImage: vi.fn(),
}))

describe('Phase 1 device application shell', () => {
  it('shows the simulation mode, backend status, and device data', async () => {
    render(<App />)

    expect(screen.getByText('SIMULATION MODE')).toBeInTheDocument()
    expect(screen.getByText('Simulation Overview')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('tab', { name: 'Devices' }))
    expect((await screen.findAllByText('MOS-TEST')).length).toBeGreaterThan(0)

    fireEvent.click(screen.getByRole('tab', { name: 'Profiles' }))
    expect((await screen.findAllByText('Illustrative MOSFET Profile')).length).toBeGreaterThan(0)

    fireEvent.click(screen.getByRole('tab', { name: 'Analytics' }))
    expect(await screen.findByText('Analytics Dashboard')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('tab', { name: 'System' }))
    expect(await screen.findByText('SIMULATION_ONLY')).toBeInTheDocument()
  })
})
