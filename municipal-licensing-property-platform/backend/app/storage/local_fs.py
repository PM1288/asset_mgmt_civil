from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from app.core.bulkhead import Bulkhead
from app.core.config import get_settings
from app.core.encryption import get_fernet


bulkhead = Bulkhead(get_settings().storage_bulkhead_limit)


class EncryptedDocumentStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def save(self, *, aggregate_type: str, aggregate_id: str, filename: str, payload: bytes) -> tuple[str, str, int]:
        target_dir = self.settings.docs_root / aggregate_type / aggregate_id
        target_dir.mkdir(parents=True, exist_ok=True)
        extension = Path(filename).suffix or ".bin"
        object_name = f"{uuid4().hex}{extension}.enc"
        object_path = target_dir / object_name

        checksum = hashlib.sha256(payload).hexdigest()
        encrypted = get_fernet().encrypt(payload)

        with bulkhead.slot():
            object_path.write_bytes(encrypted)

        relative = str(object_path.relative_to(self.settings.docs_root))
        return relative, checksum, len(payload)

    def read(self, relative_path: str) -> bytes:
        object_path = self.settings.docs_root / relative_path
        encrypted = object_path.read_bytes()
        return get_fernet().decrypt(encrypted)

    def exists(self, relative_path: str) -> bool:
        return (self.settings.docs_root / relative_path).exists()


document_store = EncryptedDocumentStore()
