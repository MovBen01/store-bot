export default function Toast({ msg, type = 'success' }) {
  return (
    <div className={'toast toast-' + type}>
      {type === 'success' ? '✅' : '❌'} {msg}
    </div>
  )
}
