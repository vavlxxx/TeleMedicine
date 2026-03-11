import { useEffect, useMemo, useState } from 'react'
import { ApiError, apiClient } from './api/client'
import { AppLink, useRouter } from './router'
import { routes, withReturnTo } from './routes'
import { formatDateTime, getDisplayName, getInitials, parsePositiveInteger } from './publicPageUtils'
import { TelemedPage } from './TelemedLayout'
import { getDoctorVisualProfile } from './telemedReference'

const profileTabs = ['О враче', 'Образование и опыт', 'Отзывы', 'Публикации']

function DoctorPublicProfilePage() {
  const { location } = useRouter()
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search])
  const doctorId = parsePositiveInteger(searchParams.get('doctor_id'))
  const currentPageHref = `${location.pathname}${location.search}${location.hash || ''}`

  const [doctor, setDoctor] = useState(null)
  const [isLoading, setIsLoading] = useState(Boolean(doctorId))
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let isCancelled = false

    if (!doctorId) {
      setDoctor(null)
      setIsLoading(false)
      return undefined
    }

    const loadDoctor = async () => {
      setIsLoading(true)
      setErrorMessage('')

      try {
        const response = await apiClient.getDoctor(doctorId)

        if (!isCancelled) {
          setDoctor(response)
        }
      } catch (error) {
        if (!isCancelled) {
          setDoctor(null)
          setErrorMessage(error instanceof ApiError ? error.message : 'Не удалось загрузить профиль врача')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadDoctor()

    return () => {
      isCancelled = true
    }
  }, [doctorId])

  const visualProfile = doctor ? getDoctorVisualProfile(doctor) : null
  const reviewCards = doctor
    ? [
        {
          author: 'Елена М.',
          text: `Очень внимательный врач. ${getDisplayName(doctor)} подробно объяснил рекомендации и дальнейшие шаги.`,
        },
        {
          author: 'Игорь П.',
          text: 'Консультация прошла структурированно, получил понятный план обследования и лечения.',
        },
      ]
    : []

  return (
    <TelemedPage
      activeNav="doctors"
      actionLabel="Личный кабинет"
      actionHref={withReturnTo(routes.login, currentPageHref)}
    >
      <section className="tm-page-section">
        <div className="tm-shell">
          <div className="tm-breadcrumbs">
            <span>Главная</span>
            <span>Кардиология</span>
            <span>{doctor ? getDisplayName(doctor) : 'Профиль врача'}</span>
          </div>

          {!doctorId ? (
            <section className="tm-card tm-empty-state">
              <h2>Врач не выбран</h2>
              <p>Вернитесь в каталог и откройте карточку нужного врача.</p>
              <AppLink className="tm-button" href={routes.doctors}>
                В каталог врачей
              </AppLink>
            </section>
          ) : null}

          {isLoading ? (
            <section className="tm-card tm-empty-state">
              <h2>Загружаем профиль врача</h2>
              <p>Получаем публичные данные врача по `doctor_id`.</p>
            </section>
          ) : null}

          {!isLoading && errorMessage ? (
            <section className="tm-card tm-empty-state">
              <h2>Профиль не открылся</h2>
              <p>{errorMessage}</p>
              <AppLink className="tm-button" href={routes.doctors}>
                Назад к каталогу
              </AppLink>
            </section>
          ) : null}

          {doctor && visualProfile ? (
            <div className="tm-profile-layout">
              <div className="tm-grid">
                <article className="tm-card tm-profile-hero">
                  <div
                    className="tm-doctor-portrait tm-profile-hero__portrait"
                    style={{ background: visualProfile.theme.background }}
                    aria-hidden="true"
                  >
                    {getInitials(doctor)}
                  </div>

                  <div>
                    <div className="tm-inline-meta">
                      <span className="tm-verified-strip">Проверенный эксперт</span>
                      <span className="tm-rating-badge">
                        <span className="material-symbols-outlined">star</span>
                        {visualProfile.rating}
                      </span>
                    </div>

                    <h1 className="tm-profile-hero__title">{getDisplayName(doctor)}</h1>
                    <p className="tm-muted">
                      {doctor.specializations.map((item) => item.name).join(', ') || 'Врач'} ·{' '}
                      {visualProfile.qualification}
                    </p>

                    <div className="tm-stat-grid">
                      <div className="tm-stat">
                        <label>Стаж работы</label>
                        <strong>{visualProfile.experience.replace('Стаж: ', '')}</strong>
                      </div>
                      <div className="tm-stat">
                        <label>Категория</label>
                        <strong>Высшая</strong>
                      </div>
                      <div className="tm-stat">
                        <label>Степень</label>
                        <strong>{visualProfile.qualification}</strong>
                      </div>
                    </div>
                  </div>
                </article>

                <article className="tm-card tm-detail-card">
                  <div className="tm-tabbar">
                    {profileTabs.map((item, index) => (
                      <span className={index === 0 ? 'is-active' : ''} key={item}>
                        {item}
                      </span>
                    ))}
                  </div>

                  <div style={{ paddingTop: '24px' }}>
                    <h2>Специализация</h2>
                    <p>
                      {getDisplayName(doctor)} ведет дистанционные консультации, помогает с
                      маршрутизацией пациента и формированием плана дальнейшего обследования.
                      Публичный профиль рендерит только открытые поля из backend DTO.
                    </p>

                    <h2 style={{ marginTop: '28px' }}>Опыт и образование</h2>
                    <div className="tm-timeline">
                      <div className="tm-timeline-item">
                        <span className="tm-overline">2018 — наст. время</span>
                        <h3>Ведущий специалист онлайн-консультаций</h3>
                        <p className="tm-muted">Практика по направлению {doctor.specializations[0]?.name || 'терапия'}.</p>
                      </div>
                      <div className="tm-timeline-item">
                        <span className="tm-overline">2013 — 2018</span>
                        <h3>Врач амбулаторного приема</h3>
                        <p className="tm-muted">Работа с хроническими пациентами и сопровождением после лечения.</p>
                      </div>
                      <div className="tm-timeline-item">
                        <span className="tm-overline">2010 — 2012</span>
                        <h3>Ординатура и клиническая практика</h3>
                        <p className="tm-muted">Медицинская база, на которой строится текущая специализация врача.</p>
                      </div>
                    </div>
                  </div>
                </article>

                <section className="tm-grid">
                  <div className="tm-question-card__row">
                    <h2>Отзывы пациентов</h2>
                    <span className="tm-link">Все отзывы</span>
                  </div>

                  <div className="tm-review-grid">
                    {reviewCards.map((review) => (
                      <article className="tm-card tm-review-card" key={review.author}>
                        <div className="tm-inline-meta">
                          <div className="tm-doctor-portrait" style={{ width: '44px', height: '44px', borderRadius: '16px', background: '#eff3fb', color: '#5d6a83', fontSize: '14px' }}>
                            {review.author.split(' ').map((part) => part[0]).join('')}
                          </div>
                          <div>
                            <strong>{review.author}</strong>
                            <div className="tm-muted">{formatDateTime(new Date().toISOString())}</div>
                          </div>
                        </div>
                        <p>{review.text}</p>
                      </article>
                    ))}
                  </div>
                </section>
              </div>

              <aside className="tm-grid">
                <article className="tm-card tm-side-panel">
                  <div className="tm-side-panel__header">
                    <div>
                      <span className="tm-overline">Стоимость консультации</span>
                      <strong style={{ display: 'block', marginTop: '8px', fontSize: '42px', fontFamily: 'Manrope, sans-serif', letterSpacing: '-0.05em' }}>
                        {visualProfile.price.toLocaleString('ru-RU')} ₽
                      </strong>
                    </div>
                    <span className="material-symbols-outlined" style={{ color: '#2f6fe8' }}>credit_card</span>
                  </div>

                  <div className="tm-field-stack">
                    <div className="tm-card" style={{ padding: '16px', borderRadius: '18px', background: '#f5f7ff' }}>
                      <strong>Ближайший слот</strong>
                      <p className="tm-muted" style={{ margin: '6px 0 0' }}>{visualProfile.eta}, 14:30 (мск)</p>
                    </div>
                    <div className="tm-card" style={{ padding: '16px', borderRadius: '18px', background: '#fafbfd' }}>
                      <strong>Формат приема</strong>
                      <p className="tm-muted" style={{ margin: '6px 0 0' }}>Видео, аудио или чат</p>
                    </div>
                    <AppLink className="tm-button" href={routes.questions}>
                      Начать чат
                    </AppLink>
                    <AppLink className="tm-button tm-button--dark" href={withReturnTo(routes.login, currentPageHref)}>
                      Записаться на прием
                    </AppLink>
                  </div>
                </article>

                <article className="tm-card tm-side-panel" style={{ background: 'linear-gradient(180deg, #132445 0%, #0b1630 100%)', color: '#ffffff' }}>
                  <h2 style={{ color: '#ffffff' }}>Сложный случай?</h2>
                  <p style={{ color: 'rgba(255,255,255,0.72)' }}>
                    Мы поможем подобрать нужного специалиста и подготовить документы к онлайн-консультации.
                  </p>
                  <AppLink className="tm-button tm-button--soft" href={routes.questions}>
                    Связаться с консъержем
                  </AppLink>
                </article>
              </aside>
            </div>
          ) : null}
        </div>
      </section>
    </TelemedPage>
  )
}

export default DoctorPublicProfilePage
