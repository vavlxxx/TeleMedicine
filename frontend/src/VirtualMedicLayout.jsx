import { AppLink } from './router'
import { routes } from './routes'
import virtualmedicIcon from './assets/virtualmedic-icon.png'

function VirtualMedicLogo() {
  return (
    <span className="vm-logo">
      <img alt="VirtualMedic" className="vm-logo__icon" src={virtualmedicIcon} />
      <span className="vm-logo__text">VirtualMedic</span>
    </span>
  )
}

function SearchField({ placeholder = 'Поиск врача или услуги', value = '', onChange = null }) {
  return (
    <label className="vm-search">
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

export function VirtualMedicHeader({
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
    <header className="vm-header">
      <div className="vm-shell vm-header__inner">
        <AppLink href={routes.landing} className="vm-header__brand">
          <VirtualMedicLogo />
        </AppLink>

        <nav className="vm-header__nav" aria-label="Основная навигация">
          {navItems.map((item) => (
            <AppLink
              key={item.key}
              href={item.href}
              className={`vm-header__link ${active === item.key ? 'is-active' : ''}`}
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

        <div className="vm-header__actions">
          <AppLink href={actionHref} className="vm-button vm-button--dark">
            {actionLabel}
          </AppLink>
          <span className="vm-header__avatar" aria-hidden="true">
            <span className="material-symbols-outlined">person</span>
          </span>
        </div>
      </div>
    </header>
  )
}

export function VirtualMedicFooter() {
  return (
    <footer className="vm-footer">
      <div className="vm-shell vm-footer__inner">
        <div className="vm-footer__brand">
          <VirtualMedicLogo />
          <p>
            Профессиональные медицинские консультации онлайн. Помогаем быстро получить второе
            мнение и выбрать врача.
          </p>
        </div>

        <div className="vm-footer__column">
          <h3>Пациентам</h3>
          <AppLink href={routes.doctors}>Каталог врачей</AppLink>
          <AppLink href={routes.questions}>Открытые вопросы</AppLink>
          <AppLink href={routes.login}>Вход</AppLink>
        </div>

        <div className="vm-footer__column">
          <h3>Платформа</h3>
          <AppLink href={routes.landing}>Главная</AppLink>
          <AppLink href={routes.register}>Регистрация</AppLink>
          <AppLink href={routes.admin}>Админ панель</AppLink>
        </div>

        <div className="vm-footer__column">
          <h3>Поддержка</h3>
          <a href="tel:88005553535">8 (800) 555-35-35</a>
          <a href="mailto:help@virtualmedic.ru">help@virtualmedic.ru</a>
          <span>Ежедневно 08:00-22:00</span>
        </div>
      </div>
    </footer>
  )
}

export function VirtualMedicPage({
  activeNav,
  actionLabel,
  actionHref,
  children,
  searchPlaceholder,
  searchValue,
  onSearchChange,
}) {
  return (
    <div className="vm-page">
      <VirtualMedicHeader
        active={activeNav}
        actionLabel={actionLabel}
        actionHref={actionHref}
        searchPlaceholder={searchPlaceholder}
        searchValue={searchValue}
        onSearchChange={onSearchChange}
      />
      <main className="vm-main">{children}</main>
      <VirtualMedicFooter />
    </div>
  )
}

export function VirtualMedicAuthFrame({ children, subtitle, title }) {
  return (
    <main className="vm-auth">
      <div className="vm-auth__topbar">
        <div className="vm-auth__topbar-inner">
          <AppLink href={routes.landing} className="vm-auth__brand">
            <VirtualMedicLogo />
          </AppLink>
          <span className="vm-auth__support">Помощь</span>
        </div>
      </div>

      <div className="vm-auth__body">
        <section className="vm-auth__card">
          <div className="vm-auth__card-brand">
            <VirtualMedicLogo />
          </div>
          <header className="vm-auth__header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </header>
          {children}
        </section>
      </div>
    </main>
  )
}
