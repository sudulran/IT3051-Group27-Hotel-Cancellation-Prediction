const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

export class ApiError extends Error {
  constructor(message, issues = []) {
    super(message)
    this.name = 'ApiError'
    this.issues = issues
  }
}

export async function predictCancellation(payload) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 30000)
  try {
    const response = await fetch(`${API_BASE_URL}/api/predict`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload), signal: controller.signal,
    })
    const body = await response.json().catch(() => null)
    if (response.status === 422) {
      const issues = Array.isArray(body?.detail) ? body.detail.map((issue) => ({
        field: issue.loc?.find((part) => Object.hasOwn(payload, part)),
        message: typeof issue.msg === 'string' ? issue.msg : 'Please check this value.',
      })) : []
      throw new ApiError('Please review the booking details highlighted below.', issues)
    }
    if (!response.ok) {
      throw new ApiError(response.status >= 500
        ? 'The prediction service is temporarily unavailable. Please try again shortly.'
        : 'The request could not be completed. Please check your details and try again.')
    }
    if (!['Cancelled', 'Not Cancelled'].includes(body?.prediction)
        || !Number.isFinite(body?.cancellation_probability)
        || body.cancellation_probability < 0 || body.cancellation_probability > 1) {
      throw new ApiError('The prediction service returned an unexpected result. Please try again.')
    }
    return body
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError(error.name === 'AbortError'
      ? 'The prediction is taking longer than expected. Please try again.'
      : 'Unable to connect to the prediction service. Check that the backend is running and your connection is available, then try again.')
  } finally {
    clearTimeout(timeout)
  }
}
