import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
export default function Home() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('Idle')
  const [links, setLinks] = useState(null)
  const [user, setUser] = useState(null)
  const [email, setEmail] = useState('')
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setUser(data.session?.user || null))
    const { data: sub } = supabase.auth.onAuthStateChange((_e, session) => setUser(session?.user || null))
    return () => sub?.subscription?.unsubscribe()
  }, [])
  const signIn = async () => {
    const { error } = await supabase.auth.signInWithOtp({ email })
    if (error) return alert(error.message)
    alert('Check your email for the magic link.')
  }
  const uploadAndProcess = async () => {
    if (!user) return alert('Please sign in first.')
    if (!file) return alert('Choose a CSV or PDF')
    const token = (await supabase.auth.getSession()).data.session?.access_token
    const headers = { 'Authorization': 'Bearer ' + token }
    setStatus('Uploading...')
    const fd = new FormData()
    fd.append('file', file)
    const up = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/api/v1/upload', { method: 'POST', body: fd, headers })
    if (!up.ok) return setStatus('Upload failed')
    const { file_id } = await up.json()
    setStatus('Processing...')
    const proc = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/api/v1/process', {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id, client_id: 'DEMO' })
    })
    if (!proc.ok) { const t = await proc.text(); return setStatus('Processing failed: ' + t) }
    const { downloads } = await proc.json()
    setLinks(downloads); setStatus('Done')
  }
  return (
    <main style={{maxWidth:780, margin:'40px auto', fontFamily:'Inter, Arial'}}>
      <h1>The Accountant</h1>
      {!user ? (
        <div style={{margin:'20px 0'}}>
          <h3>Sign in</h3>
          <input placeholder='you@email.com' value={email} onChange={e=>setEmail(e.target.value)} />
          <button onClick={signIn} style={{marginLeft:8}}>Send magic link</button>
        </div>
      ) : (<p>Signed in as {user.email}</p>)}
      <input type="file" accept=".csv,.pdf" onChange={e => setFile(e.target.files?.[0])} />
      <button onClick={uploadAndProcess} style={{marginLeft:12}}>Generate Financials</button>
      <p>Status: {status}</p>
      {links && (<div style={{marginTop:20}}>
        <h3>Downloads</h3>
        <ul>
          <li><a href={links['raw.csv']} target="_blank">raw.csv</a></li>
          <li><a href={links['financials.xlsx']} target="_blank">financials.xlsx</a></li>
          <li><a href={links['executive_summary.pdf']} target="_blank">executive_summary.pdf</a></li>
        </ul>
      </div>)}
      <hr/><p style={{color:'#666'}}>Auth + per-org monthly limits. Free tiers supported.</p>
    </main>
  )
}
