import { formatLocalDateTime, parseApiDateTime } from './dateTime'

test('treats timezone-less API timestamps as UTC', () => {
  const date = parseApiDateTime('2026-11-18T02:26:28')

  expect(date.toISOString()).toBe('2026-11-18T02:26:28.000Z')
})

test('formats valid timestamps and handles invalid values', () => {
  expect(formatLocalDateTime('2026-11-18T02:26:28Z', { locale: 'en-US' })).not.toBe('-')
  expect(formatLocalDateTime('not-a-date')).toBe('-')
})
