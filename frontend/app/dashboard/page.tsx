'use client'

import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

function parseResponse(raw: string) {
  const answerMatch = raw.match(/<ANSWER>([\s\S]*?)<\/ANSWER>/)
  const followUpsMatch = [...raw.matchAll(/<question>([\s\S]*?)<\/question>/g)]
  
  return {
    answer: answerMatch ? answerMatch[1].trim() : raw,
    followUps: followUpsMatch.map(m => m[1].trim())
  }
}

export default function Dashboard() {
  const [user, setUser] = useState<any>(null)
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [followUps, setFollowUps] = useState<string[]>([])
  const [sources, setSources] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
    }
    getUser()
  }, [])

  const handleSearch = async (q?: string) => {
    const searchQuery = q || query
    if (!searchQuery.trim()) return
    setQuery(searchQuery)
    setLoading(true)
    setAnswer('')
    setFollowUps([])
    try {
      const res = await fetch('http://localhost:8000/deductra_ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
      })
      const data = await res.json()
      const parsed = parseResponse(data.answer)
      setAnswer(parsed.answer)
      setFollowUps(parsed.followUps)
      setSources(data.sources)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center bg-black px-4 py-10">
      <div className="w-full max-w-2xl flex flex-col gap-6">
        <h1 className="text-2xl font-bold text-white">Deductra</h1>
        {user && <p className="text-white/40 text-sm">Logged in as {user.email}</p>}

        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Ask anything..."
            className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/30 outline-none"
          />
          <button
            onClick={() => handleSearch()}
            disabled={loading}
            className="px-5 py-3 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition disabled:opacity-50"
          >
            {loading ? '...' : 'Ask'}
          </button>
        </div>

        {answer && (
          <div className="bg-white/5 border border-white/10 rounded-lg p-5 text-white/80 text-sm whitespace-pre-wrap">
            {answer}
          </div>
        )}

        {followUps.length > 0 && (
          <div className="flex flex-col gap-2">
            <p className="text-white/30 text-xs uppercase tracking-wider">Follow-up questions</p>
            {followUps.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSearch(q)}
                className="text-left px-4 py-3 rounded-lg border border-white/10 text-white/60 text-sm hover:bg-white/5 transition"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {sources.length > 0 && (
          <div className="flex flex-col gap-1">
            <p className="text-white/30 text-xs uppercase tracking-wider">Sources</p>
            {sources.map((s, i) => (
              <a key={i} href={s.url} target="_blank" className="text-white/40 text-xs hover:text-white/70 truncate">
                {s.url}
              </a>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}