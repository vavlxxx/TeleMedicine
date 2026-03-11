import { useEffect, useMemo, useState } from 'react'
import { ApiError, apiClient } from './api/client'
import { AppLink, useRouter } from './router'
import { routes, withReturnTo } from './routes'
import { formatDateTime, getDisplayName, getInitials, parsePositiveInteger } from './publicPageUtils'
import { TelemedPage } from './TelemedLayout'
import {
  formatRelativeQuestionTime,
  getDoctorVisualProfile,
  getQuestionCategory,
  getQuestionPatientMeta,
} from './telemedReference'

function QuestionPublicDetailPage() {
  const { location } = useRouter()
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search])
  const questionId = parsePositiveInteger(searchParams.get('question_id'))
  const currentPageHref = `${location.pathname}${location.search}${location.hash || ''}`

  const [question, setQuestion] = useState(null)
  const [isLoading, setIsLoading] = useState(Boolean(questionId))
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let isCancelled = false

    if (!questionId) {
      setQuestion(null)
      setIsLoading(false)
      setErrorMessage('')
      return undefined
    }

    const loadQuestion = async () => {
      setIsLoading(true)
      setErrorMessage('')

      try {
        const response = await apiClient.getQuestion(questionId)

        if (!isCancelled) {
          setQuestion(response)
        }
      } catch (error) {
        if (!isCancelled) {
          setQuestion(null)
          setErrorMessage(error instanceof ApiError ? error.message : 'Не удалось загрузить вопрос')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadQuestion()

    return () => {
      isCancelled = true
    }
  }, [questionId])

  const category = question ? getQuestionCategory(question) : ''
  const patientMeta = question ? getQuestionPatientMeta(question) : null

  return (
    <TelemedPage activeNav="questions" actionLabel="Войти" actionHref={withReturnTo(routes.login, currentPageHref)}>
      <section className="tm-page-section">
        <div className="tm-shell">
          <div className="tm-breadcrumbs">
            <span>Главная</span>
            <span>Вопросы</span>
            <span>Вопрос #{questionId || '...'}</span>
          </div>

          {!questionId ? (
            <section className="tm-card tm-empty-state">
              <h2>Вопрос не выбран</h2>
              <p>Откройте ленту открытых вопросов и перейдите в конкретное обсуждение.</p>
              <AppLink className="tm-button" href={routes.questions}>
                К ленте вопросов
              </AppLink>
            </section>
          ) : null}

          {isLoading ? (
            <section className="tm-card tm-empty-state">
              <h2>Загружаем обсуждение</h2>
              <p>Получаем вопрос и ответы специалистов из backend.</p>
            </section>
          ) : null}

          {!isLoading && errorMessage ? (
            <section className="tm-card tm-empty-state">
              <h2>Не удалось открыть вопрос</h2>
              <p>{errorMessage}</p>
              <AppLink className="tm-button" href={routes.questions}>
                Вернуться в ленту
              </AppLink>
            </section>
          ) : null}

          {question ? (
            <div className="tm-question-detail-layout">
              <article className="tm-card tm-question-card">
                <div className="tm-inline-meta">
                  <span className="tm-overline">Вопрос пациента</span>
                  <span className="tm-muted">{formatRelativeQuestionTime(question.created_at)}</span>
                </div>

                <h1 className="tm-question-card__title">{question.text}</h1>

                <div className="tm-question-detail-meta">
                  <span>{getDisplayName(question.author)}</span>
                  <span>{patientMeta.age} года</span>
                  <span>{patientMeta.city}</span>
                  <span>{category}</span>
                </div>

                <p>{question.text}</p>

                <div className="tm-card tm-detail-card">
                  <h2>Прикрепленные материалы</h2>
                  <p>
                    В текущем MVP реальные attachments к вопросам ещё не подключены. Блок оставлен
                    в структуре страницы, чтобы она совпадала по иерархии с целевым макетом.
                  </p>
                </div>
              </article>

              <section className="tm-response-list">
                <div className="tm-question-card__row">
                  <h2>Ответы специалистов ({question.comments.length})</h2>
                  <span className="tm-muted">Обновлено {formatDateTime(question.created_at)}</span>
                </div>

                {question.comments.length ? (
                  question.comments.map((comment) => {
                    const visualProfile = getDoctorVisualProfile(comment.author)

                    return (
                      <article className="tm-card tm-response-card" key={comment.id}>
                        <div className="tm-response-card__head">
                          <div
                            className="tm-doctor-portrait tm-response-card__avatar"
                            style={{ background: visualProfile.theme.background }}
                            aria-hidden="true"
                          >
                            {getInitials(comment.author)}
                          </div>

                          <div>
                            <h3>{getDisplayName(comment.author)}</h3>
                            <div className="tm-inline-meta">
                              <span className="tm-muted">{category}</span>
                              <span className="tm-muted">{visualProfile.experience}</span>
                              <span className="tm-rating-badge">
                                <span className="material-symbols-outlined">star</span>
                                {visualProfile.rating}
                              </span>
                            </div>
                          </div>

                          <span className="tm-verified-strip">Доступен онлайн</span>
                        </div>

                        <p>{comment.text}</p>

                        <ul className="tm-recommendations">
                          <li>Записать ключевые симптомы и время их появления.</li>
                          <li>Подготовить предыдущие обследования перед консультацией.</li>
                          <li>При ухудшении состояния обратиться за очной помощью.</li>
                        </ul>

                        <div className="tm-response-card__footer">
                          <span className="tm-muted">Ответ опубликован {formatDateTime(comment.created_at)}</span>
                          <AppLink className="tm-button tm-button--dark" href={withReturnTo(routes.login, currentPageHref)}>
                            Записаться на консультацию
                          </AppLink>
                        </div>
                      </article>
                    )
                  })
                ) : (
                  <section className="tm-card tm-empty-state">
                    <h2>Ответов пока нет</h2>
                    <p>Вопрос опубликован и ожидает комментариев верифицированных врачей.</p>
                  </section>
                )}
              </section>
            </div>
          ) : null}
        </div>
      </section>
    </TelemedPage>
  )
}

export default QuestionPublicDetailPage
