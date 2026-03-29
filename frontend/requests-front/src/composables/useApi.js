const BASE_URL = 'http://127.0.0.1:8000/api'

export function useApi() {
  const getHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Token ${localStorage.getItem('token')}`
  })

  const get = (path) =>
    fetch(`${BASE_URL}${path}`, { headers: getHeaders() })

  const post = (path, body, auth = true) =>
    fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: auth ? getHeaders() : { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

  return { get, post }
}