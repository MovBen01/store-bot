import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

export default function SettingsPage() {
  const [form, setForm] = useState({ markup_mode: 'percent', markup_value: '10' })
  const [cloud, setCloud] = useState({ name: '', preset: 'ml_default' })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    adminApi.getSettings().then(d => { setForm(d); setLoading(false) })
    setCloud({
      name: localStorage.getItem('cloudinary_cloud') || '',
      preset: localStorage.getItem('cloudinary_preset') || 'ml_default'
    })
  }, [])

  const showToast = (msg, type = 'success') => { setToast({ msg, type }); setTimeout(() => setToast(null), 3000) }

  const saveMarkup = async () => {
    setSaving(true)
    try { await adminApi.updateSettings(form); showToast('Наценка сохранена ✓') }
    catch (e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  const saveCloud = () => {
    localStorage.setItem('cloudinary_cloud', cloud.name.trim())
    localStorage.setItem('cloudinary_preset', cloud.preset.trim())
    showToast('Cloudinary настроен ✓')
  }

  if (loading) return <div className="loading-center"><div className="spinner" /></div>

  const unit = form.markup_mode === 'percent' ? '%' : '₽'

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="page-title">Настройки</div>

      {/* Markup */}
      <div className="card" style={{ maxWidth: 500, marginBottom: 20 }}>
        <div className="card-title">Наценка на товары</div>
        <div className="form-row">
          <label className="form-label">Режим наценки</label>
          <div className="flex gap-2">
            {[['percent', 'Процент (%)'], ['fixed', 'Фиксированная (₽)']].map(([v, l]) => (
              <button key={v} className={'btn ' + (form.markup_mode === v ? 'btn-primary' : 'btn-ghost')}
                onClick={() => setForm(f => ({ ...f, markup_mode: v }))}>{l}</button>
            ))}
          </div>
        </div>
        <div className="form-row">
          <label className="form-label">Значение ({unit})</label>
          <input className="form-input" type="number" min="0" value={form.markup_value}
            onChange={e => setForm(f => ({ ...f, markup_value: e.target.value }))}
            style={{ maxWidth: 180 }} />
          <div className="text-muted text-sm" style={{ marginTop: 6 }}>
            {form.markup_mode === 'percent'
              ? `Товар 90 000 ₽ → ${Math.round(90000 * (1 + Number(form.markup_value) / 100)).toLocaleString('ru-RU')} ₽`
              : `Товар 90 000 ₽ → ${(90000 + Number(form.markup_value)).toLocaleString('ru-RU')} ₽`}
          </div>
        </div>
        <button className="btn btn-primary" onClick={saveMarkup} disabled={saving}>
          {saving ? 'Сохраняем...' : 'Сохранить наценку'}
        </button>
      </div>

      {/* Cloudinary */}
      <div className="card" style={{ maxWidth: 500 }}>
        <div className="card-title">☁️ Cloudinary — загрузка фото товаров</div>
        <div style={{ background: 'rgba(249,115,22,0.08)', border: '1px solid rgba(249,115,22,0.25)', borderRadius: 10, padding: '14px 16px', marginBottom: 18, fontSize: 13, lineHeight: 1.7 }}>
          <b style={{ color: '#f97316' }}>Как настроить (бесплатно):</b><br />
          1. Зарегистрируйся на <a href="https://cloudinary.com" target="_blank" rel="noreferrer" style={{ color: '#f97316' }}>cloudinary.com</a><br />
          2. На главной странице скопируй <b>Cloud Name</b><br />
          3. Settings → Upload → <b>Add upload preset</b> → Mode: <b>Unsigned</b> → Save<br />
          4. Скопируй название preset и вставь ниже
        </div>
        <div className="form-row">
          <label className="form-label">Cloud Name</label>
          <input className="form-input" value={cloud.name}
            onChange={e => setCloud(c => ({ ...c, name: e.target.value }))}
            placeholder="например: myshop-abc123" />
        </div>
        <div className="form-row">
          <label className="form-label">Upload Preset (Unsigned)</label>
          <input className="form-input" value={cloud.preset}
            onChange={e => setCloud(c => ({ ...c, preset: e.target.value }))}
            placeholder="например: ml_default" />
        </div>
        <button className="btn btn-primary" onClick={saveCloud}>Сохранить Cloudinary</button>
        <div className="text-muted text-sm" style={{ marginTop: 8 }}>
          {cloud.name ? `✅ Cloudinary настроен: ${cloud.name}` : '⚠️ Не настроен — загрузка файлов недоступна'}
        </div>
      </div>
    </>
  )
}
