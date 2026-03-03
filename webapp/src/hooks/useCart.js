import { useState, useCallback } from 'react'

export function useCart() {
  const [items, setItems] = useState([])

  const add = useCallback((product) => {
    setItems(prev => {
      const exists = prev.find(i => i.id === product.id)
      if (exists) return prev.map(i => i.id === product.id ? { ...i, qty: i.qty + 1 } : i)
      return [...prev, { ...product, qty: 1 }]
    })
  }, [])

  const remove = useCallback((id) => {
    setItems(prev => prev.filter(i => i.id !== id))
  }, [])

  const updateQty = useCallback((id, qty) => {
    if (qty <= 0) { remove(id); return }
    setItems(prev => prev.map(i => i.id === id ? { ...i, qty } : i))
  }, [remove])

  const clear = useCallback(() => setItems([]), [])

  const total = items.reduce((s, i) => s + i.display_price * i.qty, 0)
  const count = items.reduce((s, i) => s + i.qty, 0)
  const inCart = (id) => items.find(i => i.id === id)

  return { items, add, remove, updateQty, clear, total, count, inCart }
}
