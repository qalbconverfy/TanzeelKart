/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ['*']
    }
  },
  images: {
    domains: [
      'i.ytimg.com',
      'img.youtube.com',
      'res.cloudinary.com',
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_APP_NAME: 'TanzeelKart',
    NEXT_PUBLIC_COMPANY: 'QalbConverfy',
  },
}

module.exports = nextConfig
