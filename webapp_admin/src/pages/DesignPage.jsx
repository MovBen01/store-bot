import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'
import ImageUpload from '../components/ImageUpload'

const DEFAULTS = {
  // General
  design_store_name: 'Apple Store',
  design_store_emoji: '🍎',
  design_support_text: 'По всем вопросам: @support_username',
  // Colors
  design_accent_color: '#f97316',
  design_bg_color: '#0a0a0a',
  design_card_color: '#161616',
  design_text_color: '#f5f5f7',
  design_button_radius: '50',
  design_card_radius: '16',
  // Hero banner
  design_show_hero: '1',
  design_hero_title: 'iPhone 16 Pro\nУже в наличии',
  design_hero_subtitle: 'Титановый корпус. Чип A18 Pro.',
  design_hero_label: 'НОВИНКИ 2025',
  design_hero_btn_text: 'Смотреть →',
  design_hero_image: '',
  design_hero_gradient: 'linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)',
  // Banner 2
  design_show_banner2: '0',
  design_banner2_title: 'Специальное предложение',
  design_banner2_subtitle: 'Скидки до 30% на аксессуары',
  design_banner2_image: '',
  design_banner2_btn_text: 'Подробнее',
  design_banner2_gradient: 'linear-gradient(135deg,#0f3460,#533483)',
  // Sections visibility
  design_show_search: '1',
  design_show_categories: '1',
  design_show_hit_badge: '1',
  // Footer
  design_show_footer: '1',
  design_footer_text: 'Официальный дилер Apple. Гарантия 1 год.',
}

const TABS = [
  { id: 'general', label: '🏪 Магазин' },
  { id: 'colors',  label: '🎨 Цвета' },
  { id: 'hero',    label: '🖼 Баннер 1' },
  { id: 'banner2', label: '🖼 Баннер 2' },
  { id: 'sections',label: '📐 Секции' },
]

const ACCENT_PRESETS = ['#f97316','#3b82f6','#22c55e','#ef4444','#a855f7','#ec4899','#14b8a6','#f59e0b','#e11d48','#0ea5e9']
const BG_PRESETS = ['#0a0a0a','#0f172a','#0c0c0c','#111827','#1e1b4b','#042f2e','#1a0a00','#0a0a1a']
const GRADIENT_PRESETS = [
  ['#1a1a2e','#0f3460'],
  ['#0f3460','#533483'],
  ['#1a0a2e','#3d0c6b'],
  ['#0a2e1a','#0c6b3d'],
  ['#2e1a0a','#6b3d0c'],
  ['#0a0a2e','#1a1a6b'],
]

function ColorPicker({ label, value, onChange, presets }) {
  return (
    <div className="form-row">
      <label className="form-label">{label}</label>
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
        <input type="color" value={value} onChange={e => onChange(e.target.value)}
          style={{ width: 44, height: 44, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 2, background: 'none' }} />
        <input className="form-input" value={value} onChange={e => onChange(e.target.value)} style={{ flex: 1 }} />
      </div>
      {presets && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {presets.map(c => (
            <button key={c} onClick={() => onChange(c)}
              style={{ width: 26, height: 26, borderRadius: 6, background: c, border: value === c ? '3px solid #fff' : '1px solid #333', cursor: 'pointer' }} />
          ))}
        </div>
      )}
    </div>
  )
}

function Toggle({ label, desc, checked, onChange }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
      <div>
        <div style={{ fontSize: 14, fontWeight: 500 }}>{label}</div>
        {desc && <div className="text-muted text-sm">{desc}</div>}
      </div>
      <label className="toggle">
        <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
        <span className="toggle-slider" />
      </label>
    </div>
  )
}

function Preview({ form }) {
  const heroLines = (form.design_hero_title || '').split('\n')
  return (
    <div style={{ position: 'sticky', top: 20 }}>
      <div className="card-title" style={{ marginBottom: 12 }}>📱 Превью магазина</div>
      <div style={{
        width: '100%', maxWidth: 280, margin: '0 auto',
        background: form.design_bg_color, borderRadius: 24,
        border: '2px solid #333', overflow: 'hidden',
        fontFamily: '-apple-system, sans-serif', fontSize: 12,
        boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
      }}>
        {/* Header */}
        <div style={{ background: form.design_bg_color + 'ee', padding: '10px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #ffffff11' }}>
          <div style={{ fontWeight: 900, fontSize: 14, color: form.design_accent_color }}>{form.design_store_emoji} {form.design_store_name}</div>
          <div>🛒</div>
        </div>

        {/* Hero */}
        {form.design_show_hero === '1' && (
          <div style={{ margin: 8, borderRadius: 14, overflow: 'hidden', position: 'relative',
            background: form.design_hero_image ? `url(${form.design_hero_image}) center/cover` : form.design_hero_gradient }}>
            {form.design_hero_image && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.45)' }} />}
            <div style={{ padding: '14px 12px', position: 'relative' }}>
              <div style={{ fontSize: 8, fontWeight: 700, letterSpacing: 1.5, color: form.design_accent_color, marginBottom: 4 }}>{form.design_hero_label}</div>
              <div style={{ fontWeight: 900, fontSize: 13, lineHeight: 1.2, marginBottom: 4, color: '#fff', whiteSpace: 'pre-line' }}>{form.design_hero_title}</div>
              <div style={{ fontSize: 9, color: '#aaa', marginBottom: 10 }}>{form.design_hero_subtitle}</div>
              <div style={{ display: 'inline-flex', background: form.design_accent_color, color: '#fff', padding: '5px 12px', borderRadius: Number(form.design_button_radius) / 2 + 'px', fontSize: 9, fontWeight: 700 }}>
                {form.design_hero_btn_text}
              </div>
            </div>
          </div>
        )}

        {/* Banner 2 */}
        {form.design_show_banner2 === '1' && (
          <div style={{ margin: '0 8px 8px', borderRadius: 14, overflow: 'hidden', position: 'relative',
            background: form.design_banner2_image ? `url(${form.design_banner2_image}) center/cover` : form.design_banner2_gradient }}>
            {form.design_banner2_image && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)' }} />}
            <div style={{ padding: '12px', position: 'relative' }}>
              <div style={{ fontWeight: 700, fontSize: 11, color: '#fff', marginBottom: 2 }}>{form.design_banner2_title}</div>
              <div style={{ fontSize: 9, color: '#ccc', marginBottom: 8 }}>{form.design_banner2_subtitle}</div>
              <div style={{ display: 'inline-flex', background: form.design_accent_color, color: '#fff', padding: '4px 10px', borderRadius: Number(form.design_button_radius) / 2 + 'px', fontSize: 9, fontWeight: 700 }}>
                {form.design_banner2_btn_text}
              </div>
            </div>
          </div>
        )}

        {/* Search */}
        {form.design_show_search === '1' && (
          <div style={{ margin: '0 8px 6px', background: '#1e1e1e', borderRadius: 10, padding: '7px 10px', display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{ fontSize: 11 }}>🔍</span>
            <span style={{ color: '#555', fontSize: 10 }}>Поиск товаров...</span>
          </div>
        )}

        {/* Categories */}
        {form.design_show_categories === '1' && (
          <div style={{ display: 'flex', gap: 5, padding: '0 8px 6px', overflowX: 'hidden' }}>
            {['Все','iPhone','Mac','iPad'].map((c, i) => (
              <div key={c} style={{ padding: '4px 10px', borderRadius: 50, background: i === 0 ? form.design_accent_color : '#1e1e1e', color: i === 0 ? '#fff' : '#888', fontSize: 9, fontWeight: 600, flexShrink: 0 }}>{c}</div>
            ))}
          </div>
        )}

        {/* Products grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, padding: '0 8px 8px' }}>
          {[{name:'iPhone 16 Pro',price:'89 990 ₽'},{name:'MacBook Air M3',price:'129 990 ₽'}].map((p, i) => (
            <div key={i} style={{ background: form.design_card_color, borderRadius: Number(form.design_card_radius) / 2 + 'px', overflow: 'hidden' }}>
              <div style={{ height: 60, background: '#1e1e1e', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, position: 'relative' }}>
                {i === 0 ? '📱' : '💻'}
                {form.design_show_hit_badge === '1' && <div style={{ position: 'absolute', top: 3, right: 3, background: form.design_accent_color, color: '#fff', fontSize: 6, fontWeight: 700, padding: '1px 5px', borderRadius: 50 }}>ХИТ</div>}
              </div>
              <div style={{ padding: '6px 8px' }}>
                <div style={{ fontSize: 9, fontWeight: 600, color: form.design_text_color, marginBottom: 2 }}>{p.name}</div>
                <div style={{ fontSize: 10, fontWeight: 700, color: form.design_accent_color }}>{p.price}</div>
                <div style={{ width: 20, height: 20, borderRadius: '50%', background: form.design_accent_color, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 12, marginTop: 4 }}>+</div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        {form.design_show_footer === '1' && (
          <div style={{ padding: '8px 12px', borderTop: '1px solid #ffffff11', textAlign: 'center', color: '#555', fontSize: 8 }}>
            {form.design_footer_text}
          </div>
        )}
      </div>
    </div>
  )
}

export default function DesignPage() {
  const [form, setForm] = useState(DEFAULTS)
  const [activeTab, setActiveTab] = useState('general')
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
      showToast('Дизайн сохранён ✓ Пересоберите webapp для применения')
    } catch (e) { showToast(e.message, 'error') }
    finally { setSaving(false) }
  }

  const reset = () => { if (confirm('Сбросить дизайн к стандартному?')) { setForm(DEFAULTS) } }

  if (loading) return <div className="loading-center"><div className="spinner" /></div>

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div className="page-title" style={{ margin: 0 }}>🎨 Дизайн магазина</div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-ghost" onClick={reset}>↩ Сброс</button>
          <button className="btn btn-primary" onClick={save} disabled={saving} style={{ padding: '8px 24px' }}>
            {saving ? 'Сохраняем...' : '💾 Сохранить'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20, alignItems: 'start' }}>
        {/* Editor */}
        <div>
          {/* Tabs */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 16, background: 'var(--bg2)', padding: 4, borderRadius: 10, border: '1px solid var(--border)' }}>
            {TABS.map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id)}
                className="btn" style={{ flex: 1, justifyContent: 'center', fontSize: 12,
                  background: activeTab === t.id ? 'var(--accent)' : 'transparent',
                  color: activeTab === t.id ? '#fff' : 'var(--text2)',
                  padding: '7px 8px' }}>
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab: General */}
          {activeTab === 'general' && (
            <div className="card">
              <div className="card-title">Основное</div>
              <div className="form-grid">
                <div className="form-row">
                  <label className="form-label">Название магазина</label>
                  <input className="form-input" value={form.design_store_name} onChange={e => set('design_store_name', e.target.value)} placeholder="Apple Store" />
                </div>
                <div className="form-row">
                  <label className="form-label">Эмодзи логотипа</label>
                  <input className="form-input" value={form.design_store_emoji} onChange={e => set('design_store_emoji', e.target.value)} placeholder="🍎" style={{ fontSize: 22 }} />
                </div>
              </div>
              <div className="form-row">
                <label className="form-label">Текст поддержки (FAQ)</label>
                <input className="form-input" value={form.design_support_text} onChange={e => set('design_support_text', e.target.value)} placeholder="По всем вопросам: @username" />
              </div>
              <div className="form-row">
                <label className="form-label">Текст подвала (Footer)</label>
                <input className="form-input" value={form.design_footer_text} onChange={e => set('design_footer_text', e.target.value)} placeholder="Официальный дилер Apple..." />
              </div>
            </div>
          )}

          {/* Tab: Colors */}
          {activeTab === 'colors' && (
            <div className="card">
              <div className="card-title">Цвета и стиль</div>
              <ColorPicker label="Акцентный цвет (кнопки, цены, ссылки)" value={form.design_accent_color} onChange={v => set('design_accent_color', v)} presets={ACCENT_PRESETS} />
              <ColorPicker label="Цвет фона" value={form.design_bg_color} onChange={v => set('design_bg_color', v)} presets={BG_PRESETS} />
              <ColorPicker label="Цвет карточки товара" value={form.design_card_color} onChange={v => set('design_card_color', v)} />
              <ColorPicker label="Цвет текста" value={form.design_text_color} onChange={v => set('design_text_color', v)} />
              <div className="form-row">
                <label className="form-label">Радиус кнопок: {form.design_button_radius}px</label>
                <input type="range" min="0" max="50" value={form.design_button_radius} onChange={e => set('design_button_radius', e.target.value)}
                  style={{ width: '100%', accentColor: 'var(--accent)' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text3)' }}><span>Квадрат</span><span>Скруглённый</span></div>
              </div>
              <div className="form-row">
                <label className="form-label">Радиус карточек: {form.design_card_radius}px</label>
                <input type="range" min="0" max="32" value={form.design_card_radius} onChange={e => set('design_card_radius', e.target.value)}
                  style={{ width: '100%', accentColor: 'var(--accent)' }} />
              </div>
            </div>
          )}

          {/* Tab: Hero Banner */}
          {activeTab === 'hero' && (
            <div className="card">
              <div className="card-title">Главный баннер</div>
              <Toggle label="Показывать баннер" desc="Большой баннер в верхней части страницы" checked={form.design_show_hero === '1'} onChange={v => set('design_show_hero', v ? '1' : '0')} />

              {form.design_show_hero === '1' && <>
                <div style={{ height: 16 }} />
                <div className="form-row">
                  <label className="form-label">Фоновое изображение баннера (необязательно)</label>
                  <ImageUpload value={form.design_hero_image} onChange={url => set('design_hero_image', url)} />
                  <div className="text-muted text-sm" style={{ marginTop: 4 }}>Если фото не указано — используется градиент</div>
                </div>
                <div className="form-row">
                  <label className="form-label">Градиент фона</label>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
                    {GRADIENT_PRESETS.map(([c1, c2]) => {
                      const g = `linear-gradient(135deg,${c1},${c2})`
                      return (
                        <button key={g} onClick={() => set('design_hero_gradient', g)}
                          style={{ width: 44, height: 28, borderRadius: 8, background: g, border: form.design_hero_gradient === g ? '3px solid #fff' : '1px solid #333', cursor: 'pointer' }} />
                      )
                    })}
                  </div>
                </div>
                <div className="form-row">
                  <label className="form-label">Лейбл над заголовком</label>
                  <input className="form-input" value={form.design_hero_label} onChange={e => set('design_hero_label', e.target.value)} placeholder="НОВИНКИ 2025" />
                </div>
                <div className="form-row">
                  <label className="form-label">Заголовок (Enter = новая строка)</label>
                  <textarea className="form-textarea" rows={2} value={form.design_hero_title} onChange={e => set('design_hero_title', e.target.value)} />
                </div>
                <div className="form-row">
                  <label className="form-label">Подзаголовок</label>
                  <input className="form-input" value={form.design_hero_subtitle} onChange={e => set('design_hero_subtitle', e.target.value)} />
                </div>
                <div className="form-row">
                  <label className="form-label">Текст кнопки</label>
                  <input className="form-input" value={form.design_hero_btn_text} onChange={e => set('design_hero_btn_text', e.target.value)} placeholder="Смотреть →" />
                </div>
              </>}
            </div>
          )}

          {/* Tab: Banner 2 */}
          {activeTab === 'banner2' && (
            <div className="card">
              <div className="card-title">Второй баннер (акция/промо)</div>
              <Toggle label="Показывать второй баннер" desc="Отображается под главным баннером" checked={form.design_show_banner2 === '1'} onChange={v => set('design_show_banner2', v ? '1' : '0')} />

              {form.design_show_banner2 === '1' && <>
                <div style={{ height: 16 }} />
                <div className="form-row">
                  <label className="form-label">Фоновое изображение (необязательно)</label>
                  <ImageUpload value={form.design_banner2_image} onChange={url => set('design_banner2_image', url)} />
                </div>
                <div className="form-row">
                  <label className="form-label">Градиент фона</label>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
                    {GRADIENT_PRESETS.map(([c1, c2]) => {
                      const g = `linear-gradient(135deg,${c1},${c2})`
                      return (
                        <button key={g} onClick={() => set('design_banner2_gradient', g)}
                          style={{ width: 44, height: 28, borderRadius: 8, background: g, border: form.design_banner2_gradient === g ? '3px solid #fff' : '1px solid #333', cursor: 'pointer' }} />
                      )
                    })}
                  </div>
                </div>
                <div className="form-row">
                  <label className="form-label">Заголовок баннера</label>
                  <input className="form-input" value={form.design_banner2_title} onChange={e => set('design_banner2_title', e.target.value)} />
                </div>
                <div className="form-row">
                  <label className="form-label">Подзаголовок</label>
                  <input className="form-input" value={form.design_banner2_subtitle} onChange={e => set('design_banner2_subtitle', e.target.value)} />
                </div>
                <div className="form-row">
                  <label className="form-label">Текст кнопки</label>
                  <input className="form-input" value={form.design_banner2_btn_text} onChange={e => set('design_banner2_btn_text', e.target.value)} />
                </div>
              </>}
            </div>
          )}

          {/* Tab: Sections */}
          {activeTab === 'sections' && (
            <div className="card">
              <div className="card-title">Видимость секций</div>
              <Toggle label="🔍 Строка поиска" desc="Поиск по каталогу" checked={form.design_show_search === '1'} onChange={v => set('design_show_search', v ? '1' : '0')} />
              <Toggle label="🗂 Категории" desc="Горизонтальный список категорий" checked={form.design_show_categories === '1'} onChange={v => set('design_show_categories', v ? '1' : '0')} />
              <Toggle label="🏆 Бейдж ХИТ" desc="Отображать метку «ХИТ» на первых товарах" checked={form.design_show_hit_badge === '1'} onChange={v => set('design_show_hit_badge', v ? '1' : '0')} />
              <Toggle label="📝 Подвал (Footer)" desc="Текст внизу страницы магазина" checked={form.design_show_footer === '1'} onChange={v => set('design_show_footer', v ? '1' : '0')} />
            </div>
          )}

          <button className="btn btn-primary" onClick={save} disabled={saving}
            style={{ marginTop: 16, width: '100%', justifyContent: 'center', padding: 14, fontSize: 15 }}>
            {saving ? 'Сохраняем...' : '💾 Сохранить дизайн'}
          </button>
          <div className="text-muted text-sm" style={{ textAlign: 'center', marginTop: 8 }}>
            После сохранения: пересоберите webapp → npm run build → git push
          </div>
        </div>

        {/* Preview */}
        <Preview form={form} />
      </div>
    </>
  )
}
