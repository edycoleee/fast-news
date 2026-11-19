import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { RolePermissionPicker } from './RolePermissionPicker'

const permissions = [
  { id: 1, name: 'news.manage', resource: 'news', action: 'manage' },
  { id: 2, name: 'comment.read', resource: 'comment', action: 'read' },
  { id: 3, name: 'comment.moderate', resource: 'comment', action: 'moderate' },
]

test('filters and saves multiple permission selections', () => {
  const onSave = vi.fn()
  render(
    <RolePermissionPicker
      roleName="editor"
      permissions={permissions}
      selectedIds={[1]}
      isSaving={false}
      onSave={onSave}
      onClose={() => {}}
    />,
  )

  fireEvent.change(screen.getByTestId('permission-picker-search'), {
    target: { value: 'comment' },
  })
  expect(screen.queryByText('news.manage')).not.toBeInTheDocument()
  fireEvent.click(screen.getByText('comment.read'))
  fireEvent.click(screen.getByText('comment.moderate'))
  fireEvent.click(screen.getByTestId('permission-picker-save'))

  expect(onSave).toHaveBeenCalledWith([1, 2, 3])
})
