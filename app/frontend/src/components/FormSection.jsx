export default function FormSection({ title, description, number, children }) {
  return <fieldset className="section-card">
    <legend className="float-left mb-1 flex w-full items-center gap-3 text-base font-semibold text-slate-900">
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-100 text-xs font-semibold text-slate-500" aria-hidden="true">{String(number).padStart(2, '0')}</span>
      {title}
    </legend>
    <p className="clear-both mb-6 pl-10 text-sm text-slate-500">{description}</p>
    <div className="grid gap-x-5 gap-y-5 sm:grid-cols-2">{children}</div>
  </fieldset>
}
