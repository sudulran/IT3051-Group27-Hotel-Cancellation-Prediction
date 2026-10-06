import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { defineConfig } from '@playwright/test'

const virtualenvPython = fileURLToPath(new URL(
  process.platform === 'win32' ? '../../.venv/Scripts/python.exe' : '../../.venv/bin/python',
  import.meta.url,
))
const python = process.env.PYTHON_EXECUTABLE || (existsSync(virtualenvPython) ? virtualenvPython : 'python')

export default defineConfig({
  testDir: './tests/integration',
  workers: 1,
  use: { baseURL: 'http://127.0.0.1:5173', browserName: 'chromium', trace: 'retain-on-failure' },
  webServer: [
    {
      command: `"${python}" -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 8000`,
      url: 'http://127.0.0.1:8000/api/health',
      reuseExistingServer: false,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      url: 'http://127.0.0.1:5173',
      env: { VITE_API_BASE_URL: 'http://127.0.0.1:8000' },
      reuseExistingServer: false,
    },
  ],
})
