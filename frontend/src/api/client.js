const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail || 'API request failed')
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export const apiClient = {
  registerPatient(payload) {
    return request('/auth/register/patient', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  login(payload) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  me(accessToken) {
    return request('/auth/me', {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
  },
  refresh() {
    return request('/auth/refresh', { method: 'POST' })
  },
  listQuestions() {
    return request('/questions/')
  },
}
