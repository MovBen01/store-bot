import { useState, useEffect } from 'react'
import { adminApi } from '../api'

function fmt(n) { return Number(n || 0).toLocaleString('ru-RU') + ' ₽' }

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => { adminApi.getStats().then(setStats).catch(console.error) }, [])

  if (!stats) return <div className="loading-center"><div className="spinner"/></div>

  const STATUS = { new: ['🆕 Новый','badge-blue'], done: ['✅ Выполнен','badge-green'], cancelled: ['❌ Отменён','badge-red'] }

  return (
    <>
      <div className="page-title">Dashboard</div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Всего заказов</div>
          <div className="stat-value">{stats.orders_total}</div>
          <div className="stat-sub">за всё время</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Новых заказов</div>
          <div className="stat-value" style={{color:'var(--blue)'}}>{stats.orders_new}</div>
          <div className="stat-sub">ожидают обработки</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Выручка</div>
          <div className="stat-value" style={{color:'var(--accent)',fontSize:22}}>{fmt(stats.revenue)}</div>
          <div className="stat-sub">выполненные заказы</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Товаров</div>
          <div className="stat-value">{stats.products_count}</div>
          <div className="stat-sub">в каталоге</div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Последние заказы</div>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>#</th><th>Товар</th><th>Сумма</th><th>Контакт</th><th>Статус</th><th>Дата</th>
            </tr></thead>
            <tbody>
              {(stats.recent_orders || []).map(o => {
                const [label, cls] = STATUS[o.status] || ['—','']
                return (
                  <tr key={o.id}>
                    <td className="text-muted">#{o.id}</td>
                    <td style={{maxWidth:200,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{o.product_name}</td>
                    <td style={{fontWeight:600,color:'var(--accent)'}}>{fmt(o.price)}</td>
                    <td className="text-muted">{o.contact}</td>
                    <td><span className={'badge ' + cls}>{label}</span></td>
                    <td className="text-muted text-sm">{o.created_at?.slice(0,10)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
