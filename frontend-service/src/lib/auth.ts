const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const TOKEN_KEY = 'rxa_access_token';
export const REFRESH_KEY = 'rxa_refresh_token';

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthUser {
  id: string;
  username: string;
  email: string;
}

export function saveTokens(pair: TokenPair): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, pair.access_token);
  localStorage.setItem(REFRESH_KEY, pair.refresh_token);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

export function authHeaders(): HeadersInit {
  const token = getAccessToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

let refreshing = false;
let refreshPromise: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (!res.ok) {
      clearTokens();
      window.location.href = '/auth/login';
      return null;
    }

    const data = await res.json();
    saveTokens(data);
    return data.access_token;
  } catch {
    clearTokens();
    window.location.href = '/auth/login';
    return null;
  }
}

export async function refreshIfNeeded(): Promise<string | null> {
  const token = getAccessToken();
  if (!token) return null;

  // Check if token is expiring soon (within 5 minutes)
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiry = payload.exp * 1000;
    const now = Date.now();
    if (expiry - now > 5 * 60 * 1000) {
      return token; // Still valid for 5+ minutes
    }
  } catch {
    // If we can't parse, try refreshing anyway
  }

  if (refreshing && refreshPromise) {
    return refreshPromise;
  }

  refreshing = true;
  refreshPromise = doRefresh();

  try {
    return await refreshPromise;
  } finally {
    refreshing = false;
    refreshPromise = null;
  }
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = await refreshIfNeeded();
  if (!token) {
    window.location.href = '/auth/login';
    throw new Error('Not authenticated');
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(init.headers as Record<string, string>),
    },
  });

  if (res.status === 401) {
    // Token was rejected, force refresh and retry once
    const newToken = await doRefresh();
    if (!newToken) {
      window.location.href = '/auth/login';
      throw new Error('Not authenticated');
    }

    const retryRes = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${newToken}`,
        ...(init.headers as Record<string, string>),
      },
    });

    if (!retryRes.ok) {
      const body = await retryRes.json().catch(() => ({ detail: retryRes.statusText }));
      throw new ApiError(body.detail ?? 'Request failed', retryRes.status);
    }

    return retryRes.json();
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(body.detail ?? 'Request failed', res.status);
  }

  return res.json();
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}
