from __future__ import annotations

import hashlib
import os
import json
import shutil
import subprocess
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.engine import make_url

from app.core.config import get_settings


class BackupService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _run(self, args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def create_backup_bundle(self) -> dict[str, str]:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target_dir = self.settings.backups_root / timestamp
        target_dir.mkdir(parents=True, exist_ok=True)

        url = make_url(self.settings.database_url)
        dump_path = target_dir / "database.dump"
        docs_path = target_dir / "documents.tar.gz"
        manifest_path = target_dir / "manifest.json"

        env = os.environ.copy()
        env["PGPASSWORD"] = url.password or ""

        dump_args = [
            "pg_dump",
            "--format=custom",
            "--compress=9",
            "--host", url.host or "db",
            "--port", str(url.port or 5432),
            "--username", url.username or "app",
            "--dbname", url.database or "appdb",
            "--file", str(dump_path),
        ]
        self._run(dump_args, env=env)

        with tarfile.open(docs_path, "w:gz") as archive:
            archive.add(self.settings.docs_root, arcname="documents")

        manifest = {
            "created_at": timestamp,
            "database_dump": dump_path.name,
            "database_sha256": self._sha256(dump_path),
            "documents_archive": docs_path.name,
            "documents_sha256": self._sha256(docs_path),
            "database_url_sanitized": str(url.set(password="***")),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        self.prune_old_backups()
        return {
            "backup_dir": str(target_dir),
            "manifest": str(manifest_path),
            "database_dump": str(dump_path),
            "documents_archive": str(docs_path),
        }

    def validate_backup_bundle(self, bundle_dir: str | Path) -> dict[str, str | bool]:
        bundle = Path(bundle_dir)
        manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
        dump_path = bundle / manifest["database_dump"]
        docs_path = bundle / manifest["documents_archive"]

        if self._sha256(dump_path) != manifest["database_sha256"]:
            raise RuntimeError("Database dump checksum mismatch")
        if self._sha256(docs_path) != manifest["documents_sha256"]:
            raise RuntimeError("Document archive checksum mismatch")

        self._run(["pg_restore", "--list", str(dump_path)])
        with tarfile.open(docs_path, "r:gz") as archive:
            archive.getmembers()

        return {"ok": True, "bundle_dir": str(bundle)}

    def prune_old_backups(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.settings.backup_retention_days)
        for item in self.settings.backups_root.iterdir():
            if not item.is_dir():
                continue
            try:
                created = datetime.strptime(item.name, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if created < cutoff:
                shutil.rmtree(item, ignore_errors=True)


backup_service = BackupService()
