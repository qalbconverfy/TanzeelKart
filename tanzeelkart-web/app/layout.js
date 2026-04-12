import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

export const metadata = {
  title: 'TanzeelKart — Apna Gaon, Apna Bazaar',
  description:
    'TanzeelKart — Local marketplace for Reoti, Ballia. ' +
    'Shop online, track weather, get home delivery. ' +
    'by QalbConverfy (ZEAIPC)',
  keywords: [
    'TanzeelKart', 'Reoti', 'Ballia',
    'local shop', 'kirana', 'delivery',
    'QalbConverfy', 'ZEAIPC'
  ],
  authors: [{ name: 'ZEAIPC — QalbConverfy' }],
  openGraph: {
    title: 'TanzeelKart',
    description: 'Apna Gaon, Apna Bazaar',
    type: 'website',
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="hi" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Providers>
          {children}
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#0f172a',
                color: '#fff',
                borderRadius: '12px',
                fontSize: '14px',
              },
              success: {
                iconTheme: {
                  primary: '#16a34a',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
