export default function SuccessPage({ go }) {
  const tg = window.Telegram?.WebApp
  
  const close = () => {
    if (tg) tg.close()
    else go('home')
  }

  return (
    <div className="success-page">
      <div className="success-icon">✅</div>
      <div className="success-title">Заказ оформлен!</div>
      <div className="success-sub">
        Спасибо за покупку 🍎<br/>
        Наш менеджер свяжется с вами<br/>в течение 15 минут
      </div>
      <button
        style={{background:'var(--accent2)',color:'#fff',fontFamily:'var(--font)',fontSize:15,fontWeight:700,padding:'14px 32px',borderRadius:50,marginTop:8}}
        onClick={close}
      >
        {tg ? 'Закрыть' : 'На главную'}
      </button>
    </div>
  )
}
