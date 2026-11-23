import { useEffect, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'

import { getBackendHealth, type HealthStatus } from './services/health'
import { listDevices, registerDevice, updateDevice } from './services/devices'
import type { Device, DeviceCreate, DeviceType } from './types/device'
import { Profiles } from './components/Profiles'
import { TestExecution } from './components/TestExecution'
import { AnalyticsDashboard } from './components/AnalyticsDashboard'
import { ImageInspection } from './components/ImageInspection'
import { OverviewDashboard } from './components/OverviewDashboard'

type HealthState =
  | { status: 'loading' }
  | { status: 'connected'; health: HealthStatus }
  | { status: 'error'; message: string }

type AppTab =
  | 'Overview'
  | 'Devices'
  | 'Profiles'
  | 'Testing'
  | 'Analytics'
  | 'Inspection'
  | 'System'

const tabs: AppTab[] = [
  'Overview',
  'Devices',
  'Profiles',
  'Testing',
  'Analytics',
  'Inspection',
  'System',
]

const emptyForm: DeviceCreate = {
  part_number: '',
  device_type: 'MOSFET',
  manufacturer: '',
  description: '',
  package_type: '',
  datasheet_reference: '',
  status: 'Active',
}

function App() {
  const [activeTab, setActiveTab] = useState<AppTab>('Overview')
  const [health, setHealth] = useState<HealthState>({ status: 'loading' })
  const [devices, setDevices] = useState<Device[]>([])
  const [search, setSearch] = useState('')
  const [deviceType, setDeviceType] = useState('')
  const [form, setForm] = useState<DeviceCreate>(emptyForm)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [page, setPage] = useState(0)
  const pageSize = 20

  const loadDevices = async () => {
    setLoading(true)
    setError('')
    try {
      setDevices(await listDevices(search, deviceType, pageSize, page * pageSize))
    } catch {
      setError('Unable to load devices from the backend.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let active = true

    getBackendHealth()
      .then((result) => {
        if (active) setHealth({ status: 'connected', health: result })
      })
      .catch((error: unknown) => {
        if (active) {
          setHealth({
            status: 'error',
            message: error instanceof Error ? error.message : 'Backend unavailable',
          })
        }
      })

    loadDevices()
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    const timeout = window.setTimeout(loadDevices, 250)
    return () => window.clearTimeout(timeout)
  }, [search, deviceType, page])

  const submitDevice = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    setNotice('')
    try {
      await registerDevice({
        ...form,
        rated_voltage: form.rated_voltage || undefined,
        rated_current: form.rated_current || undefined,
      })
      setForm(emptyForm)
      setNotice('Device registered successfully.')
      await loadDevices()
    } catch (submitError: unknown) {
      setError(
        axiosErrorMessage(submitError) ||
          'Unable to register the device. Check the required fields.',
      )
    }
  }

  const toggleStatus = async (device: Device) => {
    setError('')
    setNotice('')
    try {
      await updateDevice(device.id, {
        status: device.status === 'Active' ? 'Inactive' : 'Active',
      })
      setNotice(`Device ${device.part_number} status updated.`)
      await loadDevices()
    } catch {
      setError('Unable to update the device status.')
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-900/95 backdrop-blur">
        <div className="mx-auto max-w-6xl px-6 pt-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-400">
                Semiconductor Test Intelligence
              </p>
              <h1 className="mt-1 text-xl font-semibold">SemiTest AI</h1>
            </div>
            <span className="rounded-full border border-amber-400/40 bg-amber-400/10 px-3 py-1 text-xs font-bold tracking-wide text-amber-300">
              SIMULATION MODE
            </span>
          </div>
          <nav aria-label="Primary navigation" className="mt-4 flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={activeTab === tab}
                onClick={() => setActiveTab(tab)}
                className={`whitespace-nowrap border-b-2 px-4 py-3 text-sm font-semibold transition ${
                  activeTab === tab
                    ? 'border-cyan-400 text-cyan-300'
                    : 'border-transparent text-slate-400 hover:border-slate-600 hover:text-slate-200'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 py-8">
        {activeTab === 'Overview' && (
          <OverviewDashboard onNavigate={(target) => setActiveTab(target)} />
        )}

        {activeTab === 'Devices' && (
          <>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm text-slate-400">Device master</p>
                <h2 className="text-2xl font-semibold">Device Management</h2>
              </div>
            </div>

            {error && (
              <p role="alert" className="mb-4 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-red-200">
                {error}
              </p>
            )}
            {notice && (
              <p className="mb-4 rounded-lg border border-emerald-400/20 bg-emerald-400/5 p-3 text-emerald-200">
                {notice}
              </p>
            )}

            <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
              <form onSubmit={submitDevice} className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
                <h3 className="mb-4 text-lg font-semibold">Register Device</h3>
                <div className="space-y-3">
                  <Field label="Part number *">
                    <input required value={form.part_number} onChange={(event) => setForm({ ...form, part_number: event.target.value })} />
                  </Field>
                  <Field label="Device type *">
                    <select value={form.device_type} onChange={(event) => setForm({ ...form, device_type: event.target.value as DeviceType })}>
                      <option value="MOSFET">MOSFET</option>
                      <option value="Diode">Diode</option>
                    </select>
                  </Field>
                  <Field label="Manufacturer">
                    <input value={form.manufacturer ?? ''} onChange={(event) => setForm({ ...form, manufacturer: event.target.value })} />
                  </Field>
                  <Field label="Package type">
                    <input value={form.package_type ?? ''} onChange={(event) => setForm({ ...form, package_type: event.target.value })} />
                  </Field>
                  <Field label="Rated voltage">
                    <input type="number" min="0" step="any" value={form.rated_voltage ?? ''} onChange={(event) => setForm({ ...form, rated_voltage: event.target.value ? Number(event.target.value) : undefined })} />
                  </Field>
                  <Field label="Rated current">
                    <input type="number" min="0" step="any" value={form.rated_current ?? ''} onChange={(event) => setForm({ ...form, rated_current: event.target.value ? Number(event.target.value) : undefined })} />
                  </Field>
                  <Field label="Description">
                    <textarea value={form.description ?? ''} onChange={(event) => setForm({ ...form, description: event.target.value })} />
                  </Field>
                  <button type="submit" className="w-full rounded-md bg-cyan-500 px-4 py-2 font-semibold text-slate-950 hover:bg-cyan-400">
                    Register Device
                  </button>
                </div>
              </form>

              <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
                <div className="mb-4 grid gap-3 sm:grid-cols-[1fr_180px]">
                  <input
                    aria-label="Search devices"
                    placeholder="Search part number or manufacturer"
                    value={search}
                    onChange={(event) => {
                      setPage(0)
                      setSearch(event.target.value)
                    }}
                  />
                  <select
                    aria-label="Filter device type"
                    value={deviceType}
                    onChange={(event) => {
                      setPage(0)
                      setDeviceType(event.target.value)
                    }}
                  >
                    <option value="">All types</option>
                    <option value="MOSFET">MOSFET</option>
                    <option value="Diode">Diode</option>
                  </select>
                </div>

                {loading ? (
                  <p className="py-10 text-center text-slate-400">Loading devices...</p>
                ) : devices.length === 0 ? (
                  <p className="py-10 text-center text-slate-400">No devices match this view.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                        <tr>
                          <th className="px-3 py-3">Part number</th>
                          <th className="px-3 py-3">Type</th>
                          <th className="px-3 py-3">Manufacturer</th>
                          <th className="px-3 py-3">Status</th>
                          <th className="px-3 py-3">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {devices.map((device) => (
                          <tr key={device.id} className="border-b border-slate-800">
                            <td className="px-3 py-3 font-medium">{device.part_number}</td>
                            <td className="px-3 py-3">{device.device_type}</td>
                            <td className="px-3 py-3">{device.manufacturer || '—'}</td>
                            <td className="px-3 py-3">
                              <span className={device.status === 'Active' ? 'text-emerald-300' : 'text-slate-400'}>
                                {device.status}
                              </span>
                            </td>
                            <td className="px-3 py-3">
                              <button type="button" onClick={() => toggleStatus(device)} className="text-sm text-cyan-300 hover:text-cyan-200">
                                {device.status === 'Active' ? 'Deactivate' : 'Activate'}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                {!loading && (
                  <div className="mt-4 flex items-center justify-between text-sm">
                    <button type="button" disabled={page === 0} onClick={() => setPage((current) => Math.max(0, current - 1))} className="rounded-md border border-slate-700 px-3 py-2 disabled:opacity-40">
                      Previous
                    </button>
                    <span className="text-slate-400">Page {page + 1}</span>
                    <button type="button" disabled={devices.length < pageSize} onClick={() => setPage((current) => current + 1)} className="rounded-md border border-slate-700 px-3 py-2 disabled:opacity-40">
                      Next
                    </button>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {activeTab === 'Profiles' && <Profiles />}
        {activeTab === 'Testing' && <TestExecution />}
        {activeTab === 'Analytics' && <AnalyticsDashboard />}
        {activeTab === 'Inspection' && <ImageInspection />}
        {activeTab === 'System' && (
          <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
            <p className="text-sm text-slate-400">System information</p>
            <h2 className="text-xl font-semibold">Simulation Environment</h2>
            {health.status === 'connected' ? (
              <dl className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-lg border border-slate-800 p-4">
                  <dt className="text-sm text-slate-400">Backend</dt>
                  <dd className="mt-1 text-emerald-300">{health.health.status}</dd>
                </div>
                <div className="rounded-lg border border-slate-800 p-4">
                  <dt className="text-sm text-slate-400">Environment</dt>
                  <dd className="mt-1">{health.health.environment}</dd>
                </div>
                <div className="rounded-lg border border-slate-800 p-4">
                  <dt className="text-sm text-slate-400">Operating mode</dt>
                  <dd className="mt-1 text-amber-300">{health.health.simulation_mode}</dd>
                </div>
              </dl>
            ) : health.status === 'error' ? (
              <p role="alert" className="mt-5 text-red-300">{health.message}</p>
            ) : (
              <p className="mt-5 text-slate-400">Checking backend...</p>
            )}
          </section>
        )}
      </section>
    </main>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm text-slate-300">
      <span className="mb-1 block">{label}</span>
      {children}
    </label>
  )
}

function axiosErrorMessage(error: unknown): string | null {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = (error as { response?: { data?: { detail?: string } } }).response
    if (response?.data?.detail) return response.data.detail
  }
  return null
}

export default App
