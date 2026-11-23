import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { Profiles } from './Profiles'

vi.mock('../services/profiles', () => ({
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

describe('Test profile management', () => {
  it('renders profile details and the create-profile form', async () => {
    render(<Profiles />)

    expect(await screen.findByText('Illustrative MOSFET Profile')).toBeInTheDocument()
    expect(screen.getByText('VGS Threshold')).toBeInTheDocument()
    expect(screen.getByText(/1.5 to 4.5/)).toBeInTheDocument()

    fireEvent.click(screen.getByText('Create Profile'))
    expect(screen.getByText('Save Profile')).toBeInTheDocument()
  })
})
