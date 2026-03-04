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

function applyDesign(design) {
  if (!design) return
  const r = document.documentElement.style
  if (design.design_accent_color) r.setProperty('--accent2', design.design_accent_color)
  if (design.design_bg_color) r.setProperty('--bg', design.design_bg_color)
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
    ]).finally(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const fn = search.length > 1 ? api.searchProducts(search) : api.getProducts(activeCat)
    fn.then(d => { setProducts(d); setLoading(false) }).catch(() => setLoading(false))
  }, [activeCat, search])

  const storeName = design.design_store_name || 'Apple Store'
  const heroTitle = design.design_hero_title || 'iPhone 16 Pro\nУже в наличии'
  const heroSub = design.design_hero_subtitle || 'Титановый корпус. Чип A18 Pro.'
  const showHero = design.design_show_hero !== '0'

  return (
    <div className="page">
      <div className="header">
        <div className="header-logo">🍎 {storeName}</div>
        <button className="cart-btn" onClick={() => go('cart')}>
          🛒
          {cart.count > 0 && <span className="cart-count">{cart.count}</span>}
        </button>
      </div>

      {showHero && !search && !activeCat && (
        <div className="hero fade-up">
          <div className="hero-label">НОВИНКИ 2025</div>
          <div className="hero-title" style={{whiteSpace:'pre-line'}}>{heroTitle}</div>
          <div className="hero-sub">{heroSub}</div>
          <button className="hero-btn" onClick={() => setActiveCat(cats[0]?.id)}>
            Смотреть <span>→</span>
          </button>
        </div>
      )}

      <div className="search-bar">
        <span className="search-icon">🔍</span>
        <input className="search-input" placeholder="Поиск товаров..."
          value={search} onChange={e => { setSearch(e.target.value); setActiveCat(null) }} />
        {search && <button onClick={() => setSearch('')} style={{color:'var(--text3)',fontSize:18}}>×</button>}
      </div>

      {!search && (
        <div className="cat-scroll">
          <button className={`cat-chip${activeCat === null ? ' active' : ''}`} onClick={() => setActiveCat(null)}>Все</button>
          {cats.map(c => (
            <button key={c.id} className={`cat-chip${activeCat === c.id ? ' active' : ''}`} onClick={() => setActiveCat(c.id)}>
              {c.image_url
                ? <img src={c.image_url} alt="" style={{width:18,height:18,objectFit:'cover',borderRadius:4}} onError={e => e.target.style.display='none'} />
                : c.emoji} {c.name}
            </button>
          ))}
        </div>
      )}

      <div className="section">
        <div className="section-header">
          <div className="section-title">
            {search ? `Результаты: "${search}"` : activeCat ? cats.find(c=>c.id===activeCat)?.name : 'Все товары'}
          </div>
          {!loading && <div className="section-all">{products.length} шт.</div>}
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"/></div>
        ) : products.length === 0 ? (
          <div style={{textAlign:'center',padding:'40px',color:'var(--text2)'}}>
            <div style={{fontSize:48,marginBottom:12}}>🔍</div>
            <div>Ничего не найдено</div>
          </div>
        ) : (
          <div className="products-grid">
            {products.map((p, i) => (
              <div key={p.id} className="product-card fade-up" style={{animationDelay:`${i*0.04}s`}}
                onClick={() => go('product', { id: p.id })}>
                <div className="product-img">
                  {p.image_url
                    ? <img src={p.image_url} alt={p.name}
                        style={{width:'100%',height:'100%',objectFit:'contain',padding:8}}
                        onError={e => { e.target.style.display='none'; e.target.parentNode.innerHTML += '<span style="font-size:52px">'+EMOJI(p.name)+'</span>' }} />
                    : EMOJI(p.name)
                  }
                  {i < 3 && <span className="product-img-badge">ХИТ</span>}
                </div>
                <div className="product-info">
                  <div className="product-name">{p.name}</div>
                  <div className="product-price">{fmt(p.display_price)}</div>
                  <button className="product-add"
                    onClick={e => { e.stopPropagation(); cart.add(p) }}
                    style={cart.inCart(p.id) ? {background:'var(--green)'} : {}}>
                    {cart.inCart(p.id) ? '✓' : '+'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
