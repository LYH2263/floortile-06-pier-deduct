async function readError(r) {
  const text = await r.text()
  try {
    return JSON.parse(text).detail ?? text
  } catch {
    return text
  }
}
export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await readError(r))
  return r.json()
}
export async function postJSON(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await readError(r))
  return r.json()
}
export async function delJSON(path) {
  const r = await fetch(path, { method: 'DELETE' })
  if (!r.ok) throw new Error(await readError(r))
  return r.json()
}
