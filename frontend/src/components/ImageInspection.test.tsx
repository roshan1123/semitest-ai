import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ImageInspection } from './ImageInspection'

vi.mock('../services/devices', () => ({
  listDevices: vi.fn().mockResolvedValue([]),
}))

vi.mock('../services/inspections', () => ({
  analyzeImage: vi.fn(),
}))

describe('Image inspection validation', () => {
  it('renders simulation disclaimer and file input', async () => {
    render(<ImageInspection />)

    expect(screen.getByText(/Experimental computer-vision predictions only/)).toBeInTheDocument()
    expect(screen.getByText(/JPEG or PNG/)).toBeInTheDocument()
    expect(screen.getByText('Analyze Image')).toBeInTheDocument()
  })
})
