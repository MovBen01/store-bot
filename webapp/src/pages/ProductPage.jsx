import { useState, useEffect } from 'react'
import { api } from '../api'

function fmt(n) { return Number(n).toLocaleString('ru-RU') + ' ₽' }

const EMOJI_MAP = (name) => {
  if (!name) return '📦'
  if (name.includes('iPhone')) return '📱'
  if (name.includes('MacBook')) return '💻'
  if (name.includes('iPad')) return '🗂'
  if (name.includes('AirPods')) return '🎧'
  if (name.includes('Watch')) return '⌚'
  return '📦'
}

export default function ProductPage({ params, go, cart }) {
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

  const handleBuy = () => {
    for (let i = 0; i < qty; i++) cart.add(product)
    go('cart')
  }

  return (
    <div className="detail-page">
      <button className="back-btn" onClick={() => go('home')}>← Назад</button>

      <div className="detail-img">{EMOJI_MAP(product.name)}</div>

      <div className="detail-content">
        <div className="detail-cat">{product.category_name || 'Apple'}</div>
        <div className="detail-name">{product.name}</div>
        <div className="detail-price">{fmt(product.display_price)}</div>
        <div className="detail-desc">{product.description || 'Оригинальная продукция Apple. Гарантия 1 год.'}</div>

        <div className="detail-specs">
          {product.name.includes('iPhone') && <>
            <div className="spec-row"><span className="spec-key">Чип</span><span className="spec-val">A18</span></div>
            <div className="spec-row"><span className="spec-key">Камера</span><span className="spec-val">48 МП</span></div>
            <div className="spec-row"><span className="spec-key">Гарантия</span><span className="spec-val">1 год</span></div>
          </>}
          {product.name.includes('MacBook') && <>
            <div className="spec-row"><span className="spec-key">Чип</span><span className="spec-val">Apple Silicon</span></div>
            <div className="spec-row"><span className="spec-key">RAM</span><span className="spec-val">16 ГБ</span></div>
            <div className="spec-row"><span className="spec-key">Гарантия</span><span className="spec-val">1 год</span></div>
          </>}
          <div className="spec-row"><span className="spec-key">Цена</span><span className="spec-val" style={{color:'var(--accent2)'}}>{fmt(product.display_price)}</span></div>
          <div className="spec-row"><span className="spec-key">Наличие</span><span className="spec-val" style={{color:'var(--green)'}}>✓ В наличии</span></div>
        </div>
      </div>

      <div className="buy-bar">
        <div className="qty-control">
          <button className="qty-btn" onClick={() => setQty(q => Math.max(1, q-1))}>−</button>
          <span className="qty-num">{qty}</span>
          <button className="qty-btn" onClick={() => setQty(q => q+1)}>+</button>
        </div>
        <button className={`buy-btn${inCart ? ' in-cart' : ''}`} onClick={handleBuy}>
          {inCart ? '✓ В корзине' : `Купить · ${fmt(product.display_price * qty)}`}
        </button>
      </div>
    </div>
  )
}
