import { authHeaders } from './auth';
import type { TokenPair, AuthUser } from './auth';
import type { Patient, MRIScan, Prediction, Report } from '@/types';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init.headers ?? {})
    }
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(body.detail ?? 'Request failed', res.status);
  }

  return res.json();
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export async function registerUser(payload: RegisterPayload): Promise<AuthUser> {
  return request<AuthUser>('/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function loginUser(payload: LoginPayload): Promise<TokenPair> {
  const form = new URLSearchParams();
  form.append('username', payload.email);
  form.append('password', payload.password);
  return request<TokenPair>('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString()
  });
}

export async function getPatients() {
  return request<Patient[]>('/api/v1/patients/');
}

export async function searchPatients(query: string) {
  const params = new URLSearchParams({ q: query });
  return request<Patient[]>(`/api/v1/patients/?${params.toString()}`);
}

export async function getPatient(id: string) {
  return request<Patient>(`/api/v1/patients/${id}`);
}

export async function createPatient(payload: Omit<Patient, 'id' | 'created_at'>) {
  return request<Patient>('/api/v1/patients/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function updatePatient(
  id: string,
  payload: Partial<
    Pick<
      Patient,
      | 'first_name'
      | 'last_name'
      | 'age'
      | 'gender'
      | 'phone'
      | 'address'
      | 'medical_record_number'
      | 'ocr_patient_id'
    >
  >
) {
  return request<Patient>(`/api/v1/patients/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function deletePatient(id: string) {
  return request<{ message: string }>(`/api/v1/patients/${id}`, {
    method: 'DELETE'
  });
}

export async function uploadScans(patientId: string, form: FormData) {
  return request<MRIScan>(`/api/v1/patients/${patientId}/scans`, {
    method: 'POST',
    body: form
  });
}

export async function createPrediction(scanId: string) {
  return request<Prediction>('/api/v1/predictions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scan_id: scanId })
  });
}

export async function getPrediction(id: string) {
  return request<Prediction>(`/api/v1/predictions/${id}`);
}

export async function createReport(predictionId: string) {
  return request<Report>('/api/v1/reports/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prediction_id: predictionId })
  });
}

export async function getReport(id: string) {
  return request<Report>(`/api/v1/reports/${id}`);
}

export async function healthCheck() {
  return request<{ status: string }>('/health');
}