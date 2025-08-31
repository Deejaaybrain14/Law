// src/api.js
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "dev-key";

export async function fetchEventos(rol, limit = 20, order = "desc") {
  const url = `${API_URL}/eventos?rol=${encodeURIComponent(rol)}&limit=${limit}&order=${order}`;
  const res = await fetch(url, { headers: { "X-API-Key": API_KEY } });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Error ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}
