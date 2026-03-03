const BASE = import.meta.env.VITE_API_URL || ''

async function req(path, opts = {}) {
  const r = await fetch(`${BASE}/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts
  })
  if (!r.ok) throw new Error(`API error: ${r.status}`)
  return r.json()
}

export const api = {
  getCategories: () => req('/categories'),
  getProducts: (catId) => req(`/products${catId ? `?category_id=${catId}` : ''}`),
  searchProducts: (q) => req(`/products/search?q=${encodeURIComponent(q)}`),
  getProduct: (id) => req(`/products/${id}`),
  createOrder: (data) => req('/orders', { method: 'POST', body: JSON.stringify(data) }),
}
