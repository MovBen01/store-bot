import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

const DEFAULTS = {
  design_accent_color: '#f97316',
  design_bg_color: '#0a0a0a',
  design_store_name: 'Apple Store',
  design_hero_title: 'iPhone 16 Pro\nУже в наличии',
  design_hero_subtitle: 'Титановый корпус. Чип A18 Pro.',
  design_support_text: 'По всем вопросам: @support_username',
  design_show_hero: '1',
}

const ACCENT_PRESETS = ['#f97316','#3b82f6','#22c55e','#ef4444','#a855f7','#ec4899','#14b8a6','#f59e0b','#ffffff']
const BG_PRESETS = ['#0a0a0a','#0f172a','#0c0c0c','#111827','#1e1b4b','#042f2e']

export default function DesignPage() {
  const [form, setForm] = useState(DEFAULTS)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    adminApi.getDesign().then(d => { setForm({ ...DEFAULTS, ...d }); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))
  const showToast = (msg, type = 'success') => { setToast({ msg, type }); setTimeout(() => setToast(null), 3500) }

  const save = async () => {
    setSaving(true)
    try {
      await adminApi.updateDesign(form)
      showToast('Дизайн сохранён ✓ Пересоберите webapp и задеплойте для применения')
    } catch (e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  if (loading) return <div className="loading-center"><div className="spinner" /></div>

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="page-title">🎨 Дизайн магазина</div>

      {/* Live preview */}
      <div style={{ background: form.design_bg_color, borderRadius: 14, padding: '0', marginBottom: 24, border: '1px solid #2a2a2a', overflow: 'hidden' }}>
        <div style={{ background: form.design_bg_color + 'ee', backdropFilter: 'blur(20px)', padding: '12px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #2a2a2a22' }}>
          <div style={{ fontWeight: 900, fontSize: 18, color: form.design_accent_color }}>🍎 {form.design_store_name}</div>
          <div style={{ fontSize: 20 }}>🛒</div>
        </div>
        {form.design_show_hero === '1' && (
          <div style={{ background: 'linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)', padding: '24px 20px', margin: 12, borderRadius: 16 }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 2, color: form.design_accent_color, marginBottom: 6 }}>НОВИНКИ 2025</div>
            <div style={{ fontWeight: 900, fontSize: 20, whiteSpace: 'pre-line', marginBottom: 6, color: '#fff' }}>{form.design_hero_title}</div>
            <div style={{ fontSize: 12, color: '#86868b', marginBottom: 14 }}>{form.design_hero_subtitle}</div>
            <div style={{ display: 'inline-flex', background: form.design_accent_color, color: '#fff', padding: '8px 16px', borderRadius: 50, fontSize: 12, fontWeight: 700 }}>Смотреть →</div>
          </div>
        )}
        <div style={{ padding: '4px 12px 12px', display: 'flex', gap: 8 }}>
          {['Все','iPhone','MacBook','iPad'].map((cat, i) => (
            <div key={cat} style={{ padding: '6px 14px', borderRadius: 50, background: i === 0 ? form.design_accent_color : '#1e1e1e', color: i === 0 ? '#fff' : '#888', fontSize: 12, fontWeight: 600 }}>{cat}</div>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

        {/* Colors */}
        <div className="card">
          <div className="card-title">Цвета</div>
          <div className="form-row">
            <label className="form-label">Акцентный цвет (кнопки, цены)</label>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
              <input type="color" value={form.design_accent_color} onChange={e => set('design_accent_color', e.target.value)}
                style={{ width: 44, height: 44, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 2, background: 'none' }} />
              <input className="form-input" value={form.design_accent_color} onChange={e => set('design_accent_color', e.target.value)} placeholder="#f97316" />
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {ACCENT_PRESETS.map(c => (
                <button key={c} onClick={() => set('design_accent_color', c)}
                  style={{ width: 28, height: 28, borderRadius: 6, background: c, border: form.design_accent_color === c ? '3px solid #fff' : '1px solid #333', cursor: 'pointer' }} />
              ))}
            </div>
          </div>
          <div className="form-row">
            <label className="form-label">Цвет фона</label>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
              <input type="color" value={form.design_bg_color} onChange={e => set('design_bg_color', e.target.value)}
                style={{ width: 44, height: 44, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 2, background: 'none' }} />
              <input className="form-input" value={form.design_bg_color} onChange={e => set('design_bg_color', e.target.value)} placeholder="#0a0a0a" />
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {BG_PRESETS.map(c => (
                <button key={c} onClick={() => set('design_bg_color', c)}
                  style={{ width: 28, height: 28, borderRadius: 6, background: c, border: form.design_bg_color === c ? '3px solid #f97316' : '1px solid #444', cursor: 'pointer' }} />
              ))}
            </div>
          </div>
        </div>

        {/* Texts */}
        <div className="card">
          <div className="card-title">Название и текст</div>
          <div className="form-row">
            <label className="form-label">Название магазина (шапка)</label>
            <input className="form-input" value={form.design_store_name} onChange={e => set('design_store_name', e.target.value)} placeholder="Apple Store" />
          </div>
          <div className="form-row">
            <label className="form-label">Контакт поддержки (FAQ)</label>
            <input className="form-input" value={form.design_support_text} onChange={e => set('design_support_text', e.target.value)} placeholder="@support_username" />
          </div>
        </div>

        {/* Hero */}
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <div className="card-title">Главный баннер</div>
          <div className="form-row flex gap-2" style={{ alignItems: 'center', marginBottom: 16 }}>
            <label className="toggle">
              <input type="checkbox" checked={form.design_show_hero === '1'} onChange={e => set('design_show_hero', e.target.checked ? '1' : '0')} />
              <span className="toggle-slider" />
            </label>
            <span style={{ fontSize: 13 }}>Показывать баннер на главной странице</span>
          </div>
          {form.design_show_hero === '1' && (
            <div className="form-grid">
              <div className="form-row">
                <label className="form-label">Заголовок баннера</label>
                <textarea className="form-textarea" rows={2} value={form.design_hero_title} onChange={e => set('design_hero_title', e.target.value)} placeholder="iPhone 16 Pro&#10;Уже в наличии" />
                <div className="text-muted text-sm" style={{ marginTop: 4 }}>Перенос строки = новая строка в заголовке</div>
              </div>
              <div className="form-row">
                <label className="form-label">Подзаголовок баннера</label>
                <textarea className="form-textarea" rows={2} value={form.design_hero_subtitle} onChange={e => set('design_hero_subtitle', e.target.value)} placeholder="Описание акции..." />
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 16 }}>
        <button className="btn btn-primary" style={{ padding: '12px 32px', fontSize: 15 }} onClick={save} disabled={saving}>
          {saving ? 'Сохраняем...' : '💾 Сохранить дизайн'}
        </button>
        <span className="text-muted text-sm">После сохранения пересоберите webapp: npm run build → git push</span>
      </div>
    </>
  )
}
