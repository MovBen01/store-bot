import { useState, useEffect } from 'react'
import { api } from '../api'

function fmt(n) { return Number(n).toLocaleString('ru-RU') + ' ₽' }

const EMOJI_MAP = (name) => {
  if (!name) return '📦'
  if (name.includes('iPhone')) return '📱'
  if (name.includes('MacBook') || name.includes('Mac')) return '💻'
  if (name.includes('iPad')) return '🗂'
  if (name.includes('AirPods')) return '🎧'
  if (name.includes('Watch')) return '⌚'
  return '📦'
}

export default function ProductPage({ params, go, cart, design = {} }) {
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [qty, setQty] = useState(1)

  useEffect(() => {
    api.getProduct(params.id)
      .then(d => { setProduct(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [params.id])

  if (loading) return <div className="loading"><div className="spinner"/></div>
  if (!product) return <div style={{padding:32,textAlign:'center',color:'var(--text2)'}}>Товар не найден</div>

  const inCart = cart.inCart(product.id)
  const accentColor = design.design_accent_color || '#f97316'
  const btnRadius = (design.design_button_radius || '50') + 'px'

  // Parse specs from JSON string
  let specs = []
  try { specs = JSON.parse(product.specs || '[]') } catch {}

  const handleBuy = () => {
    for (let i = 0; i < qty; i++) cart.add(product)
    go('cart')
  }

  return (
    <div className="detail-page">
      <button className="back-btn" onClick={() => go('home')}>← Назад</button>

      {/* Product image */}
      <div className="detail-img" style={{ background: product.image_url ? '#0a0a0a' : undefined }}>
        {product.image_url
          ? <img src={product.image_url} alt={product.name}
              style={{ width: '100%', height: '100%', objectFit: 'contain', padding: 16 }}
              onError={e => { e.target.style.display = 'none'; e.target.parentNode.querySelector('.fallback-emoji').style.display = 'block' }} />
          : null
        }
        <span className="fallback-emoji" style={{ fontSize: 80, display: product.image_url ? 'none' : 'block' }}>
          {EMOJI_MAP(product.name)}
        </span>
      </div>

      <div className="detail-content">
        <div className="detail-cat">{product.category_name || 'Apple'}</div>
        <div className="detail-name">{product.name}</div>
        <div className="detail-price" style={{ color: accentColor }}>{fmt(product.display_price)}</div>
        {product.description && <div className="detail-desc">{product.description}</div>}

        {/* Dynamic specs from DB */}
        {specs.length > 0 && (
          <div className="detail-specs">
            {specs.map((s, i) => (
              <div key={i} className="spec-row">
                <span className="spec-key">{s.key}</span>
                <span className="spec-val" style={s.highlight ? { color: accentColor } : {}}>{s.value}</span>
              </div>
            ))}
            <div className="spec-row">
              <span className="spec-key">Цена</span>
              <span className="spec-val" style={{ color: accentColor }}>{fmt(product.display_price)}</span>
            </div>
            <div className="spec-row">
              <span className="spec-key">Наличие</span>
              <span className="spec-val" style={{ color: 'var(--green)' }}>✓ В наличии</span>
            </div>
          </div>
        )}

        {specs.length === 0 && (
          <div className="detail-specs">
            <div className="spec-row">
              <span className="spec-key">Цена</span>
              <span className="spec-val" style={{ color: accentColor }}>{fmt(product.display_price)}</span>
            </div>
            <div className="spec-row">
              <span className="spec-key">Наличие</span>
              <span className="spec-val" style={{ color: 'var(--green)' }}>✓ В наличии</span>
            </div>
          </div>
        )}
      </div>

      <div className="buy-bar">
        <div className="qty-control">
          <button className="qty-btn" onClick={() => setQty(q => Math.max(1, q - 1))}>−</button>
          <span className="qty-num">{qty}</span>
          <button className="qty-btn" onClick={() => setQty(q => q + 1)}>+</button>
        </div>
        <button className={`buy-btn${inCart ? ' in-cart' : ''}`}
          style={{ borderRadius: btnRadius, background: inCart ? 'var(--green)' : accentColor }}
          onClick={handleBuy}>
          {inCart ? '✓ В корзине' : `Купить · ${fmt(product.display_price * qty)}`}
        </button>
      </div>
    </div>
  )
}
