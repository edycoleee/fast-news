import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { AdminSettingsPage } from './AdminSettingsPage'
import { listSettings, runRetentionCleanup, updateSettings } from '../api/settingsApi'

vi.mock('../api/settingsApi', () => ({
  listSettings: vi.fn(),
  updateSettings: vi.fn(),
  runRetentionCleanup: vi.fn(),
}))

test('loads settings and saves an updated runtime limit', async () => {
  const response = {
    items: [
      {
        key: 'upload.max_size_bytes',
        category: 'upload',
        label: 'Maksimum ukuran upload',
        value_type: 'integer',
        value: 5242880,
        minimum: 1024,
        maximum: 104857600,
        is_default: true,
      },
    ],
  }
  listSettings.mockResolvedValue(response)
  updateSettings.mockResolvedValue({
    ...response,
    items: [{ ...response.items[0], value: 10485760, is_default: false }],
  })
  const queryClient = new QueryClient()

  render(
    <QueryClientProvider client={queryClient}>
      <AdminSettingsPage />
    </QueryClientProvider>,
  )

  const input = await screen.findByTestId('setting-upload.max_size_bytes')
  fireEvent.change(input, { target: { value: '10' } })
  fireEvent.click(screen.getByTestId('settings-save-button'))

  await waitFor(() => expect(updateSettings).toHaveBeenCalled())
  expect(updateSettings.mock.calls[0][0]).toEqual([
    { key: 'upload.max_size_bytes', value: 10485760 },
  ])
})

test('runs manual retention cleanup dry-run', async () => {
  listSettings.mockResolvedValue({
    items: [
      {
        key: 'retention.audit_log_days',
        category: 'retention',
        label: 'Retention audit log',
        value_type: 'integer',
        value: 180,
        minimum: 30,
        maximum: 730,
        is_default: true,
      },
    ],
  })
  runRetentionCleanup.mockResolvedValue({
    dry_run: true,
    eligible: { audit_logs: 1, auth_sessions: 0, rate_limit_buckets: 2 },
    deleted: { audit_logs: 0, auth_sessions: 0, rate_limit_buckets: 0 },
    cutoff: {},
  })

  const queryClient = new QueryClient()
  render(
    <QueryClientProvider client={queryClient}>
      <AdminSettingsPage />
    </QueryClientProvider>,
  )

  fireEvent.click(await screen.findByTestId('retention-dry-run-button'))

  await waitFor(() => expect(runRetentionCleanup).toHaveBeenCalled())
  expect(runRetentionCleanup.mock.calls[0][0]).toEqual({ dry_run: true })
  expect(await screen.findByTestId('retention-cleanup-report')).toBeInTheDocument()
})
