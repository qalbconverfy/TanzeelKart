'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  ShoppingBag, Cloud, MapPin,
  Bell, Search, ChevronRight,
  Truck, Video, BookOpen,
  Sun, CloudRain, Wind,
  Store, Loader2, LogOut,
  User, Menu, X
} from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { weatherAPI, shopAPI, notificationAPI } from '@/lib/api'
import { formatPrice, formatDistance, timeAgo } from '@/lib/utils'
import toast from 'react-hot-toast'


export default function HomePage() {
  const router = useRouter()
  const { user, logout, isAuthenticated } = useAuthStore()

  const [weather, setWeather] = useState(null)
  const [shops, setShops] = useState([])
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [menuOpen, setMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')


  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    fetchData()
  }, [isAuthenticated])


  const fetchData = async () => {
    setLoading(true)
    try {
      // Weather fetch
      const weatherRes = await weatherAPI.getLatest()
      setWeather(weatherRes.data)

      // Nearby shops
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (pos) => {
            const shopsRes = await shopAPI.getNearbyShops({
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
              radius_km: 2.0
            })
            setShops(shopsRes.data.slice(0, 6))
          },
          async () => {
            // Location nahi mili — default Reoti
            const shopsRes = await shopAPI.getNearbyShops({
              latitude: 26.0500,
              longitude: 84.1800,
              radius_km: 2.0
            })
            setShops(shopsRes.data.slice(0, 6))
          }
        )
      }

      // Notifications
      const notifRes = await notificationAPI.getNotifications()
      setNotifications(notifRes.data.notifications.slice(0, 5))
      setUnreadCount(notifRes.data.unread_count)

    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }


  const handleLogout = () => {
    logout()
    toast.success('Logout ho gaye!')
    router.push('/login')
  }


  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/shops?search=${searchQuery}`)
    }
  }


  const getWeatherIcon = (temp) => {
    if (temp > 35) return <Sun className="w-8 h-8 text-orange-500" />
    if (temp < 15) return <Wind className="w-8 h-8 text-blue-400" />
    return <Cloud className="w-8 h-8 text-gray-400" />
  }


  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-primary-600 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Loading...</p>
        </div>
      </div>
    )
  }


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 pb-20">

      {/* Header */}
      <header className="bg-white dark:bg-gray-900 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">

            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <ShoppingBag className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-bold text-gray-900 dark:text-white">
                  TanzeelKart
                </span>
                <span className="text-xs text-gray-500 block leading-none">
                  Reoti, Ballia
                </span>
              </div>
            </div>

            {/* Right Icons */}
            <div className="flex items-center gap-3">
              {/* Notifications */}
              <Link href="/notifications" className="relative">
                <Bell className="w-6 h-6 text-gray-600 dark:text-gray-300" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Link>

              {/* Menu */}
              <button onClick={() => setMenuOpen(!menuOpen)}>
                {menuOpen
                  ? <X className="w-6 h-6 text-gray-600" />
                  : <Menu className="w-6 h-6 text-gray-600" />
                }
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {menuOpen && (
            <div className="mt-3 pb-3 border-t border-gray-100 dark:border-gray-800 animate-slide-down">
              <div className="pt-3 space-y-2">
                <Link
                  href="/profile"
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                  onClick={() => setMenuOpen(false)}
                >
                  <User className="w-5 h-5 text-gray-500" />
                  <span className="text-gray-700 dark:text-gray-300">
                    {user?.full_name || 'Profile'}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-red-50 w-full text-left"
                >
                  <LogOut className="w-5 h-5 text-red-500" />
                  <span className="text-red-500">Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </header>


      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* Welcome */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-5 text-white">
          <p className="text-primary-100 text-sm mb-1">
            Assalamu Alaikum! 👋
          </p>
          <h1 className="text-xl font-bold">
            {user?.full_name || 'TanzeelKart Pe Aapka Swagat!'}
          </h1>
          <p className="text-primary-200 text-sm mt-1">
            Reoti, Ballia — Apna Gaon, Apna Bazaar
          </p>
        </div>


        {/* Search */}
        <form onSubmit={handleSearch}>
          <div className="relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Shop ya product dhundo..."
              className="w-full pl-10 pr-4 py-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            />
          </div>
        </form>


        {/* Weather Widget */}
        {weather && (
          <div className="bg-white dark:bg-gray-900 rounded-2xl p-4 border border-gray-100 dark:border-gray-800">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Cloud className="w-5 h-5 text-primary-600" />
                Aaj Ka Mausam
              </h2>
              <Link
                href="/weather"
                className="text-sm text-primary-600 flex items-center"
              >
                Aur dekho <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="flex items-center gap-4">
              {getWeatherIcon(weather.temperature)}
              <div className="flex-1">
                <div className="flex items-end gap-2">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">
                    {weather.temperature}°C
                  </span>
                  <span className="text-gray-500 text-sm mb-1">
                    Reoti, Ballia
                  </span>
                </div>
                <div className="flex gap-4 mt-1">
                  <span className="text-sm text-gray-500">
                    💧 {weather.humidity}%
                  </span>
                  {weather.rainfall > 0 && (
                    <span className="text-sm text-blue-500">
                      🌧️ {weather.rainfall}mm
                    </span>
                  )}
                  {weather.wind_speed && (
                    <span className="text-sm text-gray-500">
                      💨 {weather.wind_speed} km/h
                    </span>
                  )}
                </div>
              </div>
            </div>
            {weather.advice && (
              <div className="mt-3 bg-primary-50 dark:bg-primary-900/20 rounded-xl p-3">
                <p className="text-sm text-primary-700 dark:text-primary-400">
                  🌾 {weather.advice}
                </p>
              </div>
            )}
          </div>
        )}


        {/* Quick Actions */}
        <div>
          <h2 className="font-bold text-gray-900 dark:text-white mb-3">
            Quick Access
          </h2>
          <div className="grid grid-cols-4 gap-3">
            {[
              {
                icon: <Store className="w-6 h-6" />,
                label: "Shops",
                href: "/shops",
                color: "bg-green-100 text-green-600"
              },
              {
                icon: <Truck className="w-6 h-6" />,
                label: "Orders",
                href: "/orders",
                color: "bg-blue-100 text-blue-600"
              },
              {
                icon: <MapPin className="w-6 h-6" />,
                label: "Map",
                href: "/map",
                color: "bg-red-100 text-red-600"
              },
              {
                icon: <Video className="w-6 h-6" />,
                label: "Videos",
                href: "/videos",
                color: "bg-purple-100 text-purple-600"
              },
              {
                icon: <BookOpen className="w-6 h-6" />,
                label: "Udhaar",
                href: "/udhaar",
                color: "bg-orange-100 text-orange-600"
              },
              {
                icon: <Cloud className="w-6 h-6" />,
                label: "Mausam",
                href: "/weather",
                color: "bg-cyan-100 text-cyan-600"
              },
              {
                icon: <Bell className="w-6 h-6" />,
                label: "Alerts",
                href: "/notifications",
                color: "bg-yellow-100 text-yellow-600"
              },
              {
                icon: <User className="w-6 h-6" />,
                label: "Profile",
                href: "/profile",
                color: "bg-gray-100 text-gray-600"
              },
            ].map((item, i) => (
              <Link
                key={i}
                href={item.href}
                className="flex flex-col items-center gap-2 p-3 bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 hover:scale-105 transition-transform"
              >
                <div className={`${item.color} p-2 rounded-xl`}>
                  {item.icon}
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {item.label}
                </span>
              </Link>
            ))}
          </div>
        </div>


        {/* Nearby Shops */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-gray-900 dark:text-white">
              Nearby Shops
            </h2>
            <Link
              href="/shops"
              className="text-sm text-primary-600 flex items-center"
            >
              Sab dekho <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          {shops.length === 0 ? (
            <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 text-center border border-gray-100">
              <Store className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">
                Aas paas koi shop nahi mili
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {shops.map((shop) => (
                <Link
                  key={shop.id}
                  href={`/shops/${shop.id}`}
                  className="bg-white dark:bg-gray-900 rounded-2xl p-4 border border-gray-100 dark:border-gray-800 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Store className="w-6 h-6 text-primary-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                        {shop.name}
                      </h3>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {shop.category}
                      </p>
                      <div className="flex items-center gap-3 mt-1">
                        {shop.distance_km && (
                          <span className="text-xs text-primary-600 font-medium">
                            📍 {formatDistance(shop.distance_km)}
                          </span>
                        )}
                        {shop.is_delivery && (
                          <span className="text-xs text-green-600">
                            🛵 Delivery
                          </span>
                        )}
                        {shop.rating > 0 && (
                          <span className="text-xs text-yellow-600">
                            ⭐ {shop.rating}
                          </span>
                        )}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>


        {/* Recent Notifications */}
        {notifications.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-bold text-gray-900 dark:text-white">
                Recent Notifications
              </h2>
              <Link
                href="/notifications"
                className="text-sm text-primary-600 flex items-center"
              >
                Sab dekho <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="space-y-2">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`bg-white dark:bg-gray-900 rounded-xl p-3 border transition-all ${
                    !notif.is_read
                      ? 'border-primary-200 bg-primary-50/50'
                      : 'border-gray-100 dark:border-gray-800'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      !notif.is_read
                        ? 'bg-primary-600'
                        : 'bg-gray-300'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {notif.title}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {notif.body}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {timeAgo(notif.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>


      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-around py-2">
            {[
              { icon: <ShoppingBag className="w-6 h-6" />, label: "Home", href: "/home", active: true },
              { icon: <Store className="w-6 h-6" />, label: "Shops", href: "/shops", active: false },
              { icon: <Truck className="w-6 h-6" />, label: "Orders", href: "/orders", active: false },
              { icon: <MapPin className="w-6 h-6" />, label: "Map", href: "/map", active: false },
              { icon: <User className="w-6 h-6" />, label: "Profile", href: "/profile", active: false },
            ].map((item, i) => (
              <Link
                key={i}
                href={item.href}
                className={`flex flex-col items-center gap-1 px-3 py-1 rounded-xl transition-colors ${
                  item.active
                    ? 'text-primary-600'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                {item.icon}
                <span className="text-xs font-medium">
                  {item.label}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </nav>

    </div>
  )
}
