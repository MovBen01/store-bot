import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

const EMPTY = { name: '', sku: '', description: '', base_price: '', category_id: '', visible: true, image_url: '', specs: [] }

function ImgUpload({ value, onChange }) {
  const [uploading, setUploading] = useState(false)
  const [err, setErr] = useState('')

  const handleFile = async (e) => {
    const file = e.target.files?.[0]; if (!file) return
    const cloud = localStorage.getItem('cloudinary_cloud') || ''
    const preset = localStorage.getItem('cloudinary_preset') || 'ml_default'
    if (!cloud) { setErr('Настройте Cloudinary в разделе Настройки'); return }
    setUploading(true); setErr('')
    try {
      const fd = new FormData(); fd.append('file', file); fd.append('upload_preset', preset)
      const res = await fetch(`https://api.cloudinary.com/v1_1/${cloud}/image/upload`, { method: 'POST', body: fd })
      const data = await res.json()
      if (data.error) throw new Error(data.error.message)
      onChange(data.secure_url)
    } catch(e) { setErr('Ошибка: ' + e.message) }
    finally { setUploading(false) }
  }

  return (
    <div>
      {value && (
        <div style={{ marginBottom: 10, position: 'relative', display: 'inline-block' }}>
          <img src={value} alt="" style={{ width: 100, height: 100, objectFit: 'contain', borderRadius: 10, background: '#1e1e1e', padding: 4, border: '1px solid #2a2a2a' }} onError={e => e.target.src=''} />
          <button onClick={() => onChange('')} style={{ position: 'absolute', top: -6, right: -6, width: 22, height: 22, borderRadius: '50%', background: '#ef4444', color: '#fff', fontSize: 14, border: 'none', cursor: 'pointer' }}>×</button>
        </div>
      )}
      <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
        <input className="form-input" value={value} onChange={e => onChange(e.target.value)} placeholder="https://i.imgur.com/abc123.jpg" />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <label style={{ cursor: 'pointer' }}>
          <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFile} />
          <span className="btn btn-ghost btn-sm">{uploading ? '⏳ Загрузка...' : '📁 Загрузить файл'}</span>
        </label>
        <span className="text-muted text-sm">через Cloudinary</span>
      </div>
      {err && <div style={{ color: 'var(--red)', fontSize: 12, marginTop: 6 }}>{err}</div>}
    </div>
  )
}

function SpecsEditor({ specs, onChange }) {
  const add = () => onChange([...specs, { key: '', value: '', highlight: false }])
  const remove = (i) => onChange(specs.filter((_, j) => j !== i))
  const update = (i, field, val) => onChange(specs.map((s, j) => j === i ? { ...s, [field]: val } : s))
  const move = (i, dir) => {
    const arr = [...specs]
    const j = i + dir
    if (j < 0 || j >= arr.length) return
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
    onChange(arr)
  }

  return (
    <div>
      {specs.map((s, i) => (
        <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 8, alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <button className="btn btn-ghost" style={{ padding: '2px 6px', fontSize: 10 }} onClick={() => move(i, -1)}>↑</button>
            <button className="btn btn-ghost" style={{ padding: '2px 6px', fontSize: 10 }} onClick={() => move(i, 1)}>↓</button>
          </div>
          <input className="form-input" value={s.key} onChange={e => update(i, 'key', e.target.value)} placeholder="Характеристика" style={{ flex: 1 }} />
          <input className="form-input" value={s.value} onChange={e => update(i, 'value', e.target.value)} placeholder="Значение" style={{ flex: 1 }} />
          <label title="Выделить цветом" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: s.highlight ? 'var(--accent)' : 'var(--text2)', flexShrink: 0 }}>
            <input type="checkbox" checked={!!s.highlight} onChange={e => update(i, 'highlight', e.target.checked)} style={{ accentColor: 'var(--accent)' }} />
            🎨
          </label>
          <button className="btn btn-danger btn-sm" onClick={() => remove(i)} style={{ flexShrink: 0 }}>✕</button>
        </div>
      ))}
      <button className="btn btn-ghost btn-sm" onClick={add}>+ Добавить характеристику</button>
      {specs.length > 0 && <div className="text-muted text-sm" style={{ marginTop: 6 }}>🎨 — выделить значение акцентным цветом</div>}
    </div>
  )
}

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [tab, setTab] = useState('main')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  const load = async () => {
    setLoading(true)
    const [p, c] = await Promise.all([adminApi.getProducts(), adminApi.getCategories()])
    setProducts(p); setCategories(c); setLoading(false)
  }
  useEffect(() => { load() }, [])

  const showToast = (msg, type = 'success') => { setToast({ msg, type }); setTimeout(() => setToast(null), 3500) }
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const openEdit = (p) => {
    let specs = []
    try { specs = JSON.parse(p.specs || '[]') } catch {}
    setForm({ ...p, visible: !!p.visible, image_url: p.image_url || '', specs })
    setTab('main'); setModal(p)
  }

  const save = async () => {
    if (!form.name || !form.base_price || !form.category_id) { showToast('Заполните обязательные поля', 'error'); return }
    setSaving(true)
    try {
      const data = { ...form, base_price: parseFloat(form.base_price), visible: form.visible ? 1 : 0, specs: JSON.stringify(form.specs) }
      if (!data.sku) data.sku = form.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').slice(0, 30) + '-' + Date.now()
      if (modal === 'create') await adminApi.createProduct(data)
      else await adminApi.updateProduct(modal.id, data)
      showToast(modal === 'create' ? 'Товар создан ✓' : 'Сохранено ✓')
      setModal(null); load()
    } catch (e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Удалить товар?')) return
    await adminApi.deleteProduct(id); showToast('Удалено'); load()
  }

  const toggleVisible = async (p) => {
    await adminApi.updateProduct(p.id, { ...p, visible: p.visible ? 0 : 1, image_url: p.image_url || '', specs: p.specs || '[]' }); load()
  }

  const fmt = n => Number(n).toLocaleString('ru-RU') + ' ₽'
  const catName = id => categories.find(c => c.id == id)?.name || '—'

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="flex-between mb-4">
        <div className="page-title" style={{ margin: 0 }}>Товары</div>
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY); setTab('main'); setModal('create') }}>+ Добавить товар</button>
      </div>

      {loading ? <div className="loading-center"><div className="spinner" /></div> : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Фото</th><th>Название</th><th>Категория</th><th>Цена</th><th>Хар-ки</th><th>Видимость</th><th>Действия</th></tr></thead>
              <tbody>
                {products.map(p => {
                  let specsCount = 0
                  try { specsCount = JSON.parse(p.specs || '[]').length } catch {}
                  return (
                    <tr key={p.id}>
                      <td>
                        {p.image_url
                          ? <img src={p.image_url} alt="" style={{ width: 44, height: 44, objectFit: 'cover', borderRadius: 8 }} onError={e => e.target.style.display = 'none'} />
                          : <div style={{ width: 44, height: 44, borderRadius: 8, background: '#1e1e1e', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22 }}>📦</div>
                        }
                      </td>
                      <td style={{ fontWeight: 500 }}>{p.name}</td>
                      <td className="text-muted">{catName(p.category_id)}</td>
                      <td style={{ color: 'var(--accent)', fontWeight: 600 }}>{fmt(p.base_price)}</td>
                      <td className="text-muted text-sm">{specsCount > 0 ? `${specsCount} полей` : <span style={{color:'var(--text3)'}}>—</span>}</td>
                      <td>
                        <label className="toggle">
                          <input type="checkbox" checked={!!p.visible} onChange={() => toggleVisible(p)} />
                          <span className="toggle-slider" />
                        </label>
                      </td>
                      <td>
                        <div className="actions">
                          <button className="btn btn-ghost btn-sm" onClick={() => openEdit(p)}>✏️ Изменить</button>
                          <button className="btn btn-danger btn-sm" onClick={() => del(p.id)}>🗑</button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className="modal" style={{ maxWidth: 580 }}>
            <div className="modal-title">
              {modal === 'create' ? 'Новый товар' : 'Редактировать: ' + form.name}
              <span className="modal-close" onClick={() => setModal(null)}>×</span>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: 4, marginBottom: 20, background: 'var(--bg3)', padding: 4, borderRadius: 8 }}>
              {[['main','📋 Основное'],['photo','📸 Фото'],['specs','📊 Характеристики']].map(([id, label]) => (
                <button key={id} onClick={() => setTab(id)} className="btn"
                  style={{ flex: 1, justifyContent: 'center', fontSize: 12, padding: '6px 8px',
                    background: tab === id ? 'var(--accent)' : 'transparent',
                    color: tab === id ? '#fff' : 'var(--text2)' }}>
                  {label}
                </button>
              ))}
            </div>

            {/* Tab: Main */}
            {tab === 'main' && <>
              <div className="form-row">
                <label className="form-label">Название *</label>
                <input className="form-input" value={form.name} onChange={e => set('name', e.target.value)} placeholder="iPhone 16 Pro 256GB" />
              </div>
              <div className="form-grid">
                <div className="form-row">
                  <label className="form-label">Категория *</label>
                  <select className="form-select" value={form.category_id} onChange={e => set('category_id', e.target.value)}>
                    <option value="">Выберите...</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.emoji} {c.name}</option>)}
                  </select>
                </div>
                <div className="form-row">
                  <label className="form-label">Базовая цена (₽) *</label>
                  <input className="form-input" type="number" value={form.base_price} onChange={e => set('base_price', e.target.value)} placeholder="89990" />
                </div>
              </div>
              <div className="form-row">
                <label className="form-label">Описание</label>
                <textarea className="form-textarea" value={form.description} onChange={e => set('description', e.target.value)} placeholder="Краткое описание товара..." rows={3} />
              </div>
              <div className="form-row">
                <label className="form-label">SKU (оставьте пустым для авто)</label>
                <input className="form-input" value={form.sku} onChange={e => set('sku', e.target.value)} placeholder="iphone16-pro-256" />
              </div>
              <div className="form-row flex gap-2" style={{ alignItems: 'center' }}>
                <label className="toggle">
                  <input type="checkbox" checked={!!form.visible} onChange={e => set('visible', e.target.checked)} />
                  <span className="toggle-slider" />
                </label>
                <span style={{ fontSize: 13 }}>Показывать в каталоге</span>
              </div>
            </>}

            {/* Tab: Photo */}
            {tab === 'photo' && <>
              <div className="form-row">
                <label className="form-label">📸 Фото товара</label>
                <ImgUpload value={form.image_url} onChange={url => set('image_url', url)} />
              </div>
              <div style={{ marginTop: 16, padding: 16, background: 'var(--bg3)', borderRadius: 12 }}>
                <div className="text-muted text-sm" style={{ marginBottom: 8 }}>Предпросмотр карточки:</div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  <div style={{ width: 80, height: 80, background: '#1e1e1e', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', flexShrink: 0 }}>
                    {form.image_url
                      ? <img src={form.image_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'contain', padding: 6 }} onError={e => e.target.style.display='none'} />
                      : <span style={{ fontSize: 36 }}>📦</span>
                    }
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>{form.name || 'Название товара'}</div>
                    <div style={{ color: 'var(--accent)', fontWeight: 700, marginTop: 4 }}>{form.base_price ? Number(form.base_price).toLocaleString('ru-RU') + ' ₽' : '0 ₽'}</div>
                  </div>
                </div>
              </div>
            </>}

            {/* Tab: Specs */}
            {tab === 'specs' && <>
              <div style={{ marginBottom: 12, padding: '10px 14px', background: 'rgba(249,115,22,0.08)', border: '1px solid rgba(249,115,22,0.2)', borderRadius: 8, fontSize: 13, color: '#ccc' }}>
                Характеристики отображаются в карточке товара. Добавьте нужные поля — например: Чип, Камера, Память, Гарантия.
              </div>
              <SpecsEditor specs={form.specs} onChange={v => set('specs', v)} />
            </>}

            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)}>Отмена</button>
              <button className="btn btn-primary" onClick={save} disabled={saving}>{saving ? 'Сохраняем...' : 'Сохранить'}</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
