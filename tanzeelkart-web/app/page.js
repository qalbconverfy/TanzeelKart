import Link from 'next/link'
import {
  ShoppingBag, Cloud, MapPin,
  Truck, Video, Shield,
  ArrowRight, Star, Zap
} from 'lucide-react'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white dark:bg-gray-950">

      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 bg-white/90 dark:bg-gray-950/90 backdrop-blur-md border-b border-gray-100 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <ShoppingBag className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-bold text-gray-900 dark:text-white text-lg">
                  TanzeelKart
                </span>
                <span className="text-xs text-gray-500 block leading-none">
                  by QalbConverfy
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary-600"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-24 pb-16 px-4 bg-gradient-to-br from-primary-50 to-white dark:from-gray-900 dark:to-gray-950">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 text-sm font-medium px-4 py-2 rounded-full mb-6">
            <Zap className="w-4 h-4" />
            Reoti, Ballia ka Digital Bazaar
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight mb-6">
            Apna Gaon,{' '}
            <span className="text-primary-600">
              Apna Bazaar
            </span>
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
            Local shops se ghar pe delivery, real-time
            mausam ki jaankari, aur bahut kuch — sirf
            TanzeelKart pe
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/register"
              className="inline-flex items-center justify-center gap-2 bg-primary-600 text-white font-semibold px-8 py-4 rounded-xl hover:bg-primary-700 transition-all hover:scale-105 shadow-lg shadow-primary-200"
            >
              Shuru Karo
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/shops"
              className="inline-flex items-center justify-center gap-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold px-8 py-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all"
            >
              <MapPin className="w-5 h-5 text-primary-600" />
              Shops Dekho
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Kya Milega TanzeelKart Pe?
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <ShoppingBag className="w-8 h-8 text-primary-600" />,
                title: "Local Marketplace",
                desc: "Reoti ke sab shops ek jagah — kirana, medical, agri sab",
                color: "bg-primary-50 dark:bg-primary-900/20"
              },
              {
                icon: <Truck className="w-8 h-8 text-blue-600" />,
                title: "1-2 Ghante Delivery",
                desc: "Order karo — 1-2 ghante mein ghar pe pahuncha denge",
                color: "bg-blue-50 dark:bg-blue-900/20"
              },
              {
                icon: <Cloud className="w-8 h-8 text-cyan-600" />,
                title: "Live Mausam",
                desc: "ESP32 sensors se real-time temperature, humidity, baarish",
                color: "bg-cyan-50 dark:bg-cyan-900/20"
              },
              {
                icon: <MapPin className="w-8 h-8 text-red-600" />,
                title: "Apna Map",
                desc: "Drone se banaya Reoti ka khud ka map — Google nahi!",
                color: "bg-red-50 dark:bg-red-900/20"
              },
              {
                icon: <Video className="w-8 h-8 text-purple-600" />,
                title: "Kisan Videos",
                desc: "Kheti, mandi bhav, mausam — sab YouTube videos",
                color: "bg-purple-50 dark:bg-purple-900/20"
              },
              {
                icon: <Shield className="w-8 h-8 text-orange-600" />,
                title: "Udhaar System",
                desc: "Digital khata — udhaar, delivery charge sab track karo",
                color: "bg-orange-50 dark:bg-orange-900/20"
              },
            ].map((feature, i) => (
              <div
                key={i}
                className={`${feature.color} rounded-2xl p-6 hover:scale-105 transition-transform`}
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="font-bold text-gray-900 dark:text-white text-lg mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4 bg-primary-600">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
            {[
              { value: "2km", label: "Delivery Radius" },
              { value: "1-2hr", label: "Delivery Time" },
              { value: "5★", label: "Verification" },
              { value: "24/7", label: "Weather Data" },
            ].map((stat, i) => (
              <div key={i}>
                <div className="text-3xl font-bold text-white mb-1">
                  {stat.value}
                </div>
                <div className="text-primary-200 text-sm">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 bg-gray-900 text-center">
        <p className="text-gray-400 text-sm">
          © 2026 TanzeelKart by{' '}
          <span className="text-primary-400 font-medium">
            QalbConverfy
          </span>
          {' '}(ZEAIPC). All rights reserved.
        </p>
        <p className="text-gray-600 text-xs mt-1">
          Reoti, Ballia, Uttar Pradesh, India
        </p>
      </footer>

    </main>
  )
}
