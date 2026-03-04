import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

const EMPTY = { name: '', sku: '', description: '', base_price: '', category_id: '', visible: true }

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [modal, setModal] = useState(null) // null | 'create' | product obj
  const [form, setForm] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  const load = async () => {
    setLoading(true)
    const [p, c] = await Promise.all([adminApi.getProducts(), adminApi.getCategories()])
    setProducts(p); setCategories(c); setLoading(false)
  }

  useEffect(() => { load() }, [])

  const showToast = (msg, type='success') => { setToast({msg,type}); setTimeout(() => setToast(null), 3000) }

  const openCreate = () => { setForm(EMPTY); setModal('create') }
  const openEdit = (p) => { setForm({...p, base_price: p.base_price, visible: !!p.visible}); setModal(p) }

  const save = async () => {
    if (!form.name || !form.base_price || !form.category_id) { showToast('Заполните обязательные поля', 'error'); return }
    setSaving(true)
    try {
      const data = { ...form, base_price: parseFloat(form.base_price), visible: form.visible ? 1 : 0 }
      if (!data.sku) data.sku = form.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').slice(0, 30) + '-' + Date.now()
      if (modal === 'create') await adminApi.createProduct(data)
      else await adminApi.updateProduct(modal.id, data)
      showToast(modal === 'create' ? 'Товар создан ✓' : 'Сохранено ✓')
      setModal(null); load()
    } catch(e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Удалить товар?')) return
    await adminApi.deleteProduct(id); showToast('Удалено'); load()
  }

  const toggleVisible = async (p) => {
    await adminApi.updateProduct(p.id, { ...p, visible: p.visible ? 0 : 1 }); load()
  }

  const fmt = n => Number(n).toLocaleString('ru-RU') + ' ₽'
  const set = (k, v) => setForm(f => ({...f, [k]: v}))
  const catName = id => categories.find(c => c.id == id)?.name || '—'

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="flex-between mb-4">
        <div className="page-title" style={{margin:0}}>Товары</div>
        <button className="btn btn-primary" onClick={openCreate}>+ Добавить товар</button>
      </div>

      {loading ? <div className="loading-center"><div className="spinner"/></div> : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr>
                <th>Название</th><th>Категория</th><th>Базовая цена</th><th>SKU</th><th>Видимость</th><th>Действия</th>
              </tr></thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.id}>
                    <td style={{fontWeight:500}}>{p.name}</td>
                    <td className="text-muted">{catName(p.category_id)}</td>
                    <td style={{color:'var(--accent)',fontWeight:600}}>{fmt(p.base_price)}</td>
                    <td className="text-muted text-sm">{p.sku}</td>
                    <td>
                      <label className="toggle">
                        <input type="checkbox" checked={!!p.visible} onChange={() => toggleVisible(p)} />
                        <span className="toggle-slider"/>
                      </label>
                    </td>
                    <td>
                      <div className="actions">
                        <button className="btn btn-ghost btn-sm" onClick={() => openEdit(p)}>✏️ Изменить</button>
                        <button className="btn btn-danger btn-sm" onClick={() => del(p.id)}>🗑</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className="modal">
            <div className="modal-title">
              {modal === 'create' ? 'Новый товар' : 'Редактировать товар'}
              <span className="modal-close" onClick={() => setModal(null)}>×</span>
            </div>
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
              <textarea className="form-textarea" value={form.description} onChange={e => set('description', e.target.value)} placeholder="Краткое описание товара..." />
            </div>
            <div className="form-row">
              <label className="form-label">SKU (оставьте пустым для авто)</label>
              <input className="form-input" value={form.sku} onChange={e => set('sku', e.target.value)} placeholder="iphone16-pro-256" />
            </div>
            <div className="form-row flex gap-2" style={{alignItems:'center'}}>
              <label className="toggle">
                <input type="checkbox" checked={!!form.visible} onChange={e => set('visible', e.target.checked)} />
                <span className="toggle-slider"/>
              </label>
              <span style={{fontSize:13}}>Показывать в каталоге</span>
            </div>
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
