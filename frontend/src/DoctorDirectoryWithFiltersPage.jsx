const STITCH_HTML_URL = '/stitch/doctor-directory-with-filters-ru.html'

function DoctorDirectoryWithFiltersPage() {
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
        title="Doctor Directory with Filters (RU)"
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

export default DoctorDirectoryWithFiltersPage
