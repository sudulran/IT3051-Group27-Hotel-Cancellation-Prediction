export default function FormField({ field, value, onChange, error, bookingDate }) {
  const { name, label, type, options, hint, optional, min, step } = field
  const props = {
    id: name, name, value, onChange: (event) => onChange(name, event.target.value),
    required: !optional, className: `form-control ${error ? 'input-error' : ''}`,
    'aria-invalid': !!error,
    'aria-describedby': [hint && `${name}-hint`, error && `${name}-error`].filter(Boolean).join(' ') || undefined,
  }
  return <div className="min-w-0">
    <label className="field-label" htmlFor={name}>{label}{optional && <> <span className="font-normal text-slate-500">(optional)</span></>}</label>
    {type === 'select'
      ? <select {...props}>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select>
      : <input {...props} type={type} min={name === 'arrival_date' ? bookingDate : min} step={step} />}
    {hint && <p className="field-hint" id={`${name}-hint`}>{hint}</p>}
    {error && <p className="field-error" id={`${name}-error`}>{error}</p>}
  </div>
}
