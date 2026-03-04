const BASE = import.meta.env.VITE_API_URL || ''
let _token = localStorage.getItem('admin_token') || ''

export function setToken(t) { _token = t; localStorage.setItem('admin_token', t) }
export function getToken() { return _token }
export function clearToken() { _token = ''; localStorage.removeItem('admin_token') }

async function req(path, opts = {}) {
  const r = await fetch(`${BASE}/admin-api${path}`, {
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': _token },
    ...opts
  })
  if (r.status === 401) { clearToken(); window.location.reload(); return }
  if (!r.ok) { const e = await r.json().catch(() => ({})); throw new Error(e.detail || 'Error ' + r.status) }
  return r.json()
}

export const adminApi = {
  login: (password) => req('/login', { method: 'POST', body: JSON.stringify({ password }) }),
  getStats: () => req('/stats'),
  getCategories: () => req('/categories'),
  createCategory: (data) => req('/categories', { method: 'POST', body: JSON.stringify(data) }),
  updateCategory: (id, data) => req('/categories/' + id, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCategory: (id) => req('/categories/' + id, { method: 'DELETE' }),
  getProducts: () => req('/products'),
  createProduct: (data) => req('/products', { method: 'POST', body: JSON.stringify(data) }),
  updateProduct: (id, data) => req('/products/' + id, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProduct: (id) => req('/products/' + id, { method: 'DELETE' }),
  getOrders: () => req('/orders'),
  updateOrderStatus: (id, status) => req('/orders/' + id + '/status', { method: 'PUT', body: JSON.stringify({ status }) }),
  getSettings: () => req('/settings'),
  updateSettings: (data) => req('/settings', { method: 'PUT', body: JSON.stringify(data) }),
}
