import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { loginSchema } from '../schemas/loginSchema'
import { login } from '../api/authApi'
import { Globe2, ShieldCheck } from 'lucide-react'

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
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-10">
      <div className="w-full max-w-5xl overflow-hidden rounded-3xl border border-white/10 bg-white shadow-2xl lg:grid lg:grid-cols-[1.05fr_0.95fr]">
        <div className="hidden bg-secondary p-10 text-white lg:flex lg:flex-col lg:justify-between">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/15">
              <Globe2 className="h-5 w-5" />
            </span>
            <span className="text-lg font-bold">NewsHub CMS</span>
          </Link>
          <div>
            <ShieldCheck className="h-10 w-10 text-teal-300" />
            <h2 className="mt-5 max-w-sm text-3xl font-bold leading-tight">
              Editorial control dengan akses yang aman dan terukur.
            </h2>
            <p className="mt-4 max-w-sm text-sm leading-6 text-blue-100">
              Session aman, RBAC backend, audit trail, dan workflow editorial dalam satu workspace.
            </p>
          </div>
          <p className="text-xs text-blue-100/70">Secure newsroom administration</p>
        </div>
        <div className="p-7 sm:p-10">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">Admin access</p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-950">Masuk ke NewsHub</h1>
        <p className="mt-2 text-sm text-slate-600">Gunakan akun admin yang terdaftar untuk mengakses workspace.</p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="username_or_email">
              Username atau Email
            </label>
            <input
              id="username_or_email"
              data-testid="login-username-input"
              type="text"
              className="field-control"
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
              className="field-control"
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
            className="button-primary w-full"
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
    </div>
  )
}
