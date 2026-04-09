'use client'
import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import { useForm } from 'react-hook-form'
import api from '@/lib/api'

export default function SettingsPage() {
  const [tab, setTab] = useState<'profile' | 'keys'>('profile')
  const [saved, setSaved] = useState(false)
  const { register, handleSubmit } = useForm()

  const onSave = async (data: any) => {
    if (tab === 'profile') {
      await api.post('/api/onboarding/profile', {
        ...data,
        post_hour: parseInt(data.post_hour),
        post_frequency: 'daily',
      })
    } else {
      await api.post('/api/onboarding/api-keys', data)
    }
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-50">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Settings</h2>

        <div className="flex gap-2 mb-6">
          {(['profile', 'keys'] as const).map((t) => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition
                ${tab === t ? 'bg-indigo-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50'}`}>
              {t === 'profile' ? 'Business Profile' : 'API Keys'}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6 max-w-lg">
          {saved && <p className="text-green-600 text-sm mb-4 bg-green-50 p-3 rounded-lg">Saved successfully.</p>}

          <form onSubmit={handleSubmit(onSave)} className="space-y-4">
            {tab === 'profile' && (
              <>
                <input {...register('company_name')} placeholder="Company Name"
                  className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                <input {...register('industry')} placeholder="Industry"
                  className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                <textarea {...register('target_audience')} placeholder="Target Audience" rows={3}
                  className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                <input {...register('competitors')} placeholder="Competitors (comma-separated)"
                  className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                <select {...register('tone')}
                  className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400">
                  <option value="professional">Professional</option>
                  <option value="casual">Casual & Friendly</option>
                  <option value="thought-leadership">Thought Leadership</option>
                  <option value="educational">Educational</option>
                </select>
                <div className="flex gap-3">
                  <input {...register('post_hour')} type="number" min={0} max={23} placeholder="Post Hour"
                    className="w-1/2 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  <input {...register('post_timezone')} placeholder="Timezone"
                    className="w-1/2 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
              </>
            )}

            {tab === 'keys' && (
              <>
                <div>
                  <label className="text-sm font-medium text-gray-700">OpenAI API Key</label>
                  <input {...register('openai_key')} type="password" placeholder="sk-..."
                    className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Tavily API Key</label>
                  <input {...register('tavily_key')} type="password" placeholder="tvly-..."
                    className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">LinkedIn Access Token</label>
                  <input {...register('linkedin_access_token')} type="password"
                    className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">LinkedIn Organization ID (optional)</label>
                  <input {...register('linkedin_org_id')} placeholder="Leave blank for personal profile"
                    className="w-full border rounded-lg px-4 py-3 mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
              </>
            )}

            <button type="submit"
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
              Save Changes
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}
