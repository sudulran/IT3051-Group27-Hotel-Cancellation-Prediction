import { useState } from 'react'
import { ArrowRight, LockKeyhole } from 'lucide-react'
import { bookingPayload, sections } from '../data/bookingFields'
import FormSection from './FormSection'
import FormField from './FormField'
import CountrySelect from './CountrySelect'
import ErrorAlert from './ErrorAlert'

export default function BookingForm({ values, onChange, onSubmit, loading, error }) {
  const [dateError, setDateError] = useState('')
  const errors = Object.fromEntries((error?.issues || []).filter((issue) => issue.field).map((issue) => [issue.field, issue.message]))
  function change(name, value) { setDateError(''); onChange(name, value) }
  function submit(event) {
    event.preventDefault()
    if (loading) return
    if (values.arrival_date < values.booking_date) {
      setDateError('Arrival date must be on or after the booking date.')
      document.getElementById('arrival_date')?.focus()
      return
    }
    onSubmit(bookingPayload(values))
  }
  return <form id="booking-form" onSubmit={submit} aria-label="Booking information" aria-busy={loading}>
    <ErrorAlert error={error} />
    <fieldset disabled={loading} className="min-w-0 space-y-5">
      <legend className="sr-only">Reservation information</legend>
      {sections.map((section, index) => <FormSection key={section.title} title={section.title} description={section.description} number={index + 1}>
        {section.fields.map((field) => field.type === 'country'
          ? <CountrySelect key={field.name} value={values.country} onChange={change} error={errors.country} />
          : <FormField key={field.name} field={field} value={values[field.name]} onChange={change} error={field.name === 'arrival_date' ? dateError || errors.arrival_date : errors[field.name]} bookingDate={values.booking_date} />)}
      </FormSection>)}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6">
        <button type="submit" className="primary-button w-full" disabled={loading}>{loading ? 'Calculating prediction…' : 'Predict Cancellation Risk'}<ArrowRight size={18} aria-hidden="true" /></button>
        <p className="mt-3 flex items-center justify-center gap-2 text-center text-xs leading-5 text-slate-500"><LockKeyhole size={13} className="shrink-0" aria-hidden="true" />Use information available when the reservation was created.</p>
      </div>
    </fieldset>
  </form>
}
