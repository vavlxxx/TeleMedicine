const STITCH_HTML_URL = '/stitch/login-desktop-ru.html'

function LoginDesktopPage() {
  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: '#f5f7fb',
      }}
    >
      <iframe
        title="Вход в систему (Desktop)"
        src={STITCH_HTML_URL}
        style={{
          width: '100%',
          minHeight: '100vh',
          border: 'none',
          background: '#ffffff',
        }}
      />
    </main>
  )
}

export default LoginDesktopPage
