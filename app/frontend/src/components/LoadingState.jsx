import { Hourglass } from 'lucide-react'

export default function LoadingState() {
  return <div role="status" className="py-14 text-center">
    <span className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-brand"><Hourglass size={26} aria-hidden="true" /></span>
    <p className="font-semibold text-slate-800">Assessing your reservation</p>
    <p className="mt-2 text-sm text-slate-500">Your cancellation estimate will appear here.</p>
  </div>
}
