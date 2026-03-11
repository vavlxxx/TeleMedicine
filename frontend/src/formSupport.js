import { useCallback, useRef } from 'react'
import { ApiError } from './api/client'

export function normalizeUsernameValue(value) {
  return value.trim().toLowerCase()
}

export function normalizeOptionalTextValue(value) {
  return value.trim().replace(/\s+/g, ' ')
}

export function normalizeMultilineTextValue(value) {
  return value
    .split('\n')
    .map((line) => line.trimEnd())
    .join('\n')
    .trim()
}

export function resolveFormApiError(
  error,
  { defaultMessage = 'Не удалось выполнить запрос. Попробуйте ещё раз.', statusMessages = {} } = {},
) {
  if (error instanceof ApiError) {
    return {
      fieldErrors: error.fieldErrors || {},
      formError: statusMessages[error.status] || error.message || defaultMessage,
    }
  }

  return {
    fieldErrors: {},
    formError: defaultMessage,
  }
}

export function useSubmitLock() {
  const isLockedRef = useRef(false)

  return useCallback(async (task) => {
    if (isLockedRef.current) {
      return undefined
    }

    isLockedRef.current = true

    try {
      return await task()
    } finally {
      isLockedRef.current = false
    }
  }, [])
}
