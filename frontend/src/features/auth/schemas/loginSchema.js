import { z } from 'zod'

export const loginSchema = z.object({
  username_or_email: z
    .string()
    .min(3, 'Username/email minimal 3 karakter')
    .max(255, 'Username/email terlalu panjang'),
  password: z
    .string()
    .min(8, 'Password minimal 8 karakter')
    .max(255, 'Password terlalu panjang'),
})
