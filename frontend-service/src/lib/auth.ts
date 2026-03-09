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

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

export function authHeaders(): HeadersInit {
  const token = getAccessToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}