import { useEffect, useMemo, useState } from 'react'
import { ApiError, apiClient } from './api/client'
import { useAuth } from './auth/AuthContext'
import { AppLink } from './router'
import { getDefaultAuthenticatedPath, routes } from './routes'
import { buildDoctorProfileHref, getDisplayName, getInitials, parsePositiveInteger } from './publicPageUtils'
import { TelemedPage } from './TelemedLayout'
import { getDoctorVisualProfile } from './telemedReference'

const DOCTORS_PAGE_SIZE = 18

function DoctorDirectoryWithFiltersPage() {
  const auth = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSpecializationId, setSelectedSpecializationId] = useState(null)
  const [minimumExperience, setMinimumExperience] = useState(0)
  const [minimumRating, setMinimumRating] = useState(0)
  const [minimumPrice, setMinimumPrice] = useState('')
  const [maximumPrice, setMaximumPrice] = useState('')
  const [onlineOnly, setOnlineOnly] = useState(false)

  const [specializations, setSpecializations] = useState([])
  const [doctors, setDoctors] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let isCancelled = false

    const loadData = async () => {
      setIsLoading(true)
      setErrorMessage('')

      try {
        const [specializationsResponse, doctorsResponse] = await Promise.all([
          apiClient.listSpecializations(),
          apiClient.listDoctors({ offset: 0, limit: DOCTORS_PAGE_SIZE }),
        ])

        if (!isCancelled) {
          setSpecializations(specializationsResponse)
          setDoctors(doctorsResponse)
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(error instanceof ApiError ? error.message : 'Не удалось загрузить каталог врачей')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadData()

    return () => {
      isCancelled = true
    }
  }, [])

  const enrichedDoctors = useMemo(
    () =>
      doctors.map((doctor) => ({
        ...doctor,
        visualProfile: getDoctorVisualProfile(doctor),
      })),
    [doctors],
  )

  const filteredDoctors = useMemo(() => {
    const normalizedSearch = searchQuery.trim().toLowerCase()

    return enrichedDoctors.filter((doctor) => {
      const specializationMatches =
        !selectedSpecializationId ||
        doctor.specializations.some((item) => item.id === selectedSpecializationId)

      const searchMatches =
        !normalizedSearch ||
        getDisplayName(doctor).toLowerCase().includes(normalizedSearch) ||
        doctor.specializations.some((item) => item.name.toLowerCase().includes(normalizedSearch))

      const experienceValue = parsePositiveInteger(doctor.visualProfile.experience.match(/\d+/)?.[0]) || 0
      const ratingMatches = Number(doctor.visualProfile.rating) >= minimumRating
      const experienceMatches = experienceValue >= minimumExperience
      const priceMatches =
        (!minimumPrice || doctor.visualProfile.price >= Number(minimumPrice)) &&
        (!maximumPrice || doctor.visualProfile.price <= Number(maximumPrice))
      const onlineMatches = !onlineOnly || doctor.is_online

      return specializationMatches && searchMatches && ratingMatches && experienceMatches && priceMatches && onlineMatches
    })
  }, [
    enrichedDoctors,
    maximumPrice,
    minimumExperience,
    minimumPrice,
    minimumRating,
    onlineOnly,
    searchQuery,
    selectedSpecializationId,
  ])

  const actionHref = auth.isAuthenticated ? getDefaultAuthenticatedPath(auth.user) : routes.login
  const actionLabel = auth.isAuthenticated ? 'Личный кабинет' : 'Войти'

  return (
    <TelemedPage
      activeNav="doctors"
      actionHref={actionHref}
      actionLabel={actionLabel}
      searchPlaceholder="Поиск врача или услуги"
      searchValue={searchQuery}
      onSearchChange={(event) => setSearchQuery(event.target.value)}
    >
      <section className="tm-page-section">
        <div className="tm-shell">
          <div className="tm-breadcrumbs">
            <span>Главная</span>
            <span>Каталог врачей</span>
          </div>

          <div className="tm-page-hero">
            <div>
              <h1>Специалисты онлайн</h1>
              <p>Найдите подходящего врача и перейдите в детальную карточку для консультации.</p>
            </div>
          </div>

          <div className="tm-chip-row">
            <button
              className={`tm-chip ${selectedSpecializationId === null ? 'is-active' : ''}`}
              type="button"
              onClick={() => setSelectedSpecializationId(null)}
            >
              Все врачи
            </button>
            {specializations.map((specialization) => (
              <button
                key={specialization.id}
                className={`tm-chip ${selectedSpecializationId === specialization.id ? 'is-active' : ''}`}
                type="button"
                onClick={() => setSelectedSpecializationId(specialization.id)}
              >
                {specialization.name}
              </button>
            ))}
          </div>

          <div className="tm-grid tm-directory-layout">
            <aside className="tm-card tm-filter-panel">
              <div className="tm-filter-panel__header">
                <h2>Фильтры</h2>
                <button className="tm-button tm-button--ghost" type="button" onClick={() => {
                  setSelectedSpecializationId(null)
                  setMinimumExperience(0)
                  setMinimumRating(0)
                  setMinimumPrice('')
                  setMaximumPrice('')
                  setOnlineOnly(false)
                  setSearchQuery('')
                }}>
                  Сбросить
                </button>
              </div>

              <div className="tm-field-stack">
                <div className="tm-field-block">
                  <label className="tm-field-label">
                    <span className="material-symbols-outlined">medical_services</span>
                    Специальность
                  </label>
                  <select
                    className="tm-select"
                    value={selectedSpecializationId || ''}
                    onChange={(event) => setSelectedSpecializationId(parsePositiveInteger(event.target.value))}
                  >
                    <option value="">Все специальности</option>
                    {specializations.map((specialization) => (
                      <option key={specialization.id} value={specialization.id}>
                        {specialization.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="tm-field-block">
                  <label className="tm-field-label">
                    <span className="material-symbols-outlined">radio_button_checked</span>
                    Сейчас на сайте
                  </label>
                  <label className="tm-checkbox">
                    <input
                      type="checkbox"
                      checked={onlineOnly}
                      onChange={(event) => setOnlineOnly(event.target.checked)}
                    />
                    Только врачи онлайн
                  </label>
                </div>

                <div className="tm-field-block">
                  <label className="tm-field-label">
                    <span className="material-symbols-outlined">workspace_premium</span>
                    Опыт работы
                  </label>
                  <div className="tm-checkbox-list">
                    {[0, 5, 10, 15].map((years) => (
                      <label className="tm-checkbox" key={years}>
                        <input
                          type="radio"
                          name="experience"
                          checked={minimumExperience === years}
                          onChange={() => setMinimumExperience(years)}
                        />
                        {years === 0 ? 'Любой стаж' : `Более ${years} лет`}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="tm-field-block">
                  <label className="tm-field-label">
                    <span className="material-symbols-outlined">payments</span>
                    Стоимость приема
                  </label>
                  <div className="tm-inline-meta">
                    <input
                      className="tm-input"
                      type="number"
                      placeholder="От"
                      value={minimumPrice}
                      onChange={(event) => setMinimumPrice(event.target.value)}
                    />
                    <input
                      className="tm-input"
                      type="number"
                      placeholder="До"
                      value={maximumPrice}
                      onChange={(event) => setMaximumPrice(event.target.value)}
                    />
                  </div>
                </div>

                <div className="tm-field-block">
                  <label className="tm-field-label">
                    <span className="material-symbols-outlined">star</span>
                    Рейтинг
                  </label>
                  <div className="tm-checkbox-list">
                    {[0, 4.5, 4.8].map((value) => (
                      <label className="tm-checkbox" key={value}>
                        <input
                          type="radio"
                          name="rating"
                          checked={minimumRating === value}
                          onChange={() => setMinimumRating(value)}
                        />
                        {value === 0 ? 'Любой рейтинг' : `${value}+`}
                      </label>
                    ))}
                  </div>
                </div>

                <button className="tm-button" type="button">
                  Применить
                </button>
              </div>
            </aside>

            <div>
              {isLoading ? (
                <section className="tm-card tm-empty-state">
                  <h2>Загружаем каталог</h2>
                  <p>Подтягиваем список врачей и справочник специализаций.</p>
                </section>
              ) : null}

              {!isLoading && errorMessage ? (
                <section className="tm-card tm-empty-state">
                  <h2>Каталог не загрузился</h2>
                  <p>{errorMessage}</p>
                </section>
              ) : null}

              {!isLoading && !errorMessage ? (
                <>
                  <div className="tm-results-grid">
                    {filteredDoctors.map((doctor) => (
                      <article className="tm-card tm-doctor-card" key={doctor.id}>
                        <div
                          className="tm-doctor-card__visual"
                          style={{ background: doctor.visualProfile.theme.background }}
                        >
                          <span className="tm-rating-badge">
                            <span className="material-symbols-outlined">star</span>
                            {doctor.visualProfile.rating}
                          </span>
                          {doctor.is_online ? (
                            <span className="tm-online-badge">
                              <span className="tm-online-dot" aria-hidden="true" />
                              Сейчас на сайте
                            </span>
                          ) : null}
                          <div className="tm-doctor-portrait" aria-hidden="true">
                            {getInitials(doctor)}
                          </div>
                        </div>

                        <div className="tm-doctor-card__body">
                          <div>
                            <div className="tm-overline">
                              {doctor.specializations[0]?.name || 'Специалист'}
                            </div>
                            <h2 className="tm-doctor-card__title">{getDisplayName(doctor)}</h2>
                            <p className="tm-muted">
                              {doctor.visualProfile.experience} · {doctor.visualProfile.qualification}
                            </p>
                          </div>

                          <div className="tm-price-row">
                            <div>
                              <span className="tm-overline">Прием от</span>
                              <strong>{doctor.visualProfile.price.toLocaleString('ru-RU')} ₽</strong>
                            </div>
                            <AppLink className="tm-button tm-button--soft" href={buildDoctorProfileHref(doctor.id)}>
                              Записаться
                            </AppLink>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>

                  {!filteredDoctors.length ? (
                    <section className="tm-card tm-empty-state" style={{ marginTop: '22px' }}>
                      <h2>Ничего не найдено</h2>
                      <p>Измените фильтры или попробуйте другой поисковый запрос.</p>
                    </section>
                  ) : null}

                  <div className="tm-pagination">
                    <button type="button">‹</button>
                    <button className="is-active" type="button">1</button>
                    <button type="button">2</button>
                    <button type="button">3</button>
                    <button type="button">›</button>
                  </div>
                </>
              ) : null}
            </div>
          </div>
        </div>
      </section>
    </TelemedPage>
  )
}

export default DoctorDirectoryWithFiltersPage
