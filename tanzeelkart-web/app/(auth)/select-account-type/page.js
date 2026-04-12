'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import {
  Store, Stethoscope, User,
  Users, SkipForward, Loader2,
  ChevronRight
} from 'lucide-react'
import { authAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store'


const ACCOUNT_TYPES = [
  {
    id: 'shop',
    icon: <Store className="w-7 h-7" />,
    title: 'Shop Owner',
    desc: 'Kirana, Agri, Hardware ya koi bhi dukan',
    color: 'border-green-200 bg-green-50 dark:bg-green-900/20',
    iconColor: 'text-green-600',
    badge: '2 Step Verify',
    badgeColor: 'bg-green-100 text-green-700'
  },
  {
    id: 'medical',
    icon: <Stethoscope className="w-7 h-7" />,
    title: 'Medical / Pharmacy',
    desc: 'Dawakhana, Medical store, Healthcare',
    color: 'border-blue-200 bg-blue-50 dark:bg-blue-900/20',
    iconColor: 'text-blue-600',
    badge: '5 Step Verify',
    badgeColor: 'bg-blue-100 text-blue-700'
  },
  {
    id: 'normal',
    icon: <User className="w-7 h-7" />,
    title: 'Normal User',
    desc: 'Shopping karna, orders dena',
    color: 'border-purple-200 bg-purple-50 dark:bg-purple-900/20',
    iconColor: 'text-purple-600',
    badge: 'No Verify',
    badgeColor: 'bg-purple-100 text-purple-700'
  },
  {
    id: 'all_types',
    icon: <Users className="w-7 h-7" />,
    title: 'All Types',
    desc: 'Buyer bhi, seller bhi',
    color: 'border-orange-200 bg-orange-50 dark:bg-orange-900/20',
    iconColor: 'text-orange-600',
    badge: 'Multi Role',
    badgeColor: 'bg-orange-100 text-orange-700'
  },
  {
    id: 'skip',
    icon: <SkipForward className="w-7 h-7" />,
    title: 'Skip for Now',
    desc: 'Baad mein select karna',
    color: 'border-gray-200 bg-gray-50 dark:bg-gray-800',
    iconColor: 'text-gray-500',
    badge: 'Later',
    badgeColor: 'bg-gray-100 text-gray-600'
  },
]


export default function SelectAccountTypePage() {
  const router = useRouter()
  const { user, updateUser } = useAuthStore()
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)


  const handleSelect = async (type) => {
    if (!user?.id) {
      toast.error('User not found. Login again.')
      router.push('/login')
      return
    }

    setSelected(type)
    setLoading(true)

    try {
      const res = await authAPI.selectAccountType(
        user.id, type
      )

      updateUser({ account_type: type })
      toast.success('Account type select ho gaya!')

      // Next step
      const next = res.data.next_step
      if (next === 'complete_shop_verification') {
        router.push('/verify/shop')
      } else if (next === 'complete_medical_verification') {
        router.push('/verify/medical')
      } else {
        router.push('/home')
      }

    } catch (err) {
      toast.error('Kuch problem hui — dobara try karo')
      setSelected(null)
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Account Type Select Karo
          </h1>
          <p className="text-gray-500 text-sm">
            Aap TanzeelKart pe kya karna chahte ho?
          </p>
        </div>

        {/* Options */}
        <div className="space-y-3">
          {ACCOUNT_TYPES.map((type) => (
            <button
              key={type.id}
              onClick={() => handleSelect(type.id)}
              disabled={loading}
              className={`
                w-full text-left p-4 rounded-2xl border-2
                transition-all hover:scale-[1.01]
                disabled:opacity-50 disabled:cursor-not-allowed
                ${selected === type.id
                  ? 'border-primary-500 ring-2 ring-primary-200'
                  : type.color
                }
              `}
            >
              <div className="flex items-center gap-4">
                <div className={`${type.iconColor} flex-shrink-0`}>
                  {type.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {type.title}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${type.badgeColor}`}>
                      {type.badge}
                    </span>
                  </div>
                  <p className="text-gray-500 text-sm mt-0.5">
                    {type.desc}
                  </p>
                </div>
                {selected === type.id && loading ? (
                  <Loader2 className="w-5 h-5 animate-spin text-primary-600 flex-shrink-0" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                )}
              </div>
            </button>
          ))}
        </div>

      </div>
    </div>
  )
}
