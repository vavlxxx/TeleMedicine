import { AppLink } from './router'
import { routes } from './routes'

function TelemedLogo() {
  return (
    <span className="tm-logo">
      <span className="tm-logo__mark" aria-hidden="true">
        <span className="tm-logo__cross tm-logo__cross--horizontal" />
        <span className="tm-logo__cross tm-logo__cross--vertical" />
      </span>
      <span className="tm-logo__text">TelemedRU</span>
    </span>
  )
}

function SearchField({ placeholder = 'Поиск врача или услуги', value = '', onChange = null }) {
  return (
    <label className="tm-search">
      <span className="material-symbols-outlined">search</span>
      {onChange ? (
        <input
          type="search"
          placeholder={placeholder}
          value={value}
          onChange={onChange}
        />
      ) : (
        <input type="search" placeholder={placeholder} defaultValue={value} />
      )}
    </label>
  )
}

export function TelemedHeader({
  active = 'doctors',
  actionLabel = 'Войти',
  actionHref = routes.login,
  searchPlaceholder = 'Поиск врача или услуги',
  searchValue = '',
  onSearchChange = null,
}) {
  const navItems = [
    { key: 'doctors', label: 'Врачи', href: routes.doctors },
    { key: 'questions', label: 'Вопросы', href: routes.questions },
  ]

  return (
    <header className="tm-header">
      <div className="tm-shell tm-header__inner">
        <AppLink href={routes.landing} className="tm-header__brand">
          <TelemedLogo />
        </AppLink>

        <nav className="tm-header__nav" aria-label="Основная навигация">
          {navItems.map((item) => (
            <AppLink
              key={item.key}
              href={item.href}
              className={`tm-header__link ${active === item.key ? 'is-active' : ''}`}
            >
              {item.label}
            </AppLink>
          ))}
        </nav>

        <SearchField
          placeholder={searchPlaceholder}
          value={searchValue}
          onChange={onSearchChange}
        />

        <div className="tm-header__actions">
          <AppLink href={actionHref} className="tm-button tm-button--dark">
            {actionLabel}
          </AppLink>
          <span className="tm-header__avatar" aria-hidden="true">
            <span className="material-symbols-outlined">person</span>
          </span>
        </div>
      </div>
    </header>
  )
}

export function TelemedFooter() {
  return (
    <footer className="tm-footer">
      <div className="tm-shell tm-footer__inner">
        <div className="tm-footer__brand">
          <TelemedLogo />
          <p>
            Профессиональные медицинские консультации онлайн. Помогаем быстро получить второе
            мнение и выбрать врача.
          </p>
        </div>

        <div className="tm-footer__column">
          <h3>Пациентам</h3>
          <AppLink href={routes.doctors}>Каталог врачей</AppLink>
          <AppLink href={routes.questions}>Открытые вопросы</AppLink>
          <AppLink href={routes.login}>Вход</AppLink>
        </div>

        <div className="tm-footer__column">
          <h3>Платформа</h3>
          <AppLink href={routes.landing}>Главная</AppLink>
          <AppLink href={routes.register}>Регистрация</AppLink>
          <AppLink href={routes.admin}>Админ панель</AppLink>
        </div>

        <div className="tm-footer__column">
          <h3>Поддержка</h3>
          <a href="tel:88005553535">8 (800) 555-35-35</a>
          <a href="mailto:help@telemed.ru">help@telemed.ru</a>
          <span>Ежедневно 08:00-22:00</span>
        </div>
      </div>
    </footer>
  )
}

export function TelemedPage({
  activeNav,
  actionLabel,
  actionHref,
  children,
  searchPlaceholder,
  searchValue,
  onSearchChange,
}) {
  return (
    <div className="tm-page">
      <TelemedHeader
        active={activeNav}
        actionLabel={actionLabel}
        actionHref={actionHref}
        searchPlaceholder={searchPlaceholder}
        searchValue={searchValue}
        onSearchChange={onSearchChange}
      />
      <main className="tm-main">{children}</main>
      <TelemedFooter />
    </div>
  )
}

export function TelemedAuthFrame({ children, subtitle, title }) {
  return (
    <main className="tm-auth">
      <div className="tm-auth__topbar">
        <div className="tm-auth__topbar-inner">
          <AppLink href={routes.landing} className="tm-auth__brand">
            <TelemedLogo />
          </AppLink>
          <span className="tm-auth__support">Помощь</span>
        </div>
      </div>

      <div className="tm-auth__body">
        <section className="tm-auth__card">
          <div className="tm-auth__card-brand">
            <TelemedLogo />
          </div>
          <header className="tm-auth__header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </header>
          {children}
        </section>
      </div>
    </main>
  )
}
