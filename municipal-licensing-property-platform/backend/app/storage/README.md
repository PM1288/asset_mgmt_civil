# storage

## Purpose

Encrypted file storage primitives for uploaded evidence and documents.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Backing implementation for document upload/download endpoints.`

## Dependencies

- runtime/documents
- core/encryption
- bulkhead

## Operational notes

- Document volume must be mounted and included in backup policy.

## Failure considerations

- Disk pressure or permission loss impacts attachments but not core metadata.
