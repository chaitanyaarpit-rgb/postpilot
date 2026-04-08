'use client'
import { useEffect, useState } from 'react'
import Sidebar from '@/components/Sidebar'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [generating, setGenerating] = useState(false)
  const { token } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!token) { router.push('/login'); return }
    api.get('/api/dashboard/stats').then((r) => setStats(r.data))
  }, [token])

  const generateNow = async () => {
    setGenerating(true)
    await api.post('/api/posts/generate-now')
    setTimeout(() => {
      setGenerating(false)
      router.push('/review')
    }, 2000)
  }

  const statusColor: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    approved: 'bg-blue-100 text-blue-700',
    published: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-50">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
            <p className="text-gray-500 text-sm mt-1">
              {stats?.profile?.company_name} · Posts daily at {stats?.profile?.post_hour}:00 {stats?.profile?.post_timezone}
            </p>
          </div>
          <button onClick={generateNow} disabled={generating}
            className="bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50">
            {generating ? 'Generating...' : '⚡ Generate Today\'s Post'}
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Posts', value: stats?.stats?.total_posts ?? '—' },
            { label: 'Published', value: stats?.stats?.published ?? '—' },
            { label: 'Pending Review', value: stats?.stats?.pending_review ?? '—' },
            { label: 'Rejected', value: stats?.stats?.rejected ?? '—' },
          ].map((s) => (
            <div key={s.label} className="bg-white rounded-xl p-5 shadow-sm border">
              <p className="text-sm text-gray-500">{s.label}</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">{s.value}</p>
            </div>
          ))}
        </div>

        {/* Recent Posts */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="font-semibold text-gray-700 mb-4">Recent Posts</h3>
          {stats?.recent_posts?.length === 0 && (
            <p className="text-gray-400 text-sm">No posts yet. Click "Generate Today's Post" to start.</p>
          )}
          <div className="space-y-3">
            {stats?.recent_posts?.map((p: any) => (
              <div key={p.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="text-sm text-gray-700">{p.topic}</span>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor[p.status] || 'bg-gray-100 text-gray-500'}`}>
                  {p.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
