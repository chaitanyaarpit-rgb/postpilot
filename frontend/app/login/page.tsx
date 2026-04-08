'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/store'

export default function LoginPage() {
  const router = useRouter()
  const { setToken } = useAuthStore()
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')
  const { register, handleSubmit } = useForm()

  const onSubmit = async (data: any) => {
    setError('')
    try {
      if (isRegister) {
        const res = await api.post('/api/auth/register', data)
        setToken(res.data.access_token)
        router.push('/onboarding')
      } else {
        const form = new FormData()
        form.append('username', data.email)
        form.append('password', data.password)
        const res = await api.post('/api/auth/login', form)
        setToken(res.data.access_token)
        router.push('/')
      }
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Something went wrong')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-600">PostPilot</h1>
          <p className="text-gray-500 mt-1">AI-powered LinkedIn automation</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {isRegister && (
            <input
              {...register('full_name')}
              placeholder="Full Name"
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          )}
          <input
            {...register('email')}
            type="email"
            placeholder="Email"
            className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <input
            {...register('password')}
            type="password"
            placeholder="Password"
            className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition"
          >
            {isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button onClick={() => setIsRegister(!isRegister)} className="text-indigo-600 font-medium">
            {isRegister ? 'Sign in' : 'Sign up'}
          </button>
        </p>
      </div>
    </div>
  )
}
