import { readFileSync } from 'node:fs'
import { test, expect } from '@playwright/test'
import { fields } from '../../src/data/bookingFields.js'

const metadata = JSON.parse(readFileSync(new URL('../../../../models/final_model_metadata.json', import.meta.url), 'utf8'))

test('frontend fields and categories match the live Pydantic schema', async ({ request }) => {
  const response = await request.get('http://127.0.0.1:8000/openapi.json')
  expect(response.ok()).toBe(true)
  const schema = (await response.json()).components.schemas.PredictionRequest
  expect(fields.map((field) => field.name).sort()).toEqual(Object.keys(schema.properties).sort())
  expect(schema.additionalProperties).toBe(false)
  for (const field of fields) {
    if (schema.properties[field.name].enum) {
      expect(field.options.map((option) => option.value).sort()).toEqual(schema.properties[field.name].enum.slice().sort())
    }
  }
})

for (const width of [1440, 390]) {
  test(`real saved-model predictions and reset at ${width}px`, async ({ page }, testInfo) => {
    const errors = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.getByLabel('Booking Date', { exact: true }).fill('2016-12-20')
    await page.getByLabel('Arrival Date', { exact: true }).fill('2017-01-08')
    await page.getByLabel('Children (optional)', { exact: true }).fill('')
    for (const values of [
      { adr: '100', adults: '2', nights: '3' },
      { adr: '-6.38', adults: '0', nights: '0' },
      { adr: '10000', adults: '100', nights: '3' },
    ]) {
      await page.getByLabel('Average Daily Rate').fill(values.adr)
      await page.getByLabel('Adults', { exact: true }).fill(values.adults)
      await page.getByLabel('Weekday Nights', { exact: true }).fill(values.nights)
      const [response] = await Promise.all([
        page.waitForResponse((response) => response.url().endsWith('/api/predict')),
        page.getByRole('button', { name: 'Predict Cancellation Risk' }).click(),
      ])
      expect(response.status()).toBe(200)
      expect(response.headers()['access-control-allow-origin']).toBe('http://127.0.0.1:5173')
      const payload = response.request().postDataJSON()
      expect(Object.keys(payload).sort()).toEqual(fields.map((field) => field.name).sort())
      expect(payload.adr).toBe(Number(values.adr))
      expect(payload.children).toBeNull()
      expect(payload.country).toBeNull()
      const result = await response.json()
      expect(result.threshold).toBe(metadata.probability_threshold)
      expect(result.class).toBe(Number(result.cancellation_probability >= metadata.probability_threshold))
      expect(result.prediction).toBe(metadata.class_labels[String(result.class)])
      await expect(page.getByRole('heading', { name: result.prediction, exact: true })).toBeFocused()
      await expect(page.getByRole('meter')).toHaveAttribute('aria-valuetext', `${(result.cancellation_probability * 100).toFixed(1)} percent`)
      await expect(page.getByText('Estimated cancellation probability:')).toContainText(`${result.cancellation_probability_percent.toFixed(1)}%`)
      await expect(page.getByText('This prediction is decision-support information', { exact: false })).toBeVisible()
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    }
    await page.screenshot({ path: testInfo.outputPath(`live-result-${width}.png`), fullPage: true })
    await page.getByRole('button', { name: 'Clear / New Prediction' }).click()
    await expect(page.getByLabel('Hotel Type')).toBeFocused()
    await expect(page.getByRole('meter')).toHaveCount(0)
    await expect(page.getByLabel('Average Daily Rate')).toHaveValue('')
    expect(errors).toEqual([])
  })
}
