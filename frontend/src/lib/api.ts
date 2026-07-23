const API_BASE = "/api/v1";
const TOKEN_KEY = "medical_kb_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> | undefined),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export type Citation = {
  document_id: string;
  chunk_id?: string | null;
  page_number: number | null;
  excerpt: string;
  score?: number;
};

export type ChatResponse = {
  conversation_id: string;
  answer: string;
  citations: Citation[];
};

export type DocumentSummary = {
  id: string;
  filename: string;
  status: string;
};

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<{ email: string; role: string }>("/auth/me"),

  documents: () => request<DocumentSummary[]>("/documents"),

  chat: (message: string, conversationId?: string, documentIds?: string[]) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId ?? null,
        document_ids: documentIds ?? null,
      }),
    }),

  dashboard: () => request<Record<string, unknown>>("/platform/dashboard"),
};
