import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, vi } from 'vitest'
import { SignatureCanvas } from './SignatureCanvas'

const clear = vi.fn()

vi.mock('signature_pad', () => ({
  default: class SignaturePad {
    constructor() {
      this.clear = clear
    }

    isEmpty() {
      return true
    }

    toData() {
      return []
    }

    fromData() {}

    addEventListener() {}

    removeEventListener() {}

    off() {}
  },
}))

afterEach(() => {
  clear.mockClear()
})

test('renders drawing canvas and clear action', () => {
  render(<SignatureCanvas onChange={() => {}} />)

  expect(screen.getByTestId('signature-canvas')).toBeInTheDocument()
  fireEvent.click(screen.getByTestId('signature-clear-button'))
  expect(clear).toHaveBeenCalled()
})
