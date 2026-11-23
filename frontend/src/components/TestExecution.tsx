import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { listDevices } from '../services/devices'
import { listProfiles } from '../services/profiles'
import { executeTest, listTests } from '../services/tests'
import type { Device } from '../types/device'
import type { TestProfile } from '../types/profile'
import type { TestExecution as TestExecutionRecord, TestScenario } from '../types/testExecution'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export function TestExecution() {
  const [devices, setDevices] = useState<Device[]>([])
  const [profiles, setProfiles] = useState<TestProfile[]>([])
  const [history, setHistory] = useState<TestExecutionRecord[]>([])
  const [deviceId, setDeviceId] = useState('')
  const [profileId, setProfileId] = useState('')
  const [scenario, setScenario] = useState<TestScenario>('NORMAL')
  const [seed, setSeed] = useState('')
  const [operator, setOperator] = useState('Operator')
  const [notes, setNotes] = useState('')
  const [result, setResult] = useState<TestExecutionRecord | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const loadHistory = async () => {
    try {
      setHistory(await listTests())
    } catch {
      setError('Unable to load test history.')
    }
  }

  useEffect(() => {
    Promise.all([listDevices('', ''), listProfiles('')])
      .then(([deviceList, profileList]) => {
        setDevices(deviceList)
        setProfiles(profileList)
      })
      .catch(() => setError('Unable to load test selections.'))
    loadHistory()
  }, [])

  useEffect(() => {
    if (!deviceId) return
    const device = devices.find((item) => item.id === deviceId)
    if (device) {
      const matching = profiles.find(
        (item) => item.device_type === device.device_type && item.is_active,
      )
      setProfileId(matching?.id ?? '')
    }
  }, [deviceId, devices, profiles])

  const submitTest = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const completed = await executeTest({
        device_id: deviceId,
        profile_id: profileId,
        scenario,
        random_seed: seed ? Number(seed) : null,
        operator,
        test_notes: notes,
      })
      setResult(completed)
      await loadHistory()
    } catch (error: unknown) {
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const response = (error as { response?: { data?: { detail?: string } } }).response
        setError(response?.data?.detail ?? 'Test execution failed.')
      } else {
        setError('Test execution failed.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="mb-4">
        <p className="text-sm text-slate-400">Phase 4</p>
        <h2 className="text-xl font-semibold">Simulated Test Execution</h2>
      </div>

      {error && (
        <p role="alert" className="mb-4 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-red-200">
          {error}
        </p>
      )}

      <form onSubmit={submitTest} className="grid gap-3 rounded-lg border border-slate-800 p-4 md:grid-cols-5">
        <label className="text-sm">
          Device *
          <select required value={deviceId} onChange={(event) => setDeviceId(event.target.value)}>
            <option value="">Select device</option>
            {devices.map((device) => (
              <option key={device.id} value={device.id}>{device.part_number}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Profile *
          <select required value={profileId} onChange={(event) => setProfileId(event.target.value)}>
            <option value="">Select profile</option>
            {profiles.map((profile) => (
              <option key={profile.id} value={profile.id}>{profile.name}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Scenario
          <select value={scenario} onChange={(event) => setScenario(event.target.value as TestScenario)}>
            <option value="NORMAL">NORMAL</option>
            <option value="BORDERLINE">BORDERLINE</option>
            <option value="ABNORMAL">ABNORMAL</option>
            <option value="INVALID">INVALID</option>
          </select>
        </label>
        <label className="text-sm">
          Random seed
          <input type="number" value={seed} onChange={(event) => setSeed(event.target.value)} />
        </label>
        <label className="text-sm">
          Operator
          <input value={operator} onChange={(event) => setOperator(event.target.value)} />
        </label>
        <label className="text-sm md:col-span-4">
          Notes
          <input value={notes} onChange={(event) => setNotes(event.target.value)} />
        </label>
        <button disabled={loading} type="submit" className="mt-auto rounded-md bg-cyan-500 px-3 py-2 font-semibold text-slate-950 disabled:opacity-50">
          {loading ? 'Executing...' : 'Execute Simulated Test'}
        </button>
      </form>

      {result && (
        <div className="mt-5 rounded-lg border border-slate-800 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Test result · {result.id}</p>
              <h3 className="text-lg font-semibold">{result.device_part_number}</h3>
            </div>
            <span className={statusColor(result.overall_status)}>{result.overall_status}</span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            {result.scenario} · Profile v{result.profile_version} · SIMULATION ONLY
          </p>
          <div className="mt-3 flex gap-3">
            <a
              href={`${API_BASE_URL}/reports/${result.id}/pdf`}
              className="rounded-md border border-cyan-400 px-3 py-2 text-sm font-semibold text-cyan-300"
            >
              Download PDF
            </a>
            <a
              href={`${API_BASE_URL}/reports/${result.id}/csv`}
              className="rounded-md border border-slate-600 px-3 py-2 text-sm font-semibold text-slate-200"
            >
              Download CSV
            </a>
          </div>
          {result.measurements && (
            <table className="mt-4 w-full text-left text-sm">
              <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                <tr>
                  <th className="py-2">Measurement</th>
                  <th className="py-2">Value</th>
                  <th className="py-2">Range</th>
                  <th className="py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {result.measurements.map((measurement) => (
                  <tr key={measurement.id} className="border-b border-slate-800">
                    <td className="py-2">{measurement.parameter_name}</td>
                    <td className="py-2">{measurement.measured_value ?? 'Invalid'} {measurement.unit}</td>
                    <td className="py-2">{measurement.lower_limit ?? '—'} to {measurement.upper_limit ?? '—'} {measurement.unit}</td>
                    <td className={statusColor(measurement.status)}>{measurement.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <div className="mt-5">
        <h3 className="mb-3 font-semibold">Test History</h3>
        {history.length === 0 ? (
          <p className="text-sm text-slate-400">No test executions yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                <tr>
                  <th className="py-2">Test</th>
                  <th className="py-2">Device</th>
                  <th className="py-2">Scenario</th>
                  <th className="py-2">Status</th>
                  <th className="py-2">Reports</th>
                </tr>
              </thead>
              <tbody>
                {history.map((test) => (
                  <tr key={test.id} className="border-b border-slate-800">
                    <td className="py-2 font-mono text-xs">{test.id}</td>
                    <td className="py-2">{test.device_part_number}</td>
                    <td className="py-2">{test.scenario}</td>
                    <td className={statusColor(test.overall_status)}>{test.overall_status}</td>
                    <td className="py-2">
                      <a className="mr-3 text-cyan-300" href={`${API_BASE_URL}/reports/${test.id}/pdf`}>PDF</a>
                      <a className="text-slate-300" href={`${API_BASE_URL}/reports/${test.id}/csv`}>CSV</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}

function statusColor(status: 'PASS' | 'FAIL' | 'REVIEW') {
  if (status === 'PASS') return 'font-semibold text-emerald-300'
  if (status === 'FAIL') return 'font-semibold text-red-300'
  return 'font-semibold text-amber-300'
}
