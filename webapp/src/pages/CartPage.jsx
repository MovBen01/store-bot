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

export default function CartPage({ go, cart }) {
  if (cart.items.length === 0) return (
    <div className="page">
      <div className="header">
        <button className="back-btn" style={{padding:0}} onClick={() => go('home')}>← Назад</button>
        <div style={{fontFamily:'var(--font)',fontWeight:700}}>Корзина</div>
        <div style={{width:40}}/>
      </div>
      <div className="cart-empty">
        <div className="cart-empty-icon">🛒</div>
        <div className="cart-empty-text">Корзина пуста</div>
        <button style={{background:'var(--accent2)',color:'#fff',padding:'12px 24px',borderRadius:50,fontWeight:700,fontSize:14}}
          onClick={() => go('home')}>Перейти в каталог</button>
      </div>
    </div>
  )

  return (
    <div className="page">
      <div className="header">
        <button className="back-btn" style={{padding:0}} onClick={() => go('home')}>← Назад</button>
        <div style={{fontFamily:'var(--font)',fontWeight:700}}>Корзина</div>
        <button onClick={cart.clear} style={{fontSize:13,color:'var(--text3)'}}>Очистить</button>
      </div>

      {cart.items.map(item => (
        <div key={item.id} className="cart-item fade-up">
          <div className="cart-item-img">{EMOJI_MAP(item.name)}</div>
          <div className="cart-item-info">
            <div className="cart-item-name">{item.name}</div>
            <div className="cart-item-price">{fmt(item.display_price * item.qty)}</div>
            <div style={{display:'flex',alignItems:'center',gap:8,marginTop:6}}>
              <button style={{width:28,height:28,borderRadius:50,background:'var(--bg3)',fontSize:16,display:'flex',alignItems:'center',justifyContent:'center'}}
                onClick={() => cart.updateQty(item.id, item.qty-1)}>−</button>
              <span style={{fontWeight:700,fontSize:14}}>{item.qty}</span>
              <button style={{width:28,height:28,borderRadius:50,background:'var(--bg3)',fontSize:16,display:'flex',alignItems:'center',justifyContent:'center'}}
                onClick={() => cart.updateQty(item.id, item.qty+1)}>+</button>
            </div>
          </div>
          <button className="cart-item-remove" onClick={() => cart.remove(item.id)}>✕</button>
        </div>
      ))}

      <div className="cart-total">
        <div className="cart-total-row"><span>Товаров</span><span>{cart.count} шт.</span></div>
        <div className="cart-total-sum"><span>Итого</span><span style={{color:'var(--accent2)'}}>{fmt(cart.total)}</span></div>
      </div>

      <div style={{padding:'0 16px'}}>
        <button
          style={{width:'100%',background:'var(--accent2)',color:'#fff',fontFamily:'var(--font)',fontSize:16,fontWeight:700,padding:18,borderRadius:14,textAlign:'center'}}
          onClick={() => go('checkout')}
        >Оформить заказ →</button>
      </div>
    </div>
  )
}
