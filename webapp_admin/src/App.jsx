import { useState, useEffect } from 'react'
import { getToken, clearToken } from './api'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ProductsPage from './pages/ProductsPage'
import CategoriesPage from './pages/CategoriesPage'
import OrdersPage from './pages/OrdersPage'
import SettingsPage from './pages/SettingsPage'

const NAV = [
  { id: 'dashboard', icon: '📊', label: 'Dashboard' },
  { id: 'products',  icon: '📦', label: 'Товары' },
  { id: 'categories',icon: '🗂',  label: 'Категории' },
  { id: 'orders',    icon: '🛒',  label: 'Заказы' },
  { id: 'settings',  icon: '⚙️',  label: 'Настройки' },
]

const PAGES = { dashboard: Dashboard, products: ProductsPage, categories: CategoriesPage, orders: OrdersPage, settings: SettingsPage }

export default function App() {
  const [auth, setAuth] = useState(!!getToken())
  const [page, setPage] = useState('dashboard')

  if (!auth) return <LoginPage onLogin={() => setAuth(true)} />

  const Page = PAGES[page]

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">🍎 Admin</div>
        {NAV.map(n => (
          <div key={n.id} className={'nav-item' + (page === n.id ? ' active' : '')} onClick={() => setPage(n.id)}>
            <span className="nav-icon">{n.icon}</span>
            {n.label}
          </div>
        ))}
        <div style={{marginTop:'auto'}}>
          <div className="nav-item" onClick={() => { clearToken(); setAuth(false) }}>
            <span className="nav-icon">🚪</span> Выйти
          </div>
        </div>
      </aside>
      <main className="main">
        <Page />
      </main>
    </div>
  )
}
