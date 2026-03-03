import { useState } from 'react'
import { useCart } from './hooks/useCart'
import HomePage from './pages/HomePage'
import ProductPage from './pages/ProductPage'
import CartPage from './pages/CartPage'
import CheckoutPage from './pages/CheckoutPage'
import SuccessPage from './pages/SuccessPage'

export default function App() {
  const [page, setPage] = useState({ name: 'home', params: {} })
  const cart = useCart()

  const go = (name, params = {}) => setPage({ name, params })

  const pages = { home: HomePage, product: ProductPage, cart: CartPage, checkout: CheckoutPage, success: SuccessPage }
  const Page = pages[page.name] || HomePage

  return <Page params={page.params} go={go} cart={cart} />
}
