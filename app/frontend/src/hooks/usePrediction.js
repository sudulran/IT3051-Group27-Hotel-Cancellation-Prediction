import { useRef, useState } from 'react'
import { predictCancellation } from '../api/predictionApi'

export default function usePrediction() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const inFlight = useRef(false)

  async function submit(payload) {
    if (inFlight.current) return
    inFlight.current = true
    setLoading(true)
    setResult(null)
    setError(null)
    try { setResult(await predictCancellation(payload)) }
    catch (failure) { setError(failure) }
    finally { inFlight.current = false; setLoading(false) }
  }

  function clear() { setResult(null); setError(null) }
  return { result, error, loading, submit, clear }
}
