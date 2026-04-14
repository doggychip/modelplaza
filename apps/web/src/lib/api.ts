// Use relative URL so requests go through Next.js rewrites (which proxy to the backend)
const API_BASE = "/api/v1";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API error");
  }

  return res.json();
}

// Auth
export const login = (username: string, password: string) =>
  apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

export const register = (
  username: string,
  email: string,
  password: string
) =>
  apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });

export const getMe = () => apiFetch("/auth/me");

// Models
export const listModels = (params?: Record<string, string>) => {
  const query = params ? "?" + new URLSearchParams(params).toString() : "";
  return apiFetch(`/models${query}`);
};

export const getModel = (owner: string, slug: string) =>
  apiFetch(`/models/${owner}/${slug}`);

export const createModel = (data: Record<string, unknown>) =>
  apiFetch("/models", { method: "POST", body: JSON.stringify(data) });

export const getProvenance = (owner: string, slug: string) =>
  apiFetch(`/models/${owner}/${slug}/provenance`);
