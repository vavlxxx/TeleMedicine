const STITCH_HTML_URL = '/stitch/registration-desktop-ru.html'

function RegistrationDesktopPage() {
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
        title="Регистрация (Desktop)"
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

export default RegistrationDesktopPage
