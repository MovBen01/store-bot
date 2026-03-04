import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

const EMPTY = { name: '', emoji: '📦', sort_order: 0, visible: true }

export default function CategoriesPage() {
  const [cats, setCats] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)

  const load = () => adminApi.getCategories().then(setCats)
  useEffect(() => { load() }, [])

  const showToast = (msg, type='success') => { setToast({msg,type}); setTimeout(() => setToast(null), 3000) }
  const set = (k, v) => setForm(f => ({...f, [k]: v}))

  const save = async () => {
    if (!form.name) { showToast('Введите название', 'error'); return }
    setSaving(true)
    try {
      const data = { ...form, sort_order: parseInt(form.sort_order) || 0, visible: form.visible ? 1 : 0 }
      if (modal === 'create') await adminApi.createCategory(data)
      else await adminApi.updateCategory(modal.id, data)
      showToast('Сохранено ✓'); setModal(null); load()
    } catch(e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  const del = async (id) => {
    if (!confirm('Удалить категорию? Товары в ней останутся.')) return
    await adminApi.deleteCategory(id); showToast('Удалено'); load()
  }

  const toggle = async (c) => {
    await adminApi.updateCategory(c.id, {...c, visible: c.visible ? 0 : 1}); load()
  }

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="flex-between mb-4">
        <div className="page-title" style={{margin:0}}>Категории</div>
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY); setModal('create') }}>+ Добавить</button>
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Категория</th><th>Порядок</th><th>Видимость</th><th>Действия</th></tr></thead>
            <tbody>
              {cats.map(c => (
                <tr key={c.id}>
                  <td><span style={{fontSize:18,marginRight:8}}>{c.emoji}</span>{c.name}</td>
                  <td className="text-muted">{c.sort_order}</td>
                  <td>
                    <label className="toggle">
                      <input type="checkbox" checked={!!c.visible} onChange={() => toggle(c)} />
                      <span className="toggle-slider"/>
                    </label>
                  </td>
                  <td>
                    <div className="actions">
                      <button className="btn btn-ghost btn-sm" onClick={() => { setForm({...c,visible:!!c.visible}); setModal(c) }}>✏️</button>
                      <button className="btn btn-danger btn-sm" onClick={() => del(c.id)}>🗑</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className="modal">
            <div className="modal-title">
              {modal === 'create' ? 'Новая категория' : 'Редактировать'}
              <span className="modal-close" onClick={() => setModal(null)}>×</span>
            </div>
            <div className="form-grid">
              <div className="form-row">
                <label className="form-label">Название *</label>
                <input className="form-input" value={form.name} onChange={e => set('name', e.target.value)} placeholder="iPhone" />
              </div>
              <div className="form-row">
                <label className="form-label">Эмодзи</label>
                <input className="form-input" value={form.emoji} onChange={e => set('emoji', e.target.value)} placeholder="📱" />
              </div>
            </div>
            <div className="form-row">
              <label className="form-label">Порядок сортировки</label>
              <input className="form-input" type="number" value={form.sort_order} onChange={e => set('sort_order', e.target.value)} />
            </div>
            <div className="form-row flex gap-2" style={{alignItems:'center'}}>
              <label className="toggle">
                <input type="checkbox" checked={!!form.visible} onChange={e => set('visible', e.target.checked)} />
                <span className="toggle-slider"/>
              </label>
              <span style={{fontSize:13}}>Показывать</span>
            </div>
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setModal(null)}>Отмена</button>
              <button className="btn btn-primary" onClick={save} disabled={saving}>{saving ? '...' : 'Сохранить'}</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
