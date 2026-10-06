import { useEffect, useRef } from 'react'
import { ChartNoAxesCombined, CircleCheck, CircleAlert, RotateCcw, ShieldCheck } from 'lucide-react'
import LoadingState from './LoadingState'
import ProbabilityGauge from './ProbabilityGauge'

export default function PredictionResult({ result, loading, onReset }) {
  const heading = useRef(null)
  useEffect(() => { if (result) heading.current?.focus() }, [result])
  const OutcomeIcon = result?.prediction === 'Cancelled' ? CircleAlert : CircleCheck
  return <aside className="min-w-0 self-start lg:sticky lg:top-7" aria-label="Prediction result">
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5"><h2 className="font-semibold text-slate-900">Reservation outlook</h2><ChartNoAxesCombined size={19} className="text-slate-400" aria-hidden="true" /></div>
      <div className="p-6" aria-busy={loading}>
        {loading ? <LoadingState /> : result ? <div>
          <p className="eyebrow">Prediction result</p>
          <div className="mt-4 flex items-center gap-3"><OutcomeIcon className={result.prediction === 'Cancelled' ? 'text-amber-700' : 'text-teal-700'} size={26} aria-hidden="true" /><h3 ref={heading} tabIndex={-1} className="text-3xl font-semibold tracking-tight text-slate-900">{result.prediction}</h3></div>
          <ProbabilityGauge probability={result.cancellation_probability} />
          <p className="mt-6 border-t border-slate-100 pt-5 text-sm leading-6 text-slate-600">Use this estimate alongside your reservation records and operational judgment.</p>
        </div> : <div className="py-10 text-center">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full border border-blue-100 bg-blue-50/60"><ChartNoAxesCombined size={32} className="text-brand" strokeWidth={1.5} aria-hidden="true" /></div>
          <h3 className="text-lg font-semibold text-slate-900">A clearer view of your booking</h3>
          <p className="mx-auto mt-3 max-w-64 text-sm leading-6 text-slate-500">Complete the reservation details to see its estimated cancellation probability.</p>
        </div>}
        <button type="button" onClick={onReset} disabled={loading} className="secondary-button mt-7 w-full"><RotateCcw size={16} aria-hidden="true" />Clear / New Prediction</button>
      </div>
    </div>
    <div className="mt-5 flex gap-3 rounded-xl border border-teal-100 bg-teal-50/70 p-5"><ShieldCheck size={20} className="mt-0.5 shrink-0 text-teal-800" aria-hidden="true" /><div><h3 className="text-sm font-semibold text-teal-950">Support for informed decisions</h3><p className="mt-2 text-xs leading-5 text-teal-900">This prediction is decision-support information and should not be treated as certainty or used as the sole basis for decisions about a guest.</p></div></div>
  </aside>
}
