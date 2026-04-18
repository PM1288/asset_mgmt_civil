export type Subject = {
  subject: string;
  username: string;
  email?: string;
  roles: string[];
};

export type PropertyRecord = {
  id: string;
  property_number: string;
  ward_code: string;
  address_line_1: string;
  address_line_2?: string | null;
  city: string;
  district: string;
  state: string;
  postal_code?: string | null;
  geo_lat?: number | null;
  geo_lng?: number | null;
  status: string;
  use_type: string;
  owner_name: string;
  owner_contact?: string | null;
  assessment_zone?: string | null;
  remarks?: string | null;
  created_at: string;
  updated_at: string;
};

export type LicenseRecord = {
  id: string;
  application_number: string;
  property_id: string;
  license_type: string;
  status: string;
  applicant_name: string;
  applicant_contact?: string | null;
  current_assignee?: string | null;
  submitted_at?: string | null;
  decided_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type HealthEnvelope = {
  status: string;
  components: { name: string; ok: boolean; detail: string }[];
};
