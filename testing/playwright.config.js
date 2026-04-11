import { defineConfig } from '@playwright/test';
import path from 'node:path';

const baseURL = process.env.E2E_BASE_URL || 'http://127.0.0.1:5173';

export default defineConfig({
  testDir: '.',
  testMatch: ['test_e2e.spec.js'],
  timeout: 60_000,
  use: {
    baseURL,
    headless: true,
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 5173',
    cwd: path.resolve(process.cwd(), 'frontend'),
    url: baseURL,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
