import { useEffect, useMemo, useState } from 'react'
import { ApiError, apiClient } from './api/client'
import { AppLink, useRouter } from './router'
import { routes, withReturnTo } from './routes'
import { formatDateTime, getDisplayName, getInitials, parsePositiveInteger } from './publicPageUtils'
import { VirtualMedicPage } from './VirtualMedicLayout'
import { getDoctorVisualProfile } from './virtualmedicReference'

const profileTabs = [
  { key: 'about', label: 'О враче' },
  { key: 'reviews', label: 'Отзывы' },
  { key: 'consultations', label: 'Консультации' },
  { key: 'certificates', label: 'Сертификаты' },
]

const numberFormatter = new Intl.NumberFormat('ru-RU')

function DoctorPublicProfilePage() {
  const { location } = useRouter()
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search])
  const doctorId = parsePositiveInteger(searchParams.get('doctor_id'))
  const currentPageHref = `${location.pathname}${location.search}${location.hash || ''}`

  const [doctor, setDoctor] = useState(null)
  const [isLoading, setIsLoading] = useState(Boolean(doctorId))
  const [errorMessage, setErrorMessage] = useState('')
  const [activeTab, setActiveTab] = useState(profileTabs[0].key)

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
  const mainSpecialization = doctor?.specializations[0]?.name || 'Врач'
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
  const tabBadges = visualProfile
    ? {
        reviews: visualProfile.reviewsCount,
        consultations: visualProfile.consultationsCount,
        certificates: visualProfile.certificatesCount,
      }
    : {}

  const renderTabContent = () => {
    if (!doctor || !visualProfile) {
      return null
    }

    if (activeTab === 'reviews') {
      return (
        <section className="vm-profile-tab-panel">
          <div className="vm-question-card__row">
            <h2>Отзывы пациентов</h2>
            <span className="vm-link">{numberFormatter.format(visualProfile.reviewsCount)} отзывов</span>
          </div>

          <div className="vm-review-grid">
            {reviewCards.map((review) => (
              <article className="vm-card vm-review-card" key={review.author}>
                <div className="vm-inline-meta">
                  <div className="vm-doctor-portrait vm-review-card__avatar">
                    {review.author.split(' ').map((part) => part[0]).join('')}
                  </div>
                  <div>
                    <strong>{review.author}</strong>
                    <div className="vm-muted">{formatDateTime(new Date().toISOString())}</div>
                  </div>
                </div>
                <p>{review.text}</p>
              </article>
            ))}
          </div>
        </section>
      )
    }

    if (activeTab === 'consultations') {
      return (
        <section className="vm-profile-tab-panel">
          <h2>Консультации</h2>
          <div className="vm-profile-info-grid">
            <div>
              <span className="vm-overline">Формат</span>
              <strong>Видео, аудио или чат</strong>
              <p className="vm-muted">Подходит для первичной консультации, разбора анализов и уточнения тактики лечения.</p>
            </div>
            <div>
              <span className="vm-overline">Ближайший слот</span>
              <strong>{visualProfile.eta}, 14:30 (мск)</strong>
              <p className="vm-muted">После записи пациент получает подтверждение и ссылку на онлайн-прием.</p>
            </div>
          </div>
        </section>
      )
    }

    if (activeTab === 'certificates') {
      return (
        <section className="vm-profile-tab-panel">
          <h2>Сертификаты</h2>
          <div className="vm-profile-certificate-list">
            <div>
              <span className="material-symbols-outlined">workspace_premium</span>
              <div>
                <strong>Действующий сертификат специалиста</strong>
                <p className="vm-muted">Подтвержден платформой при модерации профиля врача.</p>
              </div>
            </div>
            <div>
              <span className="material-symbols-outlined">verified_user</span>
              <div>
                <strong>Документы об образовании</strong>
                <p className="vm-muted">Проверено документов: {visualProfile.certificatesCount}.</p>
              </div>
            </div>
          </div>
        </section>
      )
    }

    return (
      <section className="vm-profile-tab-panel">
        <h2>О враче</h2>
        <p>
          {mainSpecialization} помогает пациентам дистанционно: оценивает симптомы, разбирает результаты
          исследований, объясняет риски и формирует понятный план дальнейших действий.
        </p>

        <h2>Специализация в лечении пациентов</h2>
        <p>
          Консультации проходят по направлениям: {doctor.specializations.map((item) => item.name).join(', ') || 'общая медицина'}.
          Врач работает с повторными обращениями, подготовкой к очному приему и сопровождением после назначений.
        </p>

        <h2>Опыт и образование</h2>
        <div className="vm-timeline">
          <div className="vm-timeline-item">
            <span className="vm-overline">2018 — наст. время</span>
            <h3>Ведущий специалист онлайн-консультаций</h3>
            <p className="vm-muted">Практика по направлению {mainSpecialization.toLowerCase()}.</p>
          </div>
          <div className="vm-timeline-item">
            <span className="vm-overline">2013 — 2018</span>
            <h3>Врач амбулаторного приема</h3>
            <p className="vm-muted">Работа с хроническими пациентами и сопровождением после лечения.</p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <VirtualMedicPage
      activeNav="doctors"
      actionLabel="Личный кабинет"
      actionHref={withReturnTo(routes.login, currentPageHref)}
    >
      <section className="vm-page-section">
        <div className="vm-shell">
          <div className="vm-breadcrumbs">
            <span>Главная</span>
            <span>Кардиология</span>
            <span>{doctor ? getDisplayName(doctor) : 'Профиль врача'}</span>
          </div>

          {!doctorId ? (
            <section className="vm-card vm-empty-state">
              <h2>Врач не выбран</h2>
              <p>Вернитесь в каталог и откройте карточку нужного врача.</p>
              <AppLink className="vm-button" href={routes.doctors}>
                В каталог врачей
              </AppLink>
            </section>
          ) : null}

          {isLoading ? (
            <section className="vm-card vm-empty-state">
              <h2>Загружаем профиль врача</h2>
              <p>Получаем публичные данные врача по `doctor_id`.</p>
            </section>
          ) : null}

          {!isLoading && errorMessage ? (
            <section className="vm-card vm-empty-state">
              <h2>Профиль не открылся</h2>
              <p>{errorMessage}</p>
              <AppLink className="vm-button" href={routes.doctors}>
                Назад к каталогу
              </AppLink>
            </section>
          ) : null}

          {doctor && visualProfile ? (
            <div className="vm-profile-layout">
              <aside className="vm-profile-sidebar">
                <article className="vm-card vm-profile-identity-card">
                  <div
                    className="vm-doctor-portrait vm-profile-identity-card__portrait"
                    style={{ background: visualProfile.theme.background }}
                    aria-hidden="true"
                  >
                    {getInitials(doctor)}
                  </div>

                  <div className={doctor.is_online ? 'vm-profile-presence is-online' : 'vm-profile-presence'}>
                    <span className="vm-online-dot" aria-hidden="true" />
                    {doctor.is_online ? 'Сейчас на сайте' : `Заходил(a): ${visualProfile.eta}`}
                  </div>

                  <div className="vm-profile-rating-row" aria-label={`Рейтинг ${visualProfile.rating}`}>
                    {Array.from({ length: 5 }).map((_, index) => (
                      <span className="material-symbols-outlined" key={index}>star</span>
                    ))}
                  </div>

                  <AppLink className="vm-button" href={withReturnTo(routes.login, currentPageHref)}>
                    Консультация {visualProfile.price.toLocaleString('ru-RU')} ₽
                  </AppLink>
                  <AppLink className="vm-button vm-button--success" href={routes.questions}>
                    Благодарность врачу
                  </AppLink>
                </article>
              </aside>

              <div className="vm-grid">
                <article className="vm-card vm-profile-summary-card">
                  <div className="vm-profile-summary-card__header">
                    <div>
                      <div className="vm-inline-meta">
                        <span className="vm-verified-strip">
                          <span className="material-symbols-outlined">verified</span>
                          Проверенный эксперт
                        </span>
                        {doctor.is_online ? (
                          <span className="vm-online-chip">
                            <span className="vm-online-dot" aria-hidden="true" />
                            Онлайн
                          </span>
                        ) : null}
                      </div>
                      <h1 className="vm-profile-hero__title">{getDisplayName(doctor)}</h1>
                      <p className="vm-muted">{doctor.specializations.map((item) => item.name).join(', ') || 'Врач'}</p>
                    </div>
                  </div>

                  <dl className="vm-profile-info-list">
                    <div>
                      <dt>Место работы</dt>
                      <dd>Онлайн-клиника VirtualMedic</dd>
                    </div>
                    <div>
                      <dt>Должность</dt>
                      <dd>{mainSpecialization}</dd>
                    </div>
                    <div>
                      <dt>Общий стаж</dt>
                      <dd>{visualProfile.experience.replace('Стаж: ', '')}</dd>
                    </div>
                    <div>
                      <dt>Специализация</dt>
                      <dd>{doctor.specializations.map((item) => item.name).join(', ') || 'Не указана'}</dd>
                    </div>
                    <div>
                      <dt>Научная степень</dt>
                      <dd>{visualProfile.qualification}</dd>
                    </div>
                    <div>
                      <dt>Образование</dt>
                      <dd>Медицинский университет, лечебный факультет, врач</dd>
                    </div>
                  </dl>
                </article>

                <section className="vm-card vm-profile-stats-card">
                  <div>
                    <strong>{numberFormatter.format(visualProfile.reviewsCount)}</strong>
                    <span>Отзывов</span>
                  </div>
                  <div>
                    <strong>{numberFormatter.format(visualProfile.viewsCount)}</strong>
                    <span>Просмотров</span>
                  </div>
                  <div>
                    <strong>{numberFormatter.format(visualProfile.consultationsCount)}</strong>
                    <span>Консультаций</span>
                  </div>
                  <div>
                    <strong>{visualProfile.responseTimeHours} часа</strong>
                    <span>Время отклика</span>
                  </div>
                </section>

                <article className="vm-card vm-detail-card">
                  <div className="vm-tabbar" role="tablist" aria-label="Разделы профиля врача">
                    {profileTabs.map((item) => (
                      <button
                        className={activeTab === item.key ? 'is-active' : ''}
                        type="button"
                        role="tab"
                        aria-selected={activeTab === item.key}
                        key={item.key}
                        onClick={() => setActiveTab(item.key)}
                      >
                        <span>{item.label}</span>
                        {tabBadges[item.key] ? <strong>{numberFormatter.format(tabBadges[item.key])}</strong> : null}
                      </button>
                    ))}
                  </div>

                  {renderTabContent()}
                </article>
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </VirtualMedicPage>
  )
}

export default DoctorPublicProfilePage
