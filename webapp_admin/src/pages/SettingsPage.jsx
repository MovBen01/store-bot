import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

export default function SettingsPage() {
  const [form, setForm] = useState({ markup_mode: 'percent', markup_value: '10' })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    adminApi.getSettings().then(d => { setForm(d); setLoading(false) })
  }, [])

  const showToast = (msg, type='success') => { setToast({msg,type}); setTimeout(() => setToast(null), 3000) }

  const save = async () => {
    setSaving(true)
    try {
      await adminApi.updateSettings(form)
      showToast('Настройки сохранены ✓')
    } catch(e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  if (loading) return <div className="loading-center"><div className="spinner"/></div>

  const unit = form.markup_mode === 'percent' ? '%' : '₽'

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="page-title">Настройки</div>

      <div className="card" style={{maxWidth:480}}>
        <div className="card-title">Наценка на товары</div>
        <div className="form-row">
          <label className="form-label">Режим наценки</label>
          <div className="flex gap-2">
            {[['percent','Процент (%)'],['fixed','Фиксированная (₽)']].map(([v,l]) => (
              <button key={v}
                className={'btn ' + (form.markup_mode===v ? 'btn-primary' : 'btn-ghost')}
                onClick={() => setForm(f => ({...f, markup_mode: v}))}>
                {l}
              </button>
            ))}
          </div>
        </div>
        <div className="form-row">
          <label className="form-label">Значение наценки ({unit})</label>
          <input className="form-input" type="number" min="0" max="10000"
            value={form.markup_value}
            onChange={e => setForm(f => ({...f, markup_value: e.target.value}))}
            placeholder="10" style={{maxWidth:200}} />
          <div className="text-muted text-sm" style={{marginTop:6}}>
            {form.markup_mode === 'percent'
              ? `Товар за 90 000 ₽ → ${Math.round(90000 * (1 + Number(form.markup_value)/100)).toLocaleString('ru-RU')} ₽`
              : `Товар за 90 000 ₽ → ${(90000 + Number(form.markup_value)).toLocaleString('ru-RU')} ₽`}
          </div>
        </div>
        <button className="btn btn-primary" onClick={save} disabled={saving}>
          {saving ? 'Сохраняем...' : 'Сохранить настройки'}
        </button>
      </div>
    </>
  )
}
