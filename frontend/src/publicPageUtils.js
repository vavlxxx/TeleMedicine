import { normalizeMultilineTextValue } from './formSupport'
import { routes } from './routes'

export function getDisplayName(person) {
  const fullName = [person?.first_name, person?.last_name].filter(Boolean).join(' ').trim()
  return fullName || person?.username || 'Неизвестный пользователь'
}

export function getUsernameLabel(person) {
  return person?.username ? `@${person.username}` : 'Профиль недоступен'
}

export function formatDateTime(value) {
  if (!value) {
    return ''
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return ''
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function getInitials(person) {
  const initials = [person?.first_name?.[0], person?.last_name?.[0]].filter(Boolean).join('')

  if (initials) {
    return initials.slice(0, 2).toUpperCase()
  }

  return (person?.username || 'TM').slice(0, 2).toUpperCase()
}

export function parsePositiveInteger(value) {
  if (!value) {
    return null
  }

  const parsedValue = Number.parseInt(value, 10)
  return Number.isInteger(parsedValue) && parsedValue > 0 ? parsedValue : null
}

export function trimMultilineText(value) {
  return normalizeMultilineTextValue(value)
}

export function formatFileSize(sizeBytes) {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0) {
    return '0 Б'
  }

  const units = ['Б', 'КБ', 'МБ', 'ГБ']
  let value = sizeBytes
  let unitIndex = 0

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }

  const digits = value >= 10 || unitIndex === 0 ? 0 : 1
  return `${value.toFixed(digits)} ${units[unitIndex]}`
}

export function downloadBlobFile(blob, fileName) {
  const objectUrl = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')

  anchor.href = objectUrl
  anchor.download = fileName || 'download'
  document.body.append(anchor)
  anchor.click()
  anchor.remove()

  window.setTimeout(() => {
    window.URL.revokeObjectURL(objectUrl)
  }, 0)
}

export function buildDoctorProfileHref(doctorId) {
  return `${routes.doctorProfile}?doctor_id=${doctorId}`
}

export function buildQuestionHref(questionId) {
  return `${routes.questionDetail}?question_id=${questionId}`
}
