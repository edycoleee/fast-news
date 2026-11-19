import { useEffect, useRef } from 'react'
import SignaturePad from 'signature_pad'

export function SignatureCanvas({ onChange }) {
  const canvasRef = useRef(null)
  const signaturePadRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) {
      return undefined
    }

    const signaturePad = new SignaturePad(canvas, {
      backgroundColor: 'rgb(255, 255, 255)',
      penColor: 'rgb(15, 23, 42)',
    })
    signaturePadRef.current = signaturePad
    const updateValue = () => {
      onChange(signaturePad.isEmpty() ? '' : signaturePad.toDataURL('image/png'))
    }
    signaturePad.addEventListener('endStroke', updateValue)

    const resizeCanvas = () => {
      const data = signaturePad.isEmpty() ? [] : signaturePad.toData()
      canvas.width = Math.max(canvas.offsetWidth, 600)
      canvas.height = 240
      signaturePad.clear()
      if (data.length) {
        signaturePad.fromData(data)
      }
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      signaturePad.removeEventListener('endStroke', updateValue)
      signaturePad.off()
      signaturePadRef.current = null
    }
  }, [onChange])

  const clear = () => {
    signaturePadRef.current?.clear()
    onChange('')
  }

  return (
    <div>
      <canvas
        ref={canvasRef}
        data-testid="signature-canvas"
        className="w-full touch-none rounded-lg border border-slate-300 bg-white"
        style={{ height: 240 }}
        aria-label="Area tanda tangan"
      />
      <button
        data-testid="signature-clear-button"
        type="button"
        onClick={clear}
        className="mt-3 rounded-lg border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
      >
        Hapus tanda tangan
      </button>
    </div>
  )
}
