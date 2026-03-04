import { useState, useEffect } from 'react'
import { api } from '../api'

const EMOJI = (name) => {
  if (!name) return '📦'
  if (name.includes('iPhone')) return '📱'
  if (name.includes('Mac')) return '💻'
  if (name.includes('iPad')) return '🗂'
  if (name.includes('AirPod')) return '🎧'
  if (name.includes('Watch')) return '⌚'
  return '📦'
}

function fmt(n) { return Number(n).toLocaleString('ru-RU') + ' ₽' }

function applyDesign(d) {
  if (!d) return
  const r = document.documentElement.style
  if (d.design_accent_color) r.setProperty('--accent2', d.design_accent_color)
  if (d.design_bg_color)     r.setProperty('--bg', d.design_bg_color)
  if (d.design_card_color)   r.setProperty('--card', d.design_card_color)
  if (d.design_text_color)   r.setProperty('--text', d.design_text_color)
  if (d.design_button_radius) r.setProperty('--btn-radius', d.design_button_radius + 'px')
  if (d.design_card_radius)   r.setProperty('--radius', d.design_card_radius + 'px')
}

export default function HomePage({ go, cart }) {
  const [cats, setCats] = useState([])
  const [products, setProducts] = useState([])
  const [activeCat, setActiveCat] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [design, setDesign] = useState({})

  useEffect(() => {
    Promise.all([
      api.getCategories().then(setCats),
      fetch('/api/design').then(r => r.json()).then(d => { setDesign(d); applyDesign(d) }).catch(() => {})
    ])
  }, [])

  useEffect(() => {
    setLoading(true)
    const fn = search.length > 1 ? api.searchProducts(search) : api.getProducts(activeCat)
    fn.then(d => { setProducts(d); setLoading(false) }).catch(() => setLoading(false))
  }, [activeCat, search])

  const D = design
  const storeName   = D.design_store_name    || 'Apple Store'
  const storeEmoji  = D.design_store_emoji   || '🍎'
  const showHero    = D.design_show_hero     !== '0'
  const showBanner2 = D.design_show_banner2  === '1'
  const showSearch  = D.design_show_search   !== '0'
  const showCats    = D.design_show_categories !== '0'
  const showHitBadge= D.design_show_hit_badge !== '0'
  const showFooter  = D.design_show_footer   !== '0'
  const accentColor = D.design_accent_color  || '#f97316'
  const btnRadius   = (D.design_button_radius || '50') + 'px'

  return (
    <div className="page">
      {/* Header */}
      <div className="header">
        <div className="header-logo">{storeEmoji} {storeName}</div>
        <button className="cart-btn" onClick={() => go('cart')}>
          🛒
          {cart.count > 0 && <span className="cart-count">{cart.count}</span>}
        </button>
      </div>

      {/* Hero Banner */}
      {showHero && !search && !activeCat && (
        <div className="hero fade-up" style={{
          background: D.design_hero_image
            ? `url(${D.design_hero_image}) center/cover`
            : (D.design_hero_gradient || 'linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)'),
          position: 'relative'
        }}>
          {D.design_hero_image && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.45)', borderRadius: 24 }} />}
          <div style={{ position: 'relative' }}>
            <div className="hero-label">{D.design_hero_label || 'НОВИНКИ 2025'}</div>
            <div className="hero-title" style={{ whiteSpace: 'pre-line' }}>{D.design_hero_title || 'iPhone 16 Pro\nУже в наличии'}</div>
            <div className="hero-sub">{D.design_hero_subtitle || ''}</div>
            <button className="hero-btn" style={{ borderRadius: btnRadius }} onClick={() => setActiveCat(cats[0]?.id)}>
              {D.design_hero_btn_text || 'Смотреть →'}
            </button>
          </div>
        </div>
      )}

      {/* Banner 2 */}
      {showBanner2 && !search && !activeCat && (
        <div className="fade-up" style={{
          margin: '0 16px 12px',
          borderRadius: 20,
          padding: '20px',
          background: D.design_banner2_image
            ? `url(${D.design_banner2_image}) center/cover`
            : (D.design_banner2_gradient || 'linear-gradient(135deg,#0f3460,#533483)'),
          position: 'relative', overflow: 'hidden'
        }}>
          {D.design_banner2_image && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)' }} />}
          <div style={{ position: 'relative' }}>
            <div style={{ fontFamily: 'var(--font)', fontSize: 18, fontWeight: 800, marginBottom: 6 }}>{D.design_banner2_title}</div>
            <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.8)', marginBottom: 14 }}>{D.design_banner2_subtitle}</div>
            <button className="hero-btn" style={{ borderRadius: btnRadius }} onClick={() => go('home')}>
              {D.design_banner2_btn_text || 'Подробнее'}
            </button>
          </div>
        </div>
      )}

      {/* Search */}
      {showSearch && (
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input className="search-input" placeholder="Поиск товаров..."
            value={search} onChange={e => { setSearch(e.target.value); setActiveCat(null) }} />
          {search && <button onClick={() => setSearch('')} style={{ color: 'var(--text3)', fontSize: 18 }}>×</button>}
        </div>
      )}

      {/* Categories */}
      {showCats && !search && (
        <div className="cat-scroll">
          <button className={`cat-chip${activeCat === null ? ' active' : ''}`} onClick={() => setActiveCat(null)}>Все</button>
          {cats.map(c => (
            <button key={c.id} className={`cat-chip${activeCat === c.id ? ' active' : ''}`} onClick={() => setActiveCat(c.id)}>
              {c.image_url
                ? <img src={c.image_url} alt="" style={{ width: 16, height: 16, objectFit: 'cover', borderRadius: 3 }} onError={e => e.target.style.display = 'none'} />
                : c.emoji} {c.name}
            </button>
          ))}
        </div>
      )}

      {/* Products */}
      <div className="section">
        <div className="section-header">
          <div className="section-title">
            {search ? `Результаты: "${search}"` : activeCat ? cats.find(c => c.id === activeCat)?.name : 'Все товары'}
          </div>
          {!loading && <div className="section-all">{products.length} шт.</div>}
        </div>

        {loading ? (
          <div className="loading"><div className="spinner" /></div>
        ) : products.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text2)' }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
            <div>Ничего не найдено</div>
          </div>
        ) : (
          <div className="products-grid">
            {products.map((p, i) => (
              <div key={p.id} className="product-card fade-up" style={{ animationDelay: `${i * 0.04}s` }}
                onClick={() => go('product', { id: p.id })}>
                <div className="product-img">
                  {p.image_url
                    ? <img src={p.image_url} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'contain', padding: 8 }}
                        onError={e => { e.target.style.display = 'none' }} />
                    : EMOJI(p.name)
                  }
                  {showHitBadge && i < 3 && <span className="product-img-badge">ХИТ</span>}
                </div>
                <div className="product-info">
                  <div className="product-name">{p.name}</div>
                  <div className="product-price">{fmt(p.display_price)}</div>
                  <button className="product-add"
                    style={{ borderRadius: '50%', background: cart.inCart(p.id) ? 'var(--green)' : accentColor }}
                    onClick={e => { e.stopPropagation(); cart.add(p) }}>
                    {cart.inCart(p.id) ? '✓' : '+'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {showFooter && (
        <div style={{ textAlign: 'center', padding: '20px 16px', color: 'var(--text3)', fontSize: 12, borderTop: '1px solid var(--border)', marginTop: 16 }}>
          {D.design_footer_text || ''}
        </div>
      )}
    </div>
  )
}
