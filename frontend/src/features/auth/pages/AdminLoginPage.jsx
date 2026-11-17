import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { loginSchema } from '../schemas/loginSchema'
import { login } from '../api/authApi'

export function AdminLoginPage() {
  const [formError, setFormError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const from = location.state?.from || '/admin/dashboard'

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      username_or_email: '',
      password: '',
    },
  })

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: async () => {
      setFormError('')
      await queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
      navigate(from, { replace: true })
    },
    onError: (error) => {
      setFormError(error?.response?.data?.detail || 'Login gagal. Periksa kredensial Anda.')
    },
  })

  const onSubmit = (values) => {
    const validation = loginSchema.safeParse(values)
    if (!validation.success) {
      setFormError(validation.error.issues[0]?.message || 'Input tidak valid.')
      return
    }
    loginMutation.mutate(validation.data)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Admin access</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Login NewsHub CMS</h1>
        <p className="mt-2 text-sm text-slate-600">Gunakan akun admin yang sudah terdaftar di backend.</p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="username_or_email">
              Username atau Email
            </label>
            <input
              id="username_or_email"
              data-testid="login-username-input"
              type="text"
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-primary"
              {...register('username_or_email', { required: 'Username/email wajib diisi.' })}
            />
            {errors.username_or_email && <p className="mt-1 text-xs text-danger">{errors.username_or_email.message}</p>}
          </div>

          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="block text-sm font-medium text-slate-700" htmlFor="password">
                Password
              </label>
              <button
                data-testid="toggle-password-visibility-button"
                type="button"
                className="text-xs font-medium text-primary hover:underline"
                onClick={() => setShowPassword((current) => !current)}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            <input
              id="password"
              data-testid="login-password-input"
              type={showPassword ? 'text' : 'password'}
              className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-primary"
              {...register('password', { required: 'Password wajib diisi.' })}
            />
            {errors.password && <p className="mt-1 text-xs text-danger">{errors.password.message}</p>}
          </div>

          {formError && (
            <div data-testid="login-error-message" className="rounded-xl border border-danger/20 bg-danger/10 px-3 py-2 text-sm text-danger">
              {formError}
            </div>
          )}

          <button
            data-testid="login-submit-button"
            type="submit"
            disabled={loginMutation.isPending}
            className="w-full rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="mt-5 text-sm text-slate-600">
          <Link className="font-medium text-primary hover:underline" to="/">
            Back to landing page
          </Link>
        </div>
      </div>
    </div>
  )
}
