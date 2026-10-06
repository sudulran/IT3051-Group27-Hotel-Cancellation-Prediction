import { useState } from 'react'
import countries from 'i18n-iso-countries'
import english from 'i18n-iso-countries/langs/en.json'

countries.registerLocale(english)
const countryOptions = Object.entries(countries.getNames('en', { select: 'official' }))
  .map(([alpha2, label]) => ({ value: countries.alpha2ToAlpha3(alpha2), label }))
  .sort((a, b) => a.label.localeCompare(b.label))

export default function CountrySelect({ value, onChange, error }) {
  const [search, setSearch] = useState('')
  const filtered = countryOptions.filter((country) => country.value === value
    || `${country.label} ${country.value}`.toLowerCase().includes(search.trim().toLowerCase()))
  return <div className="min-w-0 sm:col-span-2">
    <div className="grid gap-3 sm:grid-cols-2">
      <div>
        <label className="field-label" htmlFor="country-search">Find a country</label>
        <input className="form-control" id="country-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name or code" aria-controls="country" />
      </div>
      <div>
        <label className="field-label" htmlFor="country">Country <span className="font-normal text-slate-500">(optional)</span></label>
        <select className={`form-control ${error ? 'input-error' : ''}`} id="country" name="country" value={value} onChange={(event) => onChange('country', event.target.value)} aria-invalid={!!error} aria-describedby={error ? 'country-error' : 'country-hint'}>
          <option value="">Unknown / not provided</option>
          {filtered.map((country) => <option key={country.value} value={country.value}>{country.label} ({country.value})</option>)}
        </select>
      </div>
    </div>
    <p className="field-hint" id="country-hint">Search, then choose the guest’s country. Leave unknown if unavailable.</p>
    <span className="sr-only" role="status">{filtered.length} countries available</span>
    {error && <p className="field-error" id="country-error">{error}</p>}
  </div>
}
