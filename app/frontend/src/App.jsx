import { useState } from 'react'
import Header from './components/Header'
import BookingForm from './components/BookingForm'
import PredictionResult from './components/PredictionResult'
import usePrediction from './hooks/usePrediction'
import { initialBooking } from './data/bookingFields'

export default function App() {
  const [values, setValues] = useState(initialBooking)
  const [formVersion, setFormVersion] = useState(0)
  const prediction = usePrediction()
  function change(name, value) {
    setValues((current) => ({ ...current, [name]: value }))
    prediction.clear() // An edited booking must never display a stale prediction.
  }
  function reset() {
    setValues(initialBooking()); setFormVersion((version) => version + 1); prediction.clear()
    requestAnimationFrame(() => document.getElementById('hotel')?.focus())
  }
  return <>
    <Header />
    <main className="mx-auto max-w-7xl px-5 pb-12 pt-10 sm:px-8 sm:pt-12">
      <div className="mb-9 max-w-3xl"><p className="eyebrow mb-3">Reservation intelligence</p><h1 className="text-3xl font-semibold leading-tight tracking-tight text-slate-900 sm:text-4xl">Hotel Cancellation Risk Predictor</h1><p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">Estimate the likelihood that a reservation may be cancelled using booking information available at reservation time.</p></div>
      <div className="grid items-start gap-7 lg:grid-cols-[minmax(0,1fr)_360px] xl:grid-cols-[minmax(0,1fr)_390px]">
        <BookingForm key={formVersion} values={values} onChange={change} onSubmit={prediction.submit} loading={prediction.loading} error={prediction.error} />
        <PredictionResult result={prediction.result} loading={prediction.loading} onReset={reset} />
      </div>
      <footer className="mt-10 flex flex-wrap justify-between gap-2 border-t border-slate-200 pt-6 text-xs leading-5 text-slate-500"><span>IT3051 · Fundamentals of Data Mining</span><span>Group 27 — Entropy Zero</span></footer>
    </main>
  </>
}
