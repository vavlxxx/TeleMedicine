const STITCH_HTML_URL = '/stitch/public-questions-feed-ru.html'

function PublicQuestionsFeedPage() {
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
        title="Public Questions Feed (RU)"
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

export default PublicQuestionsFeedPage
