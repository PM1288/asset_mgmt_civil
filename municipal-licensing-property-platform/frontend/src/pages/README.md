# pages

## Purpose

Screen-level React components for dashboard, properties, licenses, health, and admin diagnostics.

## Files and subfolders

- `README.md`: Documentation for this folder.

## API endpoints implemented in this folder

- `Each page calls one or more backend endpoints through the api wrappers.`

## Dependencies

- src/api/*
- components/*
- hooks/useAsync.ts

## Operational notes

- Pages should remain resilient to partial API failure and display actionable errors.

## Failure considerations

- Incorrect page state handling can create duplicate user actions without idempotency.
