import { test, expect } from '@playwright/test'

const endpoint = '**/api/predict'
const result = {
  prediction: 'Cancelled', class: 1, cancellation_probability: 0.4,
  cancellation_probability_percent: 40, threshold: 0.33, model_name: 'XGBoost',
  message: 'Decision support only.',
}

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Average Daily Rate').fill('100')
})

test('sends business fields as JSON and displays the backend result', async ({ page }) => {
  let payload
  await page.route(endpoint, async (route) => {
    payload = route.request().postDataJSON()
    await route.fulfill({ json: result })
  })
  await page.getByLabel('Find a country').fill('Sri Lanka')
  await page.getByLabel('Country (optional)', { exact: true }).selectOption('LKA')
  await page.getByLabel('Children (optional)', { exact: true }).fill('')
  await page.getByLabel('Booking Through Agent?').selectOption('true')
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  await expect(page.getByRole('heading', { name: 'Cancelled', exact: true })).toBeFocused()
  await expect(page.getByRole('meter')).toHaveAttribute('aria-valuenow', '40')
  await expect(page.getByText('Estimated cancellation probability:')).toContainText('40.0%')
  expect(Object.keys(payload)).toHaveLength(23)
  expect(payload.adr).toBe(100)
  expect(payload.has_agent).toBe(true)
  expect(payload.has_company).toBe(false)
  expect(payload.country).toBe('LKA')
  expect(payload.children).toBeNull()
  expect(payload).not.toHaveProperty('total_guests')
  expect(payload).not.toHaveProperty('arrival_date_week_number')
  await page.getByLabel('Adults', { exact: true }).fill('3')
  await expect(page.getByRole('heading', { name: 'Cancelled', exact: true })).toHaveCount(0)
})

test('accepts negative ADR and zero guests/nights without inventing restrictions', async ({ page }) => {
  let payload
  await page.route(endpoint, async (route) => {
    payload = route.request().postDataJSON()
    await route.fulfill({ json: { ...result, prediction: 'Not Cancelled', class: 0, cancellation_probability: 0.12, cancellation_probability_percent: 12 } })
  })
  await page.getByLabel('Average Daily Rate').fill('-6.38')
  for (const label of ['Adults', 'Babies', 'Weekend Nights', 'Weekday Nights']) {
    await page.getByLabel(label, { exact: true }).fill('0')
  }
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  await expect(page.getByRole('heading', { name: 'Not Cancelled', exact: true })).toBeVisible()
  expect(payload.adr).toBe(-6.38)
  expect(payload.country).toBeNull()
  await page.getByRole('button', { name: 'Clear / New Prediction' }).click()
  await expect(page.getByLabel('Hotel Type')).toBeFocused()
  await expect(page.getByLabel('Average Daily Rate')).toHaveValue('')
  await expect(page.getByRole('heading', { name: 'Not Cancelled', exact: true })).toHaveCount(0)
})

test('blocks arrival before booking date', async ({ page }) => {
  let requests = 0
  await page.route(endpoint, (route) => { requests++; return route.fulfill({ json: result }) })
  await page.getByLabel('Booking Date', { exact: true }).fill('2026-10-06')
  await page.getByLabel('Arrival Date', { exact: true }).fill('2026-10-05')
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  expect(await page.getByLabel('Arrival Date', { exact: true }).evaluate((input) => input.validity.rangeUnderflow)).toBe(true)
  expect(requests).toBe(0)
})

test('disables submissions and editing while waiting', async ({ page }) => {
  let release
  const waiting = new Promise((resolve) => { release = resolve })
  await page.route(endpoint, async (route) => { await waiting; await route.fulfill({ json: result }) })
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  await expect(page.getByRole('button', { name: 'Calculating prediction…' })).toBeDisabled()
  await expect(page.getByLabel('Average Daily Rate')).toBeDisabled()
  await expect(page.getByText('Assessing your reservation')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Clear / New Prediction' })).toBeDisabled()
  release()
  await expect(page.getByRole('heading', { name: 'Cancelled', exact: true })).toBeVisible()
})

test('shows 422 errors at the matching field and in an accessible alert', async ({ page }) => {
  await page.route(endpoint, (route) => route.fulfill({ status: 422, json: {
    detail: [{ loc: ['body', 'adr'], msg: 'Input should be a finite number', type: 'finite_number' }],
  } }))
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  await expect(page.getByRole('alert')).toBeFocused()
  await expect(page.getByRole('alert')).toContainText('Average Daily Rate')
  await expect(page.getByLabel('Average Daily Rate')).toHaveAttribute('aria-invalid', 'true')
})

test('handles server and network failures without exposing details', async ({ page }) => {
  await page.route(endpoint, (route) => route.fulfill({ status: 500, json: { detail: 'private/server/path traceback' } }))
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  await expect(page.getByRole('alert')).toContainText('temporarily unavailable')
  await expect(page.getByRole('alert')).not.toContainText('traceback')
  await page.unroute(endpoint)
  await page.route(endpoint, (route) => route.abort('failed'))
  await page.getByRole('button', { name: 'Predict Cancellation Risk' }).click()
  await expect(page.getByRole('alert')).toContainText('Unable to connect')
})

test('all inputs have labels and desktop/mobile layouts avoid horizontal overflow', async ({ page }, testInfo) => {
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport)
    expect(await page.locator('input, select').evaluateAll((inputs) => inputs.every((input) => input.labels.length > 0))).toBe(true)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
    await page.screenshot({ path: testInfo.outputPath(`booking-${viewport.width}.png`), fullPage: true })
  }
})
