'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import api from '@/lib/api'

const STEPS = ['Business Profile', 'API Keys', 'Schedule']

export default function OnboardingPage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register, handleSubmit, getValues } = useForm()

  const onProfileSubmit = async (data: any) => {
    setError('')
    setLoading(true)
    try {
      await api.post('/api/onboarding/profile', {
        company_name: data.company_name,
        industry: data.industry,
        target_audience: data.target_audience,
        competitors: data.competitors,
        tone: data.tone,
        post_hour: parseInt(data.post_hour),
        post_timezone: data.post_timezone,
        post_frequency: 'daily',
      })
      setStep(1)
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error saving profile')
    } finally {
      setLoading(false)
    }
  }

  const onKeysSubmit = async (data: any) => {
    setError('')
    setLoading(true)
    try {
      await api.post('/api/onboarding/api-keys', {
        openai_key: data.openai_key,
        tavily_key: data.tavily_key,
        linkedin_access_token: data.linkedin_access_token,
        linkedin_org_id: data.linkedin_org_id,
        linkedin_client_id: data.linkedin_client_id || '',
        linkedin_client_secret: data.linkedin_client_secret || '',
      })
      router.push('/dashboard')
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error saving API keys')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-lg">
        {/* Progress */}
        <div className="flex items-center mb-8 gap-2">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center flex-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                ${i <= step ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-400'}`}>
                {i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-1 mx-1 ${i < step ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-1">{STEPS[step]}</h2>
        <p className="text-gray-500 text-sm mb-6">
          {step === 0 && 'Tell us about your business so we can tailor content for you.'}
          {step === 1 && 'Paste your API keys. They are encrypted and stored securely.'}
        </p>

        {error && <p className="text-red-500 text-sm mb-4 bg-red-50 p-3 rounded-lg">{error}</p>}

        {step === 0 && (
          <form onSubmit={handleSubmit(onProfileSubmit)} className="space-y-4">
            <input {...register('company_name', { required: true })} placeholder="Company Name"
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            <input {...register('industry', { required: true })} placeholder="Industry (e.g. Marketing Technology)"
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            <textarea {...register('target_audience', { required: true })}
              placeholder="Target Audience (e.g. CMOs, marketing managers at mid-size firms)"
              rows={3}
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            <input {...register('competitors')} placeholder="Competitors (comma-separated, optional)"
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            <select {...register('tone')}
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400">
              <option value="professional">Professional</option>
              <option value="casual">Casual & Friendly</option>
              <option value="thought-leadership">Thought Leadership</option>
              <option value="educational">Educational</option>
            </select>
            <div className="flex gap-3">
              <input {...register('post_hour')} type="number" min={0} max={23} defaultValue={9}
                placeholder="Post Hour (0-23)"
                className="w-1/2 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              <input {...register('post_timezone')} defaultValue="UTC" placeholder="Timezone (e.g. Asia/Kolkata)"
                className="w-1/2 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50">
              {loading ? 'Saving...' : 'Continue →'}
            </button>
          </form>
        )}

        {step === 1 && (
          <form onSubmit={handleSubmit(onKeysSubmit)} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">OpenAI API Key</label>
              <input {...register('openai_key', { required: true })} type="password" placeholder="sk-..."
                className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              <a href="https://platform.openai.com/api-keys" target="_blank" className="text-xs text-indigo-500 mt-1 block">Get key →</a>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Tavily API Key</label>
              <input {...register('tavily_key', { required: true })} type="password" placeholder="tvly-..."
                className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              <a href="https://app.tavily.com" target="_blank" className="text-xs text-indigo-500 mt-1 block">Get key (free tier available) →</a>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">LinkedIn Access Token</label>
              <input {...register('linkedin_access_token', { required: true })} type="password"
                className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">LinkedIn Organization ID</label>
              <input {...register('linkedin_org_id', { required: true })} placeholder="123456789"
                className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              <p className="text-xs text-gray-400 mt-1">Found in your LinkedIn company page URL</p>
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50">
              {loading ? 'Saving...' : '🚀 Launch PostPilot'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
