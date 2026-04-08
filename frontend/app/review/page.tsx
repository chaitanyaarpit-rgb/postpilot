'use client'
import { useEffect, useState } from 'react'
import Sidebar from '@/components/Sidebar'
import api from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { Check, X, Edit2 } from 'lucide-react'

export default function ReviewPage() {
  const [posts, setPosts] = useState<any[]>([])
  const [editing, setEditing] = useState<number | null>(null)
  const [editCaption, setEditCaption] = useState('')
  const { token } = useAuthStore()
  const router = useRouter()

  const load = () => api.get('/api/posts/?status=pending').then((r) => setPosts(r.data))

  useEffect(() => {
    if (!token) { router.push('/login'); return }
    load()
  }, [token])

  const approve = async (id: number) => {
    await api.post(`/api/posts/${id}/approve`)
    load()
  }

  const reject = async (id: number) => {
    await api.post(`/api/posts/${id}/reject`)
    load()
  }

  const saveEdit = async (id: number) => {
    await api.patch(`/api/posts/${id}`, { caption: editCaption })
    setEditing(null)
    load()
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-50">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Review Queue</h2>
        <p className="text-gray-500 text-sm mb-6">Approve, edit, or reject posts before they go live.</p>

        {posts.length === 0 && (
          <div className="bg-white rounded-xl border p-12 text-center text-gray-400">
            No posts pending review. Generate today's post from the dashboard.
          </div>
        )}

        <div className="space-y-6">
          {posts.map((post) => (
            <div key={post.id} className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <span className="text-xs font-medium bg-indigo-50 text-indigo-600 px-2 py-1 rounded-full">
                    {post.content_type}
                  </span>
                  <h3 className="font-semibold text-gray-800 mt-2">{post.topic}</h3>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => { setEditing(post.id); setEditCaption(post.caption) }}
                    className="p-2 rounded-lg border hover:bg-gray-50 text-gray-500">
                    <Edit2 size={16} />
                  </button>
                  <button onClick={() => approve(post.id)}
                    className="p-2 rounded-lg bg-green-50 hover:bg-green-100 text-green-600 border border-green-200">
                    <Check size={16} />
                  </button>
                  <button onClick={() => reject(post.id)}
                    className="p-2 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 border border-red-200">
                    <X size={16} />
                  </button>
                </div>
              </div>

              {/* Image preview */}
              {post.image_paths?.[0] && (
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/${post.image_paths[0]}`}
                  alt="Post visual"
                  className="w-full max-h-64 object-cover rounded-lg mb-4"
                />
              )}

              {/* Caption */}
              {editing === post.id ? (
                <div>
                  <textarea value={editCaption} onChange={(e) => setEditCaption(e.target.value)}
                    rows={6}
                    className="w-full border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  <div className="flex gap-2 mt-2">
                    <button onClick={() => saveEdit(post.id)}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium">Save</button>
                    <button onClick={() => setEditing(null)}
                      className="border px-4 py-2 rounded-lg text-sm text-gray-600">Cancel</button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{post.caption}</p>
              )}

              <p className="text-xs text-indigo-500 mt-3">{post.hashtags}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
