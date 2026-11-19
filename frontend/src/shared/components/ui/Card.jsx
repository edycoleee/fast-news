export function Card({ as: Component = 'section', className = '', children, ...props }) {
  return (
    <Component className={`surface-card ${className}`} {...props}>
      {children}
    </Component>
  )
}
