import { Building2, ArrowUpRight } from 'lucide-react'

export default function Header() {
  return <>
    <a className="skip-link" href="#booking-form">Skip to booking form</a>
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-5 sm:px-8">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand text-white"><Building2 size={23} aria-hidden="true" /></span>
          <div><p className="text-sm font-bold tracking-wide text-slate-900">ENTROPY ZERO</p><p className="mt-0.5 text-xs text-slate-500">Hospitality decision support</p></div>
        </div>
        <span className="hidden items-center gap-2 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 sm:flex">IT3051 · Group 27 <ArrowUpRight size={14} aria-hidden="true" /></span>
      </div>
    </header>
  </>
}
