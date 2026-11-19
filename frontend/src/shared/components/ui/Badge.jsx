const variants = {
  primary: 'bg-primary/10 text-primary ring-primary/20',
  success: 'bg-success/10 text-success ring-success/20',
  warning: 'bg-warning/15 text-amber-800 ring-warning/20',
  danger: 'bg-danger/10 text-danger ring-danger/20',
  neutral: 'bg-slate-100 text-slate-600 ring-slate-200',
}

export function Badge({ children, variant = 'neutral', className = '' }) {
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${
        variants[variant]
      } ${className}`}
    >
      {children}
    </span>
  )
}
