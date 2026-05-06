'use client'

import { supabase } from './lib/supabase'

export default function Home() {
  const handleGithubLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: {
        redirectTo: `${window.location.origin}/dashboard`
      }
    })
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-black">
      <div className="flex flex-col items-center gap-6 p-10 rounded-xl border border-white/10 bg-white/5">
        <h1 className="text-3xl font-bold text-white">Deductra</h1>
        <p className="text-white/50 text-sm">Sign in to continue</p>
        <button
          onClick={handleGithubLogin}
          className="flex items-center gap-3 px-6 py-3 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition"
        >
          Continue with GitHub
        </button>
      </div>
    </main>
  )
}