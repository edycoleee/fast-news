import { publicCommentSchema } from './commentSchema'

test('accepts a valid public comment', () => {
  const result = publicCommentSchema.safeParse({
    author_name: 'Pembaca',
    content: 'Artikel ini sangat membantu.',
    parent_id: null,
  })

  expect(result.success).toBe(true)
})

test('rejects empty and oversized public comments', () => {
  const emptyResult = publicCommentSchema.safeParse({
    author_name: 'P',
    content: 'x',
    parent_id: null,
  })
  const oversizedResult = publicCommentSchema.safeParse({
    author_name: 'Pembaca',
    content: 'x'.repeat(2001),
    parent_id: null,
  })

  expect(emptyResult.success).toBe(false)
  expect(oversizedResult.success).toBe(false)
})
