import { useState, useEffect } from 'react'
import { api } from '../api'

const EMOJI = { 1: '📱', 2: '💻', 3: '🗂', 4: '🎧', 5: '⌚' }
const CAT_EMOJI = (id, name) => {
  if (name?.includes('iPhone') || name?.includes('Смарт')) return '📱'
  if (name?.includes('Mac')) return '💻'
  if (name?.includes('iPad')) return '🗂'
  if (name?.includes('AirPod')) return '🎧'
  if (name?.includes('Watch')) return '⌚'
  return EMOJI[id] || '📦'
}

function fmt(n) { return Number(n).toLocaleString('ru-RU') + ' ₽' }

export default function HomePage({ go, cart }) {
  const [cats, setCats] = useState([])
  const [products, setProducts] = useState([])
  const [activeCat, setActiveCat] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getCategories().then(d => { setCats(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    setLoading(true)
    const fn = search.length > 1
      ? api.searchProducts(search)
      : api.getProducts(activeCat)
    fn.then(d => { setProducts(d); setLoading(false) }).catch(() => setLoading(false))
  }, [activeCat, search])

  return (
    <div className="page">
      {/* Header */}
      <div className="header">
        <div className="header-logo">🍎 STORE</div>
        <button className="cart-btn" onClick={() => go('cart')}>
          🛒
          {cart.count > 0 && <span className="cart-count">{cart.count}</span>}
        </button>
      </div>

      {/* Hero */}
      {!search && !activeCat && (
        <div className="hero fade-up">
          <div className="hero-label">Новинки 2025</div>
          <div className="hero-title">iPhone 16 Pro<br/>Уже в наличии</div>
          <div className="hero-sub">Титановый корпус. Чип A18 Pro.</div>
          <button className="hero-btn" onClick={() => setActiveCat(1)}>
            Смотреть <span>→</span>
          </button>
        </div>
      )}

      {/* Search */}
      <div className="search-bar">
        <span className="search-icon">🔍</span>
        <input
          className="search-input"
          placeholder="Поиск товаров..."
          value={search}
          onChange={e => { setSearch(e.target.value); setActiveCat(null) }}
        />
        {search && <button onClick={() => setSearch('')} style={{color:'var(--text3)',fontSize:18}}>×</button>}
      </div>

      {/* Categories */}
      {!search && (
        <div className="cat-scroll">
          <button
            className={`cat-chip${activeCat === null ? ' active' : ''}`}
            onClick={() => setActiveCat(null)}
          >Все</button>
          {cats.map(c => (
            <button
              key={c.id}
              className={`cat-chip${activeCat === c.id ? ' active' : ''}`}
              onClick={() => setActiveCat(c.id)}
            >
              {CAT_EMOJI(c.id, c.name)} {c.name}
            </button>
          ))}
        </div>
      )}

      {/* Products */}
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
                  {CAT_EMOJI(p.category_id, p.category_name)}
                  {i < 3 && <span className="product-img-badge">ХИТ</span>}
                </div>
                <div className="product-info">
                  <div className="product-name">{p.name}</div>
                  <div className="product-price">{fmt(p.display_price)}</div>
                  <button
                    className="product-add"
                    onClick={e => { e.stopPropagation(); cart.add(p) }}
                    style={cart.inCart(p.id) ? {background:'var(--green)'} : {}}
                  >
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
