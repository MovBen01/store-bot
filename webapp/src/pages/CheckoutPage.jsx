import { useState } from 'react'
import { api } from '../api'

function fmt(n) { return Number(n).toLocaleString('ru-RU') + ' ₽' }

export default function CheckoutPage({ go, cart }) {
  const [form, setForm] = useState({ contact: '', name: '', comment: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const tg = window.Telegram?.WebApp
  const user = tg?.initDataUnsafe?.user

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const submit = async () => {
    if (!form.contact.trim()) { setError('Укажите контакт для связи'); return }
    setLoading(true); setError('')
    try {
      const items = cart.items.map(i => ({ product_id: i.id, name: i.name, price: i.display_price, qty: i.qty }))
      await api.createOrder({
        user_id: user?.id || 0,
        username: user?.username || form.name,
        items,
        total: cart.total,
        contact: form.contact,
        comment: form.comment,
        tg_init_data: tg?.initData || ''
      })
      cart.clear()
      go('success')
    } catch (e) {
      setError('Ошибка оформления. Попробуйте снова.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="header">
        <button className="back-btn" style={{padding:0}} onClick={() => go('cart')}>← Корзина</button>
        <div style={{fontFamily:'var(--font)',fontWeight:700}}>Оформление</div>
        <div style={{width:60}}/>
      </div>

      <div className="checkout-form">
        <div style={{background:'var(--bg3)',borderRadius:16,padding:16,marginBottom:20}}>
          <div style={{fontSize:13,color:'var(--text2)',marginBottom:4}}>Сумма заказа</div>
          <div style={{fontFamily:'var(--font)',fontSize:24,fontWeight:700,color:'var(--accent2)'}}>{fmt(cart.total)}</div>
          <div style={{fontSize:13,color:'var(--text2)',marginTop:4}}>{cart.count} товар(ов)</div>
        </div>

        <div className="form-group">
          <label className="form-label">КОНТАКТ ДЛЯ СВЯЗИ *</label>
          <input className="form-input" placeholder="@username, телефон или email"
            value={form.contact} onChange={e => set('contact', e.target.value)} />
        </div>

        <div className="form-group">
          <label className="form-label">ВАШЕ ИМЯ</label>
          <input className="form-input" placeholder={user?.first_name || 'Введите имя'}
            value={form.name} onChange={e => set('name', e.target.value)} />
        </div>

        <div className="form-group">
          <label className="form-label">КОММЕНТАРИЙ К ЗАКАЗУ</label>
          <textarea className="form-input" rows={3}
            placeholder="Цвет, объём памяти, адрес доставки..."
            value={form.comment} onChange={e => set('comment', e.target.value)}
            style={{resize:'none'}}/>
        </div>

        {error && <div style={{color:'#ff3b30',fontSize:14,marginBottom:12}}>{error}</div>}

        <button
          style={{width:'100%',background:loading?'var(--bg3)':'var(--accent2)',color:'#fff',fontFamily:'var(--font)',fontSize:16,fontWeight:700,padding:18,borderRadius:14,opacity:loading?0.6:1}}
          onClick={submit}
          disabled={loading}
        >
          {loading ? '⏳ Оформляем...' : 'Подтвердить заказ ✓'}
        </button>

        <div style={{fontSize:12,color:'var(--text3)',textAlign:'center',marginTop:16,lineHeight:1.6}}>
          После оформления менеджер свяжется с вами в течение 15 минут
        </div>
      </div>
    </div>
  )
}
