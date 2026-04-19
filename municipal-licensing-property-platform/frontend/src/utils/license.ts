import type { LicenseRecord } from "../types";

const REVIEW_SLA_DAYS: Record<string, number> = {
  submitted: 2,
  under_review: 5
};

const RENEWAL_DAYS: Record<string, number> = {
  trade: 365,
  health: 365,
  fire: 365,
  signage: 365,
  building: 730
};

export function getReviewDueAt(record: LicenseRecord): Date | null {
  const days = REVIEW_SLA_DAYS[record.status];
  if (!days) {
    return null;
  }
  const anchor = record.submitted_at || record.updated_at || record.created_at;
  const parsed = new Date(anchor);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  parsed.setDate(parsed.getDate() + days);
  return parsed;
}

export function getEstimatedExpiryAt(record: LicenseRecord): Date | null {
  if (!["approved", "revoked"].includes(record.status)) {
    return null;
  }
  const anchor = record.decided_at || record.updated_at || record.created_at;
  const parsed = new Date(anchor);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  parsed.setDate(parsed.getDate() + (RENEWAL_DAYS[record.license_type] || 365));
  return parsed;
}
