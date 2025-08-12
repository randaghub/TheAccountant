import { useState } from 'react'

export default function Home() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('Idle')
  const [links, setLinks] = useState(null)

  const go = async () => {
    if (!file) return alert('Choose a CSV or PDF')
    setStatus('Uploading...')
    const fd = new FormData()
    fd.append('file', file)
    const u = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/api/v1/upload', { method:'POST', body: fd })
    if (!u.ok) return setStatus('Upload failed')
    const { file_id } = await u.json()
    setStatus('Processing...')
    const p = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/api/v1/process', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ file_id, client_id:'DEMO' })
    })
    if (!p.ok) return setStatus('Processing failed')
    const { downloads } = await p.json()
    setLinks(downloads); setStatus('Done')
  }

  return (
    <main style={{maxWidth:780, margin:'40px auto', fontFamily:'Inter, Arial'}}>
      <h1>The Accountant</h1>
      <p>Upload your bank statement (CSV/PDF) and download Excel + PDF financials.</p>
      <input type='file' accept='.csv,.pdf' onChange={e=>setFile(e.target.files?.[0])} />
      <button onClick={go} style={{marginLeft:12}}>Generate</button>
      <p>Status: {status}</p>
      {links && <ul>
        <li><a href={links['raw.csv']} target='_blank'>raw.csv</a></li>
        <li><a href={links['financials.xlsx']} target='_blank'>financials.xlsx</a></li>
        <li><a href={links['executive_summary.pdf']} target='_blank'>executive_summary.pdf</a></li>
      </ul>}
    </main>
  )
}
