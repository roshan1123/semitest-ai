import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export type InspectionResult = {
  id: string
  device_id: string | null
  image_filename: string
  image_path: string
  inspection_type: string
  result: string
  confidence: number
  analysis_metadata: string
  human_review_status: string
  created_at: string
}

export async function analyzeImage(
  file: File,
  deviceId: string,
): Promise<InspectionResult> {
  const form = new FormData()
  form.append('image', file)
  if (deviceId) form.append('device_id', deviceId)
  const response = await axios.post<InspectionResult>(
    `${API_BASE_URL}/inspections/analyze`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return response.data
}
