import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { createProfile, listProfiles, updateProfile } from '../services/profiles'
import type { TestProfile } from '../types/profile'

export function Profiles() {
  const [profiles, setProfiles] = useState<TestProfile[]>([])
  const [deviceType, setDeviceType] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState('')
  const [profileType, setProfileType] = useState<'MOSFET' | 'Diode'>('MOSFET')
  const [description, setDescription] = useState('')

  const loadProfiles = async () => {
    setLoading(true)
    setError('')
    try {
      setProfiles(await listProfiles(deviceType))
    } catch {
      setError('Unable to load test profiles from the backend.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfiles()
  }, [deviceType])

  const toggleActive = async (profile: TestProfile) => {
    setError('')
    setNotice('')
    try {
      await updateProfile(profile.id, { is_active: !profile.is_active })
      setNotice(`${profile.name} updated to version ${profile.version + 1}.`)
      await loadProfiles()
    } catch {
      setError('Unable to update the test profile.')
    }
  }

  const submitProfile = async (event: FormEvent) => {
      event.preventDefault()
      setError('')
      setNotice('')
      try {
        await createProfile({
          name,
          device_type: profileType,
          description,
          is_active: true,
          created_by: 'Administrator',
          parameters: [
            {
              parameter_name: profileType === 'MOSFET' ? 'VGS Threshold' : 'Forward Voltage',
              unit: profileType === 'MOSFET' ? 'V' : 'V',
              lower_limit: null,
              upper_limit: null,
              nominal_value: null,
              tolerance: null,
              required: true,
              evaluation_method: 'RANGE',
            },
          ],
        })
        setName('')
        setDescription('')
        setShowCreate(false)
        setNotice('Test profile created. Configure limits before execution.')
        await loadProfiles()
      } catch (error: unknown) {
        setError(
          typeof error === 'object' && error !== null && 'response' in error
            ? 'Unable to create the test profile. Check the required fields and limits.'
            : 'Unable to create the test profile.',
        )
      }
  }

  return (
    <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">Phase 2</p>
          <h2 className="text-xl font-semibold">Test Profiles</h2>
        </div>
        <button
          type="button"
          onClick={() => setShowCreate((current) => !current)}
          className="rounded-md bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950"
        >
          {showCreate ? 'Cancel' : 'Create Profile'}
        </button>
      </div>

      {showCreate && (
        <form onSubmit={submitProfile} className="mb-5 grid gap-3 rounded-lg border border-slate-800 p-4 sm:grid-cols-3">
          <label className="text-sm">
            Profile name *
            <input required value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="text-sm">
            Device type *
            <select value={profileType} onChange={(event) => setProfileType(event.target.value as 'MOSFET' | 'Diode')}>
              <option value="MOSFET">MOSFET</option>
              <option value="Diode">Diode</option>
            </select>
          </label>
          <label className="text-sm">
            Description
            <input value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
          <button type="submit" className="rounded-md border border-cyan-400 px-3 py-2 text-sm font-semibold text-cyan-300 sm:col-start-3">
            Save Profile
          </button>
        </form>
      )}
      <div className="mb-4 flex justify-end">
        <select
          aria-label="Filter profiles by device type"
          className="max-w-48"
          value={deviceType}
          onChange={(event) => setDeviceType(event.target.value)}
        >
          <option value="">All types</option>
          <option value="MOSFET">MOSFET</option>
          <option value="Diode">Diode</option>
        </select>
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

      {loading ? (
        <p className="py-6 text-center text-slate-400">Loading profiles...</p>
      ) : profiles.length === 0 ? (
        <p className="py-6 text-center text-slate-400">No test profiles match this view.</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {profiles.map((profile) => (
            <article key={profile.id} className="rounded-lg border border-slate-800 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold">{profile.name}</h3>
                  <p className="mt-1 text-sm text-slate-400">
                    {profile.device_type} · Version {profile.version}
                  </p>
                </div>
                <span className={profile.is_active ? 'text-emerald-300' : 'text-slate-400'}>
                  {profile.is_active ? 'Active' : 'Disabled'}
                </span>
              </div>
              <p className="mt-3 text-sm text-slate-300">{profile.description}</p>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-slate-700 text-xs uppercase text-slate-400">
                    <tr>
                      <th className="py-2">Measurement</th>
                      <th className="py-2">Unit</th>
                      <th className="py-2">Limits</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profile.parameters.map((parameter) => (
                      <tr key={parameter.id} className="border-b border-slate-800">
                        <td className="py-2 pr-3">{parameter.parameter_name}</td>
                        <td className="py-2 pr-3">{parameter.unit}</td>
                        <td className="py-2">
                          {parameter.lower_limit ?? '—'} to {parameter.upper_limit ?? '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <button
                type="button"
                onClick={() => toggleActive(profile)}
                className="mt-4 text-sm font-semibold text-cyan-300 hover:text-cyan-200"
              >
                {profile.is_active ? 'Disable profile' : 'Enable profile'}
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
