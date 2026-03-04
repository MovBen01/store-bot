import { useState, useEffect } from 'react'
import { adminApi } from '../api'
import Toast from '../components/Toast'

const STATUS_MAP = {
  new:       { label: '🆕 Новый',    cls: 'badge-blue' },
  done:      { label: '✅ Выполнен', cls: 'badge-green' },
  cancelled: { label: '❌ Отменён',  cls: 'badge-red' },
}

function fmt(n) { return Number(n).toLocaleString('ru-RU') + ' ₽' }

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [toast, setToast] = useState(null)

  const load = () => { setLoading(true); adminApi.getOrders().then(d => { setOrders(d); setLoading(false) }) }
  useEffect(() => { load() }, [])

  const showToast = (msg, type='success') => { setToast({msg,type}); setTimeout(() => setToast(null), 3000) }

  const setStatus = async (id, status) => {
    await adminApi.updateOrderStatus(id, status)
    showToast('Статус обновлён ✓'); load()
  }

  const filtered = filter === 'all' ? orders : orders.filter(o => o.status === filter)

  return (
    <>
      {toast && <Toast msg={toast.msg} type={toast.type} />}
      <div className="flex-between mb-4">
        <div className="page-title" style={{margin:0}}>Заказы</div>
        <div className="flex gap-2">
          {['all','new','done','cancelled'].map(f => (
            <button key={f} className={'btn btn-ghost btn-sm' + (filter===f?' btn-primary':'')} onClick={() => setFilter(f)}>
              {f==='all'?'Все':STATUS_MAP[f]?.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? <div className="loading-center"><div className="spinner"/></div> : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr>
                <th>#</th><th>Товар</th><th>Сумма</th><th>Контакт</th><th>Комментарий</th><th>Статус</th><th>Дата</th><th>Действие</th>
              </tr></thead>
              <tbody>
                {filtered.map(o => {
                  const s = STATUS_MAP[o.status] || { label: o.status, cls: '' }
                  return (
                    <tr key={o.id}>
                      <td className="text-muted">#{o.id}</td>
                      <td style={{maxWidth:180,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',fontWeight:500}}>{o.product_name}</td>
                      <td style={{color:'var(--accent)',fontWeight:600}}>{fmt(o.price)}</td>
                      <td className="text-muted">{o.contact}</td>
                      <td className="text-muted text-sm" style={{maxWidth:150,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{o.comment || '—'}</td>
                      <td><span className={'badge ' + s.cls}>{s.label}</span></td>
                      <td className="text-muted text-sm">{o.created_at?.slice(0,10)}</td>
                      <td>
                        <div className="flex gap-2">
                          {o.status !== 'done' && <button className="btn btn-ghost btn-sm" style={{color:'var(--green)'}} onClick={() => setStatus(o.id,'done')}>✅</button>}
                          {o.status !== 'cancelled' && <button className="btn btn-ghost btn-sm" style={{color:'var(--red)'}} onClick={() => setStatus(o.id,'cancelled')}>❌</button>}
                          {o.status !== 'new' && <button className="btn btn-ghost btn-sm" onClick={() => setStatus(o.id,'new')}>🔄</button>}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  )
}
