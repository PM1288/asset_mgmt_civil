#!/usr/bin/env python3
"""
Import synthetic seed data into the current Municipal Licensing & Property Platform API.

Requirements:
    pip install requests

Usage:
    python import_via_api.py --base-url http://localhost:8080 --token <TOKEN> --profile-dir ../exports/developer_seed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import sys
import time
from pathlib import Path

import requests


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def idempotency_key(prefix: str, body: dict) -> str:
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def call(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected: tuple[int, ...] = (200, 201),
    json_body: dict | None = None,
    files=None,
    headers: dict | None = None,
    timeout: int = 45,
) -> requests.Response:
    response = session.request(
        method,
        url,
        json=json_body,
        files=files,
        headers=headers or {},
        timeout=timeout,
    )
    if response.status_code not in expected:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"{method} {url} failed with {response.status_code}: {detail}")
    return response


def create_properties(session: requests.Session, base_url: str, rows: list[dict], sleep_s: float) -> dict[str, str]:
    mapping: dict[str, str] = {}
    endpoint = f"{base_url}/api/v1/properties"
    for index, row in enumerate(rows, start=1):
        headers = {"Idempotency-Key": idempotency_key("property", row)}
        response = call(session, "POST", endpoint, expected=(200, 201, 409), json_body=row, headers=headers)
        if response.status_code == 409:
            raise RuntimeError(f"Property conflict for {row['property_number']}. Check if idempotency key/body changed.")
        payload = response.json()
        mapping[row["property_number"]] = payload["id"]
        print(f"[property {index}/{len(rows)}] created {row['property_number']} -> {payload['id']}")
        if sleep_s:
            time.sleep(sleep_s)
    return mapping


def create_licenses(session: requests.Session, base_url: str, rows: list[dict], property_map: dict[str, str], sleep_s: float) -> dict[str, str]:
    mapping: dict[str, str] = {}
    endpoint = f"{base_url}/api/v1/licenses"
    for index, row in enumerate(rows, start=1):
        property_number = row["property_number"]
        if property_number not in property_map:
            raise RuntimeError(f"Property number {property_number} not found in import map.")
        body = {
            "application_number": row["application_number"],
            "property_id": property_map[property_number],
            "license_type": row["license_type"],
            "applicant_name": row["applicant_name"],
            "applicant_contact": row.get("applicant_contact"),
            "notes": row.get("notes"),
        }
        headers = {"Idempotency-Key": idempotency_key("license", body)}
        response = call(session, "POST", endpoint, expected=(200, 201, 409), json_body=body, headers=headers)
        if response.status_code == 409:
            raise RuntimeError(f"License conflict for {row['application_number']}. Check idempotency/body consistency.")
        payload = response.json()
        mapping[row["application_number"]] = payload["id"]
        print(f"[license {index}/{len(rows)}] created {row['application_number']} -> {payload['id']}")
        if sleep_s:
            time.sleep(sleep_s)
    return mapping


def replay_transitions(session: requests.Session, base_url: str, rows: list[dict], license_map: dict[str, str], sleep_s: float) -> None:
    for index, row in enumerate(rows, start=1):
        application_number = row["application_number"]
        license_id = license_map[application_number]
        assignee = row.get("assignee_username")
        comments = row.get("notes") or f"Seeded transition replay for {application_number}"
        for transition in row.get("transition_path", []):
            endpoint = f"{base_url}/api/v1/licenses/{license_id}/{transition}"
            body = {"comments": comments, "assignee": assignee}
            call(session, "POST", endpoint, expected=(200,), json_body=body)
            print(f"[transition {index}/{len(rows)}] {application_number} -> {transition}")
            if sleep_s:
                time.sleep(sleep_s)


def upload_documents(session: requests.Session, base_url: str, documents_dir: Path, license_map: dict[str, str], sleep_s: float) -> None:
    if not documents_dir.exists():
        print(f"[documents] skipped: {documents_dir} does not exist")
        return

    files = sorted(p for p in documents_dir.iterdir() if p.is_file())
    for index, path in enumerate(files, start=1):
        app_no = path.name.split("_", 1)[0].upper()
        license_id = license_map.get(app_no)
        if not license_id:
            print(f"[documents] skipping {path.name}: no created license for {app_no}")
            continue
        mime_type = mimetypes.guess_type(path.name)[0] or "text/plain"
        with path.open("rb") as handle:
            response = call(
                session,
                "POST",
                f"{base_url}/api/v1/licenses/{license_id}/documents",
                expected=(200, 201),
                files={"file": (path.name, handle, mime_type)},
            )
        doc = response.json()
        print(f"[documents {index}/{len(files)}] uploaded {path.name} -> {doc['id']}")
        if sleep_s:
            time.sleep(sleep_s)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import municipal dummy data via API.")
    parser.add_argument("--base-url", required=True, help="Example: http://localhost:8080")
    parser.add_argument("--token", default=None, help="Bearer token. If omitted, uses BEARER_TOKEN env var.")
    parser.add_argument("--profile-dir", required=True, help="Path to exports/developer_seed or exports/hybrid_demo")
    parser.add_argument("--sleep-ms", type=int, default=0, help="Optional delay between API calls")
    parser.add_argument("--skip-documents", action="store_true")
    parser.add_argument("--verify-tls", action="store_true", default=False, help="Verify TLS certificates (default false for dev/local)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = args.token or __import__("os").environ.get("BEARER_TOKEN")
    if not token:
        print("Error: bearer token is required via --token or BEARER_TOKEN.", file=sys.stderr)
        return 2

    profile_dir = Path(args.profile_dir).resolve()
    props_file = profile_dir / "properties_api.jsonl"
    licenses_file = profile_dir / "licenses_api_plan.jsonl"
    docs_dir = profile_dir / "sample_documents"

    for path in [props_file, licenses_file]:
        if not path.exists():
            print(f"Error: missing required file {path}", file=sys.stderr)
            return 2

    properties = load_jsonl(props_file)
    licenses = load_jsonl(licenses_file)

    session = requests.Session()
    session.verify = bool(args.verify_tls)
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
    )

    sleep_s = max(0.0, args.sleep_ms / 1000.0)
    base_url = args.base_url.rstrip("/")

    try:
        property_map = create_properties(session, base_url, properties, sleep_s)
        license_map = create_licenses(session, base_url, licenses, property_map, sleep_s)
        replay_transitions(session, base_url, licenses, license_map, sleep_s)
        if not args.skip_documents:
            upload_documents(session, base_url, docs_dir, license_map, sleep_s)
    except Exception as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1

    print("Import completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
