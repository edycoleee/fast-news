export function parseApiDateTime(value) {
  if (!value) {
    return null
  }
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
  const date = new Date(hasTimezone ? value : `${value}Z`)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatLocalDateTime(
  value,
  {
    locale = 'id-ID',
    fallback = '-',
    dateStyle = 'medium',
    timeStyle = 'short',
  } = {},
) {
  const date = parseApiDateTime(value)
  return date
    ? new Intl.DateTimeFormat(locale, { dateStyle, timeStyle }).format(date)
    : fallback
}
