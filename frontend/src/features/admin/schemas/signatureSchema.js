import { z } from 'zod'

export const signatureSchema = z.object({
  purpose: z.string().trim().min(3, 'Tujuan approval minimal 3 karakter.').max(500),
  news_id: z.number().int().positive().nullable(),
  signature_data_url: z
    .string()
    .startsWith('data:image/png;base64,', 'Tanda tangan harus berupa PNG.'),
})
