'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import {
  ShoppingBag, Phone, Lock, Mail,
  User, ArrowRight, Loader2,
  Eye, EyeOff
} from 'lucide-react'
import { authAPI, setTokens } from '@/lib/api'
import { useAuthStore } from '@/lib/store'


const phoneSchema = z.object({
  phone: z
    .string()
    .min(10, '10 digits chahiye')
    .max(10, '10 digits chahiye')
    .regex(/^[6-9]\d{9}$/, 'Valid Indian number daalo'),
  full_name: z
    .string()
    .min(2, 'Naam 2+ characters ka hona chahiye'),
})

const otpSchema = z.object({
  otp: z
    .string()
    .length(6, 'OTP 6 digits ka hona chahiye')
    .regex(/^\d{6}$/, 'Sirf numbers daalo'),
})

const emailSchema = z.object({
  full_name: z
    .string()
    .min(2, 'Naam 2+ characters ka hona chahiye'),
  email: z.string().email('Valid email daalo'),
  password: z
    .string()
    .min(6, 'Password 6+ characters hona chahiye'),
})


export default function RegisterPage() {
  const router = useRouter()
  const { setUser } = useAuthStore()

  const [registerType, setRegisterType] = useState('phone')
  const [step, setStep] = useState('input')
  const [phone, setPhone] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendTimer, setResendTimer] = useState(0)
  const [showPassword, setShowPassword] = useState(false)

  const phoneForm = useForm({ resolver: zodResolver(phoneSchema) })
  const otpForm = useForm({ resolver: zodResolver(otpSchema) })
  const emailForm = useForm({ resolver: zodResolver(emailSchema) })

  const startTimer = () => {
    setResendTimer(30)
    const interval = setInterval(() => {
      setResendTimer((prev) => {
        if (prev <= 1) { clearInterval(interval); return 0 }
        return prev - 1
      })
    }, 1000)
  }

  const handleSuccess = (data, name = '') => {
    setTokens(data.access_token, data.refresh_token)
    setUser({
      id: data.user_id,
      phone: phone || '',
      full_name: name || fullName,
      role: data.role,
      account_type: data.account_type,
    })
    toast.success('Account ban gaya! 🎉')
    router.push('/select-account-type')
  }

  const onSendOTP = async (data) => {
    setLoading(true)
    try {
      await authAPI.sendOTP(data.phone)
      setPhone(data.phone)
      setFullName(data.full_name)
      setStep('otp')
      startTimer()
      toast.success('OTP bheja gaya!')
    } catch (err) {
      toast.error(err.response?.data?.message || 'OTP nahi gaya')
    } finally {
      setLoading(false)
    }
  }

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

  const onEmailRegister = async (data) => {
    setLoading(true)
    try {
      const res = await authAPI.emailRegister(data)
      handleSuccess(res.data, data.full_name)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Register failed')
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
            Naya Account Banao
          </p>
        </div>

        {/* Tabs */}
        {step === 'input' && (
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-2xl p-1 mb-6">
            {[
              { id: 'phone', label: '📱 Phone' },
              { id: 'email', label: '📧 Email' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setRegisterType(tab.id)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  registerType === tab.id
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

          {/* ── Phone Register ── */}
          {registerType === 'phone' && step === 'input' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Phone Se Register
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                OTP se verify hoga
              </p>
              <form onSubmit={phoneForm.handleSubmit(onSendOTP)}>
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Aapka Naam
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        {...phoneForm.register('full_name')}
                        type="text"
                        placeholder="Mohammad Arman"
                        className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                    </div>
                    {phoneForm.formState.errors.full_name && (
                      <p className="text-red-500 text-xs mt-1">
                        {phoneForm.formState.errors.full_name.message}
                      </p>
                    )}
                  </div>
                  <div>
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

          {/* ── OTP ── */}
          {registerType === 'phone' && step === 'otp' && (
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
                    : <><span>Account Banao</span><ArrowRight className="w-5 h-5" /></>
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
                      ? `Resend (${resendTimer}s)`
                      : 'OTP Dobara Bhejo'
                    }
                  </button>
                </div>
              </form>
            </>
          )}

          {/* ── Email Register ── */}
          {registerType === 'email' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Email Se Register
              </h2>
              <p className="text-gray-500 text-sm mb-6">
                Email aur password se account banao
              </p>
              <form onSubmit={emailForm.handleSubmit(onEmailRegister)}>
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Aapka Naam
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        {...emailForm.register('full_name')}
                        type="text"
                        placeholder="Mohammad Arman"
                        className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                    </div>
                    {emailForm.formState.errors.full_name && (
                      <p className="text-red-500 text-xs mt-1">
                        {emailForm.formState.errors.full_name.message}
                      </p>
                    )}
                  </div>
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
                    : <><span>Account Banao</span><ArrowRight className="w-5 h-5" /></>
                  }
                </button>
              </form>
            </>
          )}

        </div>

        {/* Login Link */}
        <p className="text-center text-gray-500 text-sm mt-6">
          Pehle se account hai?{' '}
          <Link
            href="/login"
            className="text-primary-600 font-semibold hover:underline"
          >
            Login Karo
          </Link>
        </p>

      </div>
    </div>
  )
}
