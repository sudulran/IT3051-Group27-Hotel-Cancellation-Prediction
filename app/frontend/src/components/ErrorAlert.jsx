import { useEffect, useRef } from 'react'
import { CircleAlert } from 'lucide-react'
import { fieldLabels } from '../data/bookingFields'

export default function ErrorAlert({ error }) {
  const alert = useRef(null)
  useEffect(() => { if (error) alert.current?.focus() }, [error])
  if (!error) return null
  return <div ref={alert} tabIndex={-1} role="alert" className="mb-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">
    <div className="flex items-start gap-3"><CircleAlert size={19} className="mt-0.5 shrink-0" aria-hidden="true" /><p className="font-semibold">{error.message}</p></div>
    {error.issues?.length > 0 && <ul className="mt-3 space-y-2 pl-8">{error.issues.map((issue, index) => <li key={index}>
      {issue.field ? <a className="font-medium underline underline-offset-2" href={`#${issue.field}`}>{fieldLabels[issue.field] || 'Booking field'}</a> : 'Booking details'}: {issue.message}
    </li>)}</ul>}
  </div>
}
