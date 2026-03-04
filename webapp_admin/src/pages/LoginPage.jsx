import { useState } from 'react'
import { adminApi, setToken } from '../api'

export default function LoginPage({ onLogin }) {
  const [pw, setPw] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if (!pw) return
    setLoading(true); setError('')
    try {
      const r = await adminApi.login(pw)
      setToken(r.token)
      onLogin()
    } catch (e) {
      setError('Неверный пароль')
    } finally { setLoading(false) }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-title">🍎 Admin Panel</div>
        <div className="login-sub">Apple Store — панель управления</div>
        {error && <div className="login-error">{error}</div>}
        <div className="form-row">
          <label className="form-label">Пароль</label>
          <input className="form-input" type="password" placeholder="Введите пароль"
            value={pw} onChange={e => setPw(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && submit()} autoFocus />
        </div>
        <button className="btn btn-primary" style={{width:'100%',justifyContent:'center'}}
          onClick={submit} disabled={loading}>
          {loading ? 'Вход...' : 'Войти →'}
        </button>
      </div>
    </div>
  )
}
