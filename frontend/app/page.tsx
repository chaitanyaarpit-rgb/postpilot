'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import api from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const { token, setUser } = useAuthStore()

  useEffect(() => {
    if (!token) {
      router.push('/login')
      return
    }
    api.get('/api/auth/me').then((res) => {
      setUser(res.data)
      if (!res.data.onboarding_complete) {
        router.push('/onboarding')
      } else {
        router.push('/dashboard')
      }
    }).catch(() => {
      router.push('/login')
    })
  }, [token])

  return <div className="flex items-center justify-center h-screen text-gray-400">Loading...</div>
}
