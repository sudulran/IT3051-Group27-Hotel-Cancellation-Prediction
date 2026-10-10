import { Building2, ArrowDownRight } from 'lucide-react'

export default function Header() {
  return <>
    <a className="skip-link" href="#booking-form">Skip to booking form</a>
    <header className="sticky top-0 z-50 border-b border-blue-950/20 bg-brand">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-2 px-5 py-5 sm:gap-4 sm:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand"><Building2 size={26} aria-hidden="true" /></span>
          <div><p className="text-base font-bold tracking-wide text-white">ENTROPY ZERO</p><p className="mt-0.5 text-xs text-blue-100">Hospitality decision support</p></div>
        </div>
        <a href="#booking-form" className="inline-flex min-h-11 shrink-0 items-center gap-1.5 rounded-full bg-brand-soft px-3 py-2.5 text-sm font-semibold text-brand shadow-sm hover:bg-white focus-visible:outline-white sm:gap-2 sm:px-4" aria-label="Start a prediction"><span className="sm:hidden">Predict</span><span className="hidden sm:inline">Start a prediction</span><ArrowDownRight size={16} aria-hidden="true" /></a>
      </div>
    </header>
  </>
}
