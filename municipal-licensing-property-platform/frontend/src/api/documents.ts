import { apiDownload, apiUpload } from "./client";
import type { DocumentRecord } from "../types";

export function uploadPropertyDocument(propertyId: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiUpload<DocumentRecord>(`/api/v1/properties/${propertyId}/documents`, form);
}

export function uploadLicenseDocument(licenseId: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiUpload<DocumentRecord>(`/api/v1/licenses/${licenseId}/documents`, form);
}

export function downloadDocument(documentId: string, filename: string) {
  return apiDownload(`/api/v1/documents/${documentId}/download`, filename);
}
