import { Icons } from '@/components/icons';

// ─── Existing template types (keep as-is) ────────────────────────────────────

export interface PermissionCheck {
  permission?: string;
  plan?: string;
  feature?: string;
  role?: string;
  requireOrg?: boolean;
}

export interface NavItem {
  title: string;
  url: string;
  disabled?: boolean;
  external?: boolean;
  shortcut?: [string, string];
  icon?: keyof typeof Icons;
  label?: string;
  description?: string;
  isActive?: boolean;
  items?: NavItem[];
  access?: PermissionCheck;
}

export interface NavItemWithChildren extends NavItem {
  items: NavItemWithChildren[];
}

export interface NavItemWithOptionalChildren extends NavItem {
  items?: NavItemWithChildren[];
}

export interface FooterItem {
  title: string;
  items: {
    title: string;
    href: string;
    external?: boolean;
  }[];
}

export type MainNavItem = NavItemWithOptionalChildren;
export type SidebarNavItem = NavItemWithChildren;

// ─── RetinaXAI domain types ───────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  username: string;
  email: string;
}

export interface Patient {
  id: string;
  username: string;
  date_of_birth: string;
  gender: 'male' | 'female' | 'other';
  medical_record_number: string;
  created_at: string;
}

export interface MRIScan {
  id: string;
  patient_id: string;
  left_scan_path: string;
  right_scan_path: string;
  uploaded_at: string;
}

export type DRSeverity =
  | 'no_dr'
  | 'mild'
  | 'moderate'
  | 'severe'
  | 'proliferative';

export interface Prediction {
  id: string;
  patient_id: string;
  scan_id: string;
  severity: DRSeverity;
  confidence: number;
  gradcam_url: string;
  created_at: string;
}

export interface Report {
  id: string;
  prediction_id: string;
  content: string;
  generated_at: string;
}

export interface ApiError {
  detail: string;
  status: number;
}