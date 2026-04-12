'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import {
  Store, User, Hash,
  CheckCircle, Loader2, ArrowRight
} from 'lucide-react'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store'


const layer1Schema = z.object({
  shop_owner_name: z.string().min(2, 'Naam daalo'),
  seller_name: z.string().min(2, 'Seller naam daalo'),
})

const layer2Schema = z.object({
  shop_id: z.string().min(3, 'Shop ID daalo'),
})


export default function ShopVerifyPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [layer, setLayer] = useState(1)
  const [loading, setLoading] = useState(false)


  const layer1Form = useForm({
    resolver: zodResolver(layer1Schema),
  })

  const layer2Form = useForm({
    resolver: zodResolver(layer2Schema),
  })


  const onLayer1 = async (data) => {
    if (!user?.id) return
    setLoading(true)
    try {
      await authAPI.shopVerifyLayer1(user.id, data)
      toast.success('Layer 1 complete!')
      setLayer(2)
    } catch (err) {
      toast.error(
        err.response?.data?.message || 'Error aaya'
      )
    } finally {
      setLoading(false)
    }
  }


  const onLayer2 = async (data) => {
    if (!user?.id) return
    setLoading(true)
    try {
      await authAPI.shopVerifyLayer2(user.id, data)
      toast.success('Shop verify ho gayi! 🎉')
      router.push('/home')
    } catch (err) {
      toast.error(
        err.response?.data?.message || 'Error aaya'
      )
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Store className="w-9 h-9 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Shop Verify Karo
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            2 steps mein verify hoga
          </p>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-3 mb-8">
          {[1, 2].map((step) => (
            <div key={step} className="flex-1">
              <div className={`h-2 rounded-full transition-all ${
                layer >= step
                  ? 'bg-primary-600'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`} />
              <p className={`text-xs mt-1 text-center ${
                layer >= step
                  ? 'text-primary-600 font-medium'
                  : 'text-gray-400'
              }`}>
                Layer {step}
              </p>
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-800 p-8">

          {layer === 1 ? (
            <>
              <h2 className="font-bold text-gray-900 dark:text-white text-lg mb-4">
                Shop Ki Details
              </h2>
              <form onSubmit={layer1Form.handleSubmit(onLayer1)}>
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Owner Ka Naam
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        {...layer1Form.register('shop_owner_name')}
                        placeholder="Arman Khan"
                        className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                    </div>
                    {layer1Form.formState.errors.shop_owner_name && (
                      <p className="text-red-500 text-xs mt-1">
                        {layer1Form.formState.errors.shop_owner_name.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Seller Ka Naam
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        {...layer1Form.register('seller_name')}
                        placeholder="Mohammad Arman"
                        className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                      />
                    </div>
                    {layer1Form.formState.errors.seller_name && (
                      <p className="text-red-500 text-xs mt-1">
                        {layer1Form.formState.errors.seller_name.message}
                      </p>
                    )}
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>Aage Bado <ArrowRight className="w-5 h-5" /></>
                  )}
                </button>
              </form>
            </>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium text-sm">
                  Layer 1 Complete!
                </span>
              </div>
              <h2 className="font-bold text-gray-900 dark:text-white text-lg mb-4">
                Shop ID Daalo
              </h2>
              <p className="text-gray-500 text-sm mb-4">
                TanzeelKart ne aapko jo Shop ID di hai
                woh daalo (TK-2026-XXXXX format)
              </p>
              <form onSubmit={layer2Form.handleSubmit(onLayer2)}>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Shop ID
                  </label>
                  <div className="relative">
                    <Hash className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <input
                      {...layer2Form.register('shop_id')}
                      placeholder="TK-2026-00001"
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all font-mono"
                    />
                  </div>
                  {layer2Form.formState.errors.shop_id && (
                    <p className="text-red-500 text-xs mt-1">
                      {layer2Form.formState.errors.shop_id.message}
                    </p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white font-semibold py-3 rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>Verify Karo <CheckCircle className="w-5 h-5" /></>
                  )}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
