import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'

import { listDevices } from '../services/devices'
import { analyzeImage, type InspectionResult } from '../services/inspections'
import type { Device } from '../types/device'

export function ImageInspection() {
  const [devices, setDevices] = useState<Device[]>([])
  const [deviceId, setDeviceId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState('')
  const [result, setResult] = useState<InspectionResult | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    listDevices('', '').then(setDevices).catch(() => setError('Unable to load devices.'))
  }, [])

  useEffect(() => {
    if (!file) {
      setPreview('')
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const onFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setResult(null)
    setError('')
    setFile(event.target.files?.[0] ?? null)
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!file) {
      setError('Select a JPEG or PNG image.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      setResult(await analyzeImage(file, deviceId))
    } catch (error: unknown) {
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const response = (error as { response?: { data?: { detail?: string } } }).response
        setError(response?.data?.detail ?? 'Unable to analyze the image.')
      } else {
        setError('Unable to analyze the image.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mt-8 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <p className="text-sm text-slate-400">Phase 7</p>
      <h2 className="text-xl font-semibold">Image Inspection Demonstration</h2>
      <p className="mt-2 text-sm text-amber-300">
        Experimental computer-vision predictions only. Human review is required; no result is validated semiconductor defect detection.
      </p>

      {error && (
        <p role="alert" className="mt-4 rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-red-200">
          {error}
        </p>
      )}

      <form onSubmit={submit} className="mt-4 grid gap-4 md:grid-cols-[1fr_220px]">
        <div>
          <label className="block text-sm">
            Inspection image (JPEG or PNG, maximum 5 MB)
            <input type="file" accept="image/jpeg,image/png" onChange={onFileChange} />
          </label>
          {preview && (
            <img src={preview} alt="Selected inspection preview" className="mt-3 max-h-80 rounded-lg border border-slate-800" />
          )}
        </div>
        <div>
          <label className="block text-sm">
            Device (optional)
            <select value={deviceId} onChange={(event) => setDeviceId(event.target.value)}>
              <option value="">No device selected</option>
              {devices.map((device) => (
                <option key={device.id} value={device.id}>{device.part_number}</option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            disabled={loading}
            className="mt-4 w-full rounded-md bg-cyan-500 px-3 py-2 font-semibold text-slate-950 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </div>
      </form>

      {result && (
        <div className="mt-5 rounded-lg border border-slate-800 p-4">
          <p className="text-sm text-slate-400">Inspection {result.id}</p>
          <h3 className="mt-1 font-semibold text-amber-300">{result.result}</h3>
          <dl className="mt-3 grid gap-3 sm:grid-cols-3">
            <div><dt className="text-sm text-slate-400">Confidence</dt><dd>{result.confidence}</dd></div>
            <div><dt className="text-sm text-slate-400">Review status</dt><dd>{result.human_review_status}</dd></div>
            <div><dt className="text-sm text-slate-400">Inspection type</dt><dd>{result.inspection_type}</dd></div>
          </dl>
        </div>
      )}
    </section>
  )
}
