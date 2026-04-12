'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { ShoppingBag, Phone, Lock, ArrowRight, Loader2 } from 'lucide-react'
import { authAPI, setTokens } from '@/lib/api'
import { useAuthStore } from '@/lib/store'


// Validation
const phoneSchema = z.object({
  phone: z
    .string()
    .min(10, 'Phone number 10 digits ka hona chahiye')
    .max(10, 'Phone number 10 digits ka hona chahiye')
    .regex(/^[6-9]\d{9}$/, 'Valid Indian number daalo'),
})

const otpSchema = z.object({
  otp: z
    .string()
    .min(6, 'OTP 6 digits ka hona chahiye')
    .max(6, 'OTP 6 digits ka hona chahiye')
    .regex(/^\d{6}$/, 'Sirf numbers daalo'),
})


export default function LoginPage() {
  const router = useRouter()
  const { setUser } = useAuthStore()

  const [step, setStep] = useState('phone')
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendTimer, setResendTimer] = useState(0)

  const phoneForm = useForm({
    resolver: zodResolver(phoneSchema),
    defaultValues: { phone: '' }
  })

  const otpForm = useForm({
    resolver: zodResolver(otpSchema),
    defaultValues: { otp: '' }
  })

  // Timer start
  const startTimer = () => {
    setResendTimer(30)
    const interval = setInterval(() => {
      setResendTimer((prev) => {
        if (prev <= 1) {
          clearInterval(interval)
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }

  // Send OTP
  const onSendOTP = async (data) => {
    setLoading(true)
    try {
      await authAPI.sendOTP(data.phone)
      setPhone(data.phone)
      setStep('otp')
      startTimer()
      toast.success('OTP bhej diya!')
    } catch (err) {
      toast.error(
        err.response?.data?.message || 'OTP nahi gaya'
      )
    } finally {
      setLoading(false)
    }
  }

  // Verify OTP
  const onVerifyOTP = async (data) => {
    setLoading(true)
    try {
      const res = await authAPI.verifyOTP(phone, data.otp)
      const { access_token, refresh_token, user_id, role, account_type, is_new_user } = res.data

      setTokens(access_token, refresh_token)

      // User info set karo
      setUser({
        id: user_id,
        phone,
        role,
        account_type,
      })

      toast.success('Login ho gaya! 🎉')

      // New user → account type select
      if (is_new_user || !account_type || account_type === 'skip') {
        router.push('/select-account-type')
      } else {
        router.push('/home')
      }

    } catch (err) {
      toast.error(
        err.response?.data?.message || 'OTP galat hai'
      )
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

        {/* Card */}
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-800 p-8">

          {step === 'phone' ? (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Login Karo
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                Phone number daalo — OTP aayega
              </p>

              <form onSubmit={phoneForm.handleSubmit(onSendOTP)}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Phone className="w-5 h-5 text-gray-400" />
                    </div>
                    <input
                      {...phoneForm.register('phone')}
                      type="tel"
                      placeholder="9876543210"
                      maxLength={10}
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
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
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      OTP Bhejo
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </form>
            </>
          ) : (
            <>
              <button
                onClick={() => setStep('phone')}
                className="text-sm text-primary-600 font-medium mb-4 flex items-center gap-1 hover:underline"
              >
                ← Wapas
              </button>

              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                OTP Verify Karo
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                {phone} pe OTP bheja gaya
              </p>

              <form onSubmit={otpForm.handleSubmit(onVerifyOTP)}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    6-digit OTP
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="w-5 h-5 text-gray-400" />
                    </div>
                    <input
                      {...otpForm.register('otp')}
                      type="number"
                      placeholder="123456"
                      maxLength={6}
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-center text-2xl font-bold tracking-widest"
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
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      Verify Karo
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>

                {/* Resend */}
                <div className="text-center mt-4">
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={resendTimer > 0}
                    className="text-sm text-primary-600 font-medium disabled:text-gray-400 disabled:cursor-not-allowed hover:underline"
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
