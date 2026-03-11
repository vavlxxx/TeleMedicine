const doctorPortraitThemes = [
  { background: 'linear-gradient(135deg, #52a8b3 0%, #2b6d86 100%)', accent: '#0e7490' },
  { background: 'linear-gradient(135deg, #d6c0ae 0%, #b79274 100%)', accent: '#8b5e3c' },
  { background: 'linear-gradient(135deg, #70c3d0 0%, #2079a0 100%)', accent: '#2563eb' },
  { background: 'linear-gradient(135deg, #cad9ea 0%, #8db1d2 100%)', accent: '#1d4ed8' },
  { background: 'linear-gradient(135deg, #b9d5cb 0%, #7cb09c 100%)', accent: '#0f766e' },
]

const experienceLabels = [
  'Стаж: 6 лет',
  'Стаж: 8 лет',
  'Стаж: 12 лет',
  'Стаж: 15 лет',
  'Стаж: 18 лет',
]

const qualificationLabels = [
  'Врач высшей категории',
  'К.М.Н.',
  'Специалист телемедицины',
  'Эксперт платформы',
  'Врач первой категории',
]

const cityLabels = ['Москва', 'Екатеринбург', 'Казань', 'Новосибирск', 'Санкт-Петербург']

export function createSeedNumber(value) {
  const source = String(value || 'telemed')
  let hash = 0

  for (let index = 0; index < source.length; index += 1) {
    hash = (hash * 31 + source.charCodeAt(index)) >>> 0
  }

  return hash
}

export function getDoctorVisualProfile(doctor) {
  const seed = createSeedNumber(`${doctor?.id || ''}-${doctor?.username || ''}`)
  const theme = doctorPortraitThemes[seed % doctorPortraitThemes.length]
  const rating = (4.6 + (seed % 5) * 0.1).toFixed(1)
  const price = 1800 + (seed % 8) * 250
  const experience = experienceLabels[seed % experienceLabels.length]
  const qualification = qualificationLabels[(seed + 2) % qualificationLabels.length]
  const eta = ['Сегодня', 'Завтра', 'Через 2 дня'][seed % 3]

  return {
    theme,
    rating,
    price,
    experience,
    qualification,
    eta,
  }
}

export function getQuestionCategory(question) {
  const text = `${question?.text || ''}`.toLowerCase()

  if (/(голов|невро|мигр|сон|затыл)/.test(text)) {
    return 'Неврология'
  }
  if (/(ребен|сып|педи|темпера|кашл)/.test(text)) {
    return 'Педиатрия'
  }
  if (/(желуд|живот|подреб|гастр|тошнот)/.test(text)) {
    return 'Гастроэнтерология'
  }
  if (/(кож|сыпь|дерм|пятн)/.test(text)) {
    return 'Дерматология'
  }
  if (/(серд|давлен|карди|пульс)/.test(text)) {
    return 'Кардиология'
  }

  return 'Терапия'
}

export function formatRelativeQuestionTime(value) {
  if (!value) {
    return 'Недавно'
  }

  const targetDate = new Date(value)
  const diffMs = Date.now() - targetDate.getTime()

  if (Number.isNaN(targetDate.getTime()) || diffMs < 0) {
    return 'Недавно'
  }

  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)

  if (diffHours < 1) {
    return 'Только что'
  }
  if (diffHours < 24) {
    return `${diffHours} ч назад`
  }
  if (diffDays < 7) {
    return `${diffDays} дн назад`
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'short',
  }).format(targetDate)
}

export function getQuestionPatientMeta(question) {
  const seed = createSeedNumber(`${question?.id || ''}-${question?.author?.username || ''}`)
  const age = 24 + (seed % 23)
  const city = cityLabels[seed % cityLabels.length]

  return {
    age,
    city,
  }
}

export function summarizeQuestion(text, maxLength = 148) {
  const normalized = `${text || ''}`.replace(/\s+/g, ' ').trim()

  if (normalized.length <= maxLength) {
    return normalized
  }

  return `${normalized.slice(0, maxLength - 1).trimEnd()}…`
}
