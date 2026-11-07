const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8787/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  home: () => request<any>("/home"),
  signals: (category?: string) => request<any>(`/signals${category ? `?category=${category}` : ""}`),
  convergences: () => request<any>("/convergences"),
  ideas: (status = "all") => request<any>(`/ideas?status=${status}`),
  idea: (id: string) => request<any>(`/ideas/${id}`),
  prototypes: () => request<any>("/prototypes"),
  resurrections: () => request<any>("/resurrections"),
  memory: () => request<any>("/memory"),
  runs: () => request<any>("/runs"),
  run: (id: string) => request<any>(`/runs/${id}`),
  modes: () => request<any>("/modes"),
  analytics: () => request<any>("/analytics/overview"),
  evaluation: () => request<any>("/analytics/evaluation"),
  startRun: (body: { mode: string; theme?: string; dry_run?: boolean; build?: boolean }) =>
    request<any>("/runs/start", { method: "POST", body: JSON.stringify(body) }),
  feedback: (ideaId: string, body: { reaction: string; action?: string }) =>
    request<any>(`/ideas/${ideaId}/feedback`, { method: "POST", body: JSON.stringify(body) }),
};

export type Idea = {
  id: string;
  name: string;
  one_liner: string;
  score: number;
  score_band: string;
  status: string;
  why_now?: string;
  mode?: string;
  is_demo?: boolean;
};
