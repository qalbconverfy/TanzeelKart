import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'


// Tailwind class merge
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

// Price format
export function formatPrice(price) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
  }).format(price)
}

// Date format
export function formatDate(date) {
  return new Intl.DateTimeFormat('hi-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(date))
}

// Time ago
export function timeAgo(date) {
  const seconds = Math.floor(
    (new Date() - new Date(date)) / 1000
  )
  if (seconds < 60) return 'Abhi'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min pehle`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} ghante pehle`
  return `${Math.floor(seconds / 86400)} din pehle`
}

// Phone format
export function formatPhone(phone) {
  return phone.replace(/(\d{5})(\d{5})/, '$1 $2')
}

// Distance format
export function formatDistance(km) {
  if (km < 1) return `${Math.round(km * 1000)}m`
  return `${km.toFixed(1)}km`
}

// Order status color
export function getStatusColor(status) {
  const colors = {
    pending:   'bg-yellow-100 text-yellow-800',
    accepted:  'bg-blue-100 text-blue-800',
    preparing: 'bg-orange-100 text-orange-800',
    ready:     'bg-purple-100 text-purple-800',
    picked:    'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

// Order status Hindi
export function getStatusHindi(status) {
  const hindi = {
    pending:   'Pending',
    accepted:  'Accept hua',
    preparing: 'Taiyar ho raha hai',
    ready:     'Ready hai',
    picked:    'Pickup hua',
    delivered: 'Deliver ho gaya ✅',
    cancelled: 'Cancel hua ❌',
  }
  return hindi[status] || status
}

// Truncate text
export function truncate(text, length = 50) {
  if (!text) return ''
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

// Get initials
export function getInitials(name) {
  if (!name) return 'U'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}
