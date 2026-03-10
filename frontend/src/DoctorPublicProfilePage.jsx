const STITCH_HTML_URL = '/stitch/doctor-public-profile-ru.html'

function DoctorPublicProfilePage() {
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
        title="Doctor Public Profile (RU)"
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

export default DoctorPublicProfilePage
