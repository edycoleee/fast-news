import { useQuery } from '@tanstack/react-query'
import { getMe } from '../api/authApi'

export function useAuthMe() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: getMe,
    retry: false,
  })
}
