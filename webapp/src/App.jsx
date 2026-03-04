import { useState, useEffect } from 'react'
import { useCart } from './hooks/useCart'
import HomePage from './pages/HomePage'
import ProductPage from './pages/ProductPage'
import CartPage from './pages/CartPage'
import CheckoutPage from './pages/CheckoutPage'
import SuccessPage from './pages/SuccessPage'

function applyDesign(d) {
  if (!d) return
  const r = document.documentElement.style
  if (d.design_accent_color)  r.setProperty('--accent2', d.design_accent_color)
  if (d.design_bg_color)      r.setProperty('--bg', d.design_bg_color)
  if (d.design_card_color)    r.setProperty('--card', d.design_card_color)
  if (d.design_text_color)    r.setProperty('--text', d.design_text_color)
  if (d.design_button_radius) r.setProperty('--btn-radius', d.design_button_radius + 'px')
  if (d.design_card_radius)   r.setProperty('--radius', d.design_card_radius + 'px')
}

export default function App() {
  const [page, setPage] = useState({ name: 'home', params: {} })
  const [design, setDesign] = useState({})
  const cart = useCart()

  // Load design on mount and poll every 30s for live updates
  useEffect(() => {
    const load = () =>
      fetch('/api/design')
        .then(r => r.json())
        .then(d => { setDesign(d); applyDesign(d) })
        .catch(() => {})

    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  const go = (name, params = {}) => setPage({ name, params })

  const pages = {
    home: HomePage,
    product: ProductPage,
    cart: CartPage,
    checkout: CheckoutPage,
    success: SuccessPage
  }
  const Page = pages[page.name] || HomePage

  return <Page params={page.params} go={go} cart={cart} design={design} />
}
