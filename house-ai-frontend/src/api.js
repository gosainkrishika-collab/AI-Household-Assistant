/**
 * ----------------------------------------------------------------------
 * BACKEND CALLS
 * ----------------------------------------------------------------------
 * Every request to your FastAPI backend goes through request() below.
 * It adds the login token (saved in the browser) to each call.
 *
 * Requires VITE_API_URL to be set (in a local .env file, and as an
 * Environment Variable in your frontend's Vercel project settings) to
 * your backend's deployed URL, e.g. https://your-backend.vercel.app
 * ----------------------------------------------------------------------
 */
const API_URL = import.meta.env.VITE_API_URL;

// The login token lives in localStorage so you stay logged in after a refresh
export const getToken = () => localStorage.getItem("token");
export const saveToken = (token) => localStorage.setItem("token", token);
export const clearToken = () => localStorage.removeItem("token");

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (getToken()) headers.Authorization = `Bearer ${getToken()}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    // Token expired or invalid -> send the user back to the login page
    if (res.status === 401 && getToken()) {
      clearToken();
      window.location.href = "/login";
    }
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

// ---------------- Authentication ----------------
export async function signup(name, email, password) {
  const data = await request("/signup", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
  saveToken(data.token);
  return data.user;
}

export async function login(email, password) {
  const data = await request("/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  saveToken(data.token);
  return data.user;
}

export const getMe = () => request("/me");

export async function logout() {
  try {
    await request("/logout", { method: "POST" });
  } finally {
    clearToken();
  }
}

// ---------------- Assistant ----------------
// Your graph handles query classification (food / appliance / energy)
// and recommendation generation internally — this just sends the raw
// query and returns whatever text comes back.
export async function askAssistant(message) {
  const data = await request("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
  return data.response;
}

// ---------------- History ----------------
export const getHistory = () => request("/history");
export const getHistoryItem = (id) => request(`/history/${id}`);
