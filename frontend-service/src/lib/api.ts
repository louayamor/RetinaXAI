import { authHeaders, refreshIfNeeded, getAccessToken, clearTokens } from './auth';
import type { TokenPair, AuthUser } from './auth';
import type { Patient, MRIScan, Prediction, Report, PaginatedResponse } from '@/types';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  // Ensure token is fresh before making request
  await refreshIfNeeded();

  const token = getAccessToken();
  const isFormData = init.body instanceof FormData;
  const headers: Record<string, string> = isFormData
    ? {}
    : { 'Content-Type': 'application/json', ...(init.headers as Record<string, string> || {}) };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers
  });

  // Handle 401 by clearing tokens and redirecting to login
  if (res.status === 401) {
    clearTokens();
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/login';
    }
    const body = await res.json().catch(() => ({ detail: 'Session expired. Please login again.' }));
    throw new ApiError(body.detail ?? 'Session expired', 401);
  }

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

export interface PredictionRequest {
  patient_id: string;
  mri_scan_id: string;
  model_name: string;
  model_version: string;
  input_payload: Record<string, unknown>;
}

export async function createPrediction(data: PredictionRequest) {
  return request<Prediction>('/api/v1/predictions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

export async function getPrediction(id: string) {
  return request<Prediction>(`/api/v1/predictions/${id}`);
}

export async function listPatientPredictions(
  patientId: string,
  page = 1,
  size = 20
): Promise<PaginatedResponse<Prediction>> {
  return request<PaginatedResponse<Prediction>>(
    `/api/v1/predictions/patient/${patientId}?page=${page}&size=${size}`
  );
}

export async function listAllPredictions(page = 1, size = 20): Promise<PaginatedResponse<Prediction>> {
  return request<PaginatedResponse<Prediction>>(`/api/v1/predictions/?page=${page}&size=${size}`);
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

export async function listPatientReports(
  patientId: string,
  page = 1,
  size = 20
): Promise<PaginatedResponse<Report>> {
  return request<PaginatedResponse<Report>>(
    `/api/v1/reports/patient/${patientId}?page=${page}&size=${size}`
  );
}

export async function listAllReports(page = 1, size = 20): Promise<PaginatedResponse<Report>> {
  return request<PaginatedResponse<Report>>(`/api/v1/reports/?page=${page}&size=${size}`);
}

// Async report generation (LLMOps)
interface AsyncReportResponse {
  job_id: string;
  status: string;
}

interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: Report;
  error?: string;
  progress?: number;
  created_at: string;
  updated_at: string;
}

export async function createAsyncReport(predictionId: string): Promise<AsyncReportResponse> {
  return request<AsyncReportResponse>('/api/v1/reports/async', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prediction_id: predictionId })
  });
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return request<JobStatusResponse>(`/api/v1/reports/jobs/${jobId}`);
}

export async function listJobs(): Promise<JobStatusResponse[]> {
  return request<JobStatusResponse[]>('/api/v1/reports/jobs');
}

export async function healthCheck() {
  return request<{ status: string }>('/health');
}

// Dashboard stats
export interface DashboardStats {
  totals: {
    patients: number;
    predictions: number;
    reports: number;
    scans: number;
  };
  prediction_status: Record<string, number>;
  report_status: Record<string, number>;
  severity_distribution: Record<number, number>;
  predictions_timeline: Array<{ date: string; predictions: number }>;
  age_distribution: Record<string, number>;
  gender_distribution: Record<string, number>;
  recent_activity: {
    new_patients: number;
    new_predictions: number;
    new_reports: number;
  };
  avg_confidence: number | null;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return request<DashboardStats>('/api/v1/dashboard/stats');
}

// LLMOps service API (runs on port 8002)
const LLMOPS_BASE = process.env.NEXT_PUBLIC_LLMOPS_URL ?? 'http://localhost:8002';

interface RagStatusResponse {
  status: string;
  schema_version?: string;
  run_id?: string;
  artifact_count: number;
  collection_name?: string;
  persist_directory?: string;
}

interface RagReindexResponse {
  status: string;
  result?: {
    schema_version: string;
    run_id: string;
    artifact_count: number;
    pipeline: string;
    document_count: number;
    chunk_count: number;
  };
}

const LLMOPS_API_KEY = process.env.NEXT_PUBLIC_LLMOPS_API_KEY ?? 'dev-api-key';

export async function getRagStatus(): Promise<RagStatusResponse> {
  const res = await fetch(`${LLMOPS_BASE}/api/rag/status`, {
    headers: { 'x-api-key': LLMOPS_API_KEY },
  });
  if (!res.ok) throw new Error(`RAG status failed: ${res.status}`);
  return res.json();
}

export async function triggerRagReindex(): Promise<RagReindexResponse> {
  const res = await fetch(`${LLMOPS_BASE}/api/rag/reindex`, {
    method: 'POST',
    headers: { 'x-api-key': LLMOPS_API_KEY },
  });
  if (!res.ok) throw new Error(`RAG reindex failed: ${res.status}`);
  return res.json();
}