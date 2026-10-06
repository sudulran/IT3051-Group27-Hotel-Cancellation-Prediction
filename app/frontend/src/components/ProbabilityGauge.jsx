export default function ProbabilityGauge({ probability }) {
  const percent = probability * 100
  return <div className="mt-7">
    <p className="text-sm leading-6 text-slate-600">Estimated cancellation probability: <strong className="text-slate-900">{percent.toFixed(1)}%</strong></p>
    <div role="meter" aria-label="Estimated cancellation probability" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent} aria-valuetext={`${percent.toFixed(1)} percent`} className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
      <div className="h-full rounded-full bg-brand" style={{ width: `${percent}%` }} />
    </div>
    <div className="mt-2 flex justify-between text-xs tabular-nums text-slate-500" aria-hidden="true"><span>0%</span><span>100%</span></div>
  </div>
}
