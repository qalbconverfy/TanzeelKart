'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import {
  ShoppingBag, Phone, Lock,
  Mail, Eye, EyeOff,
  ArrowRight, Loader2,
  UserX
} from 'lucide-react'
import { authAPI, setTokens } from '@/lib/api'
import { useAuthStore } from '@/lib/store'


// Schemas
const phoneSchema = z.object({
  phone: z
    .string()
    .min(10, '10 digits chahiye')
    .max(10, '10 digits chahiye')
    .regex(/^[6-9]\d{9}$/, 'Valid Indian number daalo'),
})

const otpSchema = z.object({
  otp: z
    .string()
    .length(6, 'OTP 6 digits ka hona chahiye')
    .regex(/^\d{6}$/, 'Sirf numbers daalo'),
})

const emailSchema = z.object({
  email: z.string().email('Valid email daalo'),
  password: z.string().min(6, 'Password 6+ characters'),
})


export default function LoginPage() {
  const router = useRouter()
  const { setUser } = useAuthStore()

  const [loginType, setLoginType] = useState('phone')
  const [step, setStep] = useState('input')
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendTimer, setResendTimer] = useState(0)
  const [showPassword, setShowPassword] = useState(false)

  const phoneForm = useForm({
    resolver: zodResolver(phoneSchema),
  })

  const otpForm = useForm({
    resolver: zodResolver(otpSchema),
  })

  const emailForm = useForm({
    resolver: zodResolver(emailSchema),
  })

  // Timer
  const startTimer = () => {
    setResendTimer(30)
    const interval = setInterval(() => {
      setResendTimer((prev) => {
        if (prev <= 1) { clearInterval(interval); return 0 }
        return prev - 1
      })
    }, 1000)
  }

  // Handle success — token save + redirect
  const handleSuccess = (data) => {
    setTokens(data.access_token, data.refresh_token)
    setUser({
      id: data.user_id,
      phone: phone || '',
      role: data.role,
      account_type: data.account_type,
      is_guest: data.is_guest || false,
    })
    toast.success('Login ho gaya! 🎉')
    if (data.is_new_user || !data.account_type || data.account_type === 'skip') {
      router.push('/select-account-type')
    } else {
      router.push('/home')
    }
  }

  // Phone — Send OTP
  const onSendOTP = async (data) => {
    setLoading(true)
    try {
      await authAPI.sendOTP(data.phone)
      setPhone(data.phone)
      setStep('otp')
      startTimer()
      toast.success('OTP bheja gaya!')
    } catch (err) {
      toast.error(err.response?.data?.message || 'OTP nahi gaya')
    } finally {
      setLoading(false)
    }
  }

  // Phone — Verify OTP
  const onVerifyOTP = async (data) => {
    setLoading(true)
    try {
      const res = await authAPI.verifyOTP(phone, data.otp)
      handleSuccess(res.data)
    } catch (err) {
      toast.error(err.response?.data?.message || 'OTP galat hai')
    } finally {
      setLoading(false)
    }
  }

  // Resend OTP
  const handleResend = async () => {
    if (resendTimer > 0) return
    setLoading(true)
    try {
      await authAPI.sendOTP(phone)
      startTimer()
      toast.success('OTP dobara bheja!')
    } catch (err) {
      toast.error('OTP nahi gaya')
    } finally {
      setLoading(false)
    }
  }

  // Email Login
  const onEmailLogin = async (data) => {
    setLoading(true)
    try {
      const res = await authAPI.emailLogin(data)
      handleSuccess(res.data)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  // Guest Login
  const onGuestLogin = async () => {
    setLoading(true)
    try {
      const res = await authAPI.guestLogin()
      handleSuccess({ ...res.data, is_new_user: false })
      router.push('/home')
    } catch (err) {
      toast.error('Guest login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white dark:from-gray-900 dark:to-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-200">
            <ShoppingBag className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            TanzeelKart
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            by QalbConverfy
          </p>
        </div>

        {/* Login Type Tabs */}
        {step === 'input' && (
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-2xl p-1 mb-6">
            {[
              { id: 'phone', label: '📱 Phone', },
              { id: 'email', label: '📧 Email', },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setLoginType(tab.id)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  loginType === tab.id
                    ? 'bg-white dark:bg-gray-700 text-primary-600 shadow-sm'
                    : 'text-gray-500'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        )}

        {/* Card */}
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-800 p-8">

          {/* ── Phone Login ── */}
          {loginType === 'phone' && step === 'input' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Phone Se Login
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                OTP aapke number pe aayega
              </p>
              <form onSubmit={phoneForm.handleSubmit(onSendOTP)}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <input
                      {...phoneForm.register('phone')}
                      type="tel"
                      placeholder="9876543210"
                      maxLength={10}
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                    />
                  </div>
                  {phoneForm.formState.errors.phone && (
                    <p className="text-red-500 text-xs mt-1">
                      {phoneForm.formState.errors.phone.message}
                    </p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {loading
                    ? <Loader2 className="w-5 h-5 animate-spin" />
                    : <><span>OTP Bhejo</span><ArrowRight className="w-5 h-5" /></>
                  }
                </button>
              </form>
            </>
          )}

          {/* ── OTP Verify ── */}
          {loginType === 'phone' && step === 'otp' && (
            <>
              <button
                onClick={() => setStep('input')}
                className="text-sm text-primary-600 font-medium mb-4 hover:underline"
              >
                ← Wapas
              </button>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                OTP Verify Karo
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                <span className="font-semibold text-gray-700 dark:text-gray-300">
                  {phone}
                </span>{' '}
                pe OTP bheja gaya
              </p>
              <form onSubmit={otpForm.handleSubmit(onVerifyOTP)}>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    6-digit OTP
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <input
                      {...otpForm.register('otp')}
                      type="tel"
                      placeholder="123456"
                      maxLength={6}
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all text-center text-2xl font-bold tracking-widest"
                    />
                  </div>
                  {otpForm.formState.errors.otp && (
                    <p className="text-red-500 text-xs mt-1">
                      {otpForm.formState.errors.otp.message}
                    </p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {loading
                    ? <Loader2 className="w-5 h-5 animate-spin" />
                    : <><span>Verify Karo</span><ArrowRight className="w-5 h-5" /></>
                  }
                </button>
                <div className="text-center mt-4">
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={resendTimer > 0}
                    className="text-sm text-primary-600 font-medium disabled:text-gray-400 hover:underline"
                  >
                    {resendTimer > 0
                      ? `Resend OTP (${resendTimer}s)`
                      : 'OTP Dobara Bhejo'
                    }
                  </button>
                </div>
              </form>
            </>
          )}

          {/* ── Email Login ── */}
          {loginType === 'email' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Email Se Login
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                Email aur password daalo
              </p>
              <form onSubmit={emailForm.handleSubmit(onEmailLogin)}>
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        {...emailForm.register('email')}
                        type="email"
                        placeholder="arman@example.com"
                        className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                    </div>
                    {emailForm.formState.errors.email && (
                      <p className="text-red-500 text-xs mt-1">
                        {emailForm.formState.errors.email.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        {...emailForm.register('password')}
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        className="w-full pl-10 pr-10 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-3 text-gray-400"
                      >
                        {showPassword
                          ? <EyeOff className="w-5 h-5" />
                          : <Eye className="w-5 h-5" />
                        }
                      </button>
                    </div>
                    {emailForm.formState.errors.password && (
                      <p className="text-red-500 text-xs mt-1">
                        {emailForm.formState.errors.password.message}
                      </p>
                    )}
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {loading
                    ? <Loader2 className="w-5 h-5 animate-spin" />
                    : <><span>Login Karo</span><ArrowRight className="w-5 h-5" /></>
                  }
                </button>
              </form>
            </>
          )}

          {/* ── Divider ── */}
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
            <span className="text-xs text-gray-400">ya</span>
            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          </div>

          {/* ── Guest Login ── */}
          <button
            onClick={onGuestLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 text-gray-500 hover:border-primary-300 hover:text-primary-600 transition-all disabled:opacity-50"
          >
            <UserX className="w-5 h-5" />
            <span className="text-sm font-medium">
              Guest Ke Roop Mein Continue Karo
            </span>
          </button>

        </div>

        {/* Register Link */}
        <p className="text-center text-gray-500 text-sm mt-6">
          Naya account?{' '}
          <Link
            href="/register"
            className="text-primary-600 font-semibold hover:underline"
          >
            Register Karo
          </Link>
        </p>

      </div>
    </div>
  )
}
