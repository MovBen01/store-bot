import { useState, useRef } from 'react'

export default function ImageUpload({ value, onChange }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [urlInput, setUrlInput] = useState(value || '')
  const fileRef = useRef()

  const cloudName = localStorage.getItem('cloudinary_cloud') || ''
  const uploadPreset = localStorage.getItem('cloudinary_preset') || 'ml_default'

  const handleFile = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!cloudName) {
      setError('Сначала укажите Cloudinary Cloud Name в разделе Настройки')
      return
    }
    setUploading(true); setError('')
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('upload_preset', uploadPreset)
      const res = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/image/upload`, { method: 'POST', body: fd })
      const data = await res.json()
      if (data.error) throw new Error(data.error.message)
      onChange(data.secure_url)
      setUrlInput(data.secure_url)
    } catch (e) {
      setError('Ошибка загрузки: ' + e.message)
    } finally { setUploading(false) }
  }

  const handleUrl = () => {
    if (urlInput.trim()) { onChange(urlInput.trim()); setError('') }
  }

  return (
    <div>
      {/* Preview */}
      {value && (
        <div style={{ marginBottom: 12, position: 'relative', display: 'inline-block' }}>
          <img src={value} alt=""
            style={{ width: 120, height: 120, objectFit: 'contain', borderRadius: 12, background: '#1e1e1e', padding: 4, border: '1px solid #2a2a2a' }}
            onError={e => e.target.src = ''} />
          <button onClick={() => { onChange(''); setUrlInput('') }}
            style={{ position: 'absolute', top: -6, right: -6, width: 22, height: 22, borderRadius: '50%', background: '#ef4444', color: '#fff', fontSize: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', border: 'none' }}>×</button>
        </div>
      )}

      {/* URL input */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <input className="form-input" value={urlInput}
          onChange={e => setUrlInput(e.target.value)}
          onBlur={handleUrl}
          onKeyDown={e => e.key === 'Enter' && handleUrl()}
          placeholder="https://i.imgur.com/abc123.jpg" />
        <button className="btn btn-ghost" onClick={handleUrl} style={{ flexShrink: 0 }}>Вставить</button>
      </div>

      {/* File upload */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => fileRef.current?.click()} disabled={uploading}>
          {uploading ? '⏳ Загрузка...' : '📁 Загрузить файл'}
        </button>
        <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFile} />
        <span className="text-muted text-sm">через Cloudinary</span>
      </div>

      {error && <div style={{ color: 'var(--red)', fontSize: 12, marginTop: 6 }}>{error}</div>}
    </div>
  )
}
