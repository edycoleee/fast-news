import { z } from 'zod'

export const publicCommentSchema = z.object({
  author_name: z.string().trim().min(2, 'Nama minimal 2 karakter.').max(80, 'Nama maksimal 80 karakter.'),
  content: z.string().trim().min(3, 'Komentar minimal 3 karakter.').max(2000, 'Komentar maksimal 2000 karakter.'),
  parent_id: z.number().int().positive().nullable(),
})
