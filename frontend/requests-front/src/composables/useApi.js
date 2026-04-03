// composables/useApi.js
const BASE_URL = 'http://127.0.0.1:8000/api'

export function useApi() {
  const getHeaders = () => {
    const token = localStorage.getItem('token')
    const headers = { 'Content-Type': 'application/json' }
    // ✅ Only attach Authorization if a token actually exists
    if (token) headers['Authorization'] = `Token ${token}`
    return headers
  }

  const get = (path) => fetch(`${BASE_URL}${path}`, { headers: getHeaders() })
  const post = (path, body) =>
    fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    })

  return { get, post }
}
