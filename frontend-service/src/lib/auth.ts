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

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [key, ...valueParts] = cookie.trim().split('=');
    if (key === name) {
      return valueParts.join('=');
    }
  }
  return null;
}

function deleteCookie(name: string): void {
  if (typeof document === 'undefined') return;
  // Must match backend cookie settings: path=/, samesite=lax, secure (if production)
  const isProduction = typeof window !== 'undefined' && window.location.hostname !== 'localhost';
  const secure = isProduction ? '; secure' : '';
  document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; samesite=lax' + secure;
}

export function saveTokens(pair: TokenPair): void {
  // Tokens are now stored in httpOnly cookies by backend - no action needed
  // But we keep this for compatibility with token refresh responses
}

export function clearTokens(): void {
  deleteCookie(TOKEN_KEY);
  deleteCookie(REFRESH_KEY);
}

export function getAccessToken(): string | null {
  return getCookie(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return getCookie(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

export function authHeaders(): HeadersInit {
  // Tokens now in httpOnly cookies - browser sends them automatically
  // This function kept for backward compatibility
  return {};
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
  // For cookie-based auth, we don't need to read tokens from JS
  // Cookies are sent automatically with credentials: 'include'
  // Just make the request - if 401, redirect to login

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers as Record<string, string>),
    },
  });

  if (res.status === 401) {
    window.location.href = '/auth/login';
    throw new Error('Not authenticated');
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
