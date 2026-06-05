"""
Azure Blob Storage service for JurisFind.

Handles PDF upload, download, deletion, and existence checks.
Blob path pattern: documents/{user_id}/{uuid}.pdf

Falls back to local ephemeral storage when USE_LOCAL_FILES=true
(for local development without an Azure subscription).
"""

import os
import uuid
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# Azure SDK – imported lazily so local-only mode works without azure creds
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    _AZURE_AVAILABLE = True
except ImportError:
    _AZURE_AVAILABLE = False


class BlobStorageError(Exception):
    """Raised when a blob storage operation fails."""
    pass


class BlobStorageService:
    """
    Service for PDF persistence in Azure Blob Storage (or local fallback).

    When USE_LOCAL_FILES=true (default for dev), files are stored under
    api/data/confidential_tmp/<blob_path> so no Azure account is needed.

    Args:
        connection_string: Azure storage connection string (reads from env if omitted)
        container_name: Blob container name (reads from env if omitted)
        use_local: Override to force local mode
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        container_name: Optional[str] = None,
        use_local: Optional[bool] = None,
    ):
        self._conn_str = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        self._container = container_name or os.getenv(
            "AZURE_STORAGE_CONTAINER_NAME",
            os.getenv("AZURE_DATA_CONTAINER", "documents"),
        )

        env_local = os.getenv("USE_LOCAL_FILES", "true").lower() == "true"
        self._use_local: bool = use_local if use_local is not None else env_local

        # Local storage root
        _api_dir = Path(__file__).resolve().parent.parent
        self._local_root: Path = _api_dir / "data" / "uploaded_documents"
        self._local_root.mkdir(parents=True, exist_ok=True)

        # Lazy Azure client
        self._blob_client: Optional[object] = None

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_blob_client(self):
        """Return (or lazily create) the Azure BlobServiceClient."""
        if not _AZURE_AVAILABLE:
            raise BlobStorageError(
                "azure-storage-blob package is not installed. "
                "Run: pip install azure-storage-blob"
            )
        if not self._conn_str:
            raise BlobStorageError(
                "AZURE_STORAGE_CONNECTION_STRING is not set. "
                "Set USE_LOCAL_FILES=true for local development."
            )
        if self._blob_client is None:
            self._blob_client = BlobServiceClient.from_connection_string(self._conn_str)
        return self._blob_client

    @staticmethod
    def _generate_blob_path(user_id: str) -> str:
        """Generate a unique blob path: documents/{user_id}/{uuid}.pdf"""
        return f"documents/{user_id}/{uuid.uuid4()}.pdf"

    def _local_path(self, blob_path: str) -> Path:
        """Resolve a blob_path to an absolute local filesystem path.

        There are two classes of local paths:
        - Uploaded user docs:   documents/{user_id}/{uuid}.pdf  → self._local_root/...
        - Corpus legal cases:   data/pdfs/{filename}.pdf        → backend_root/data/pdfs/...
        """
        if os.path.isabs(blob_path):
            return Path(blob_path)

        # Corpus PDFs live at backend/data/pdfs/, not under uploaded_documents
        # _api_dir is backend/app/, so parent is backend/
        if blob_path.startswith("data/pdfs/"):
            _backend_root = Path(__file__).resolve().parent.parent.parent
            return _backend_root / blob_path

        return self._local_root / blob_path

    # ── Public API ───────────────────────────────────────────────────────────

    def upload_pdf(self, file_bytes: bytes, user_id: str) -> str:
        """
        Upload a PDF file and return its blob_path.

        Args:
            file_bytes: Raw PDF bytes
            user_id: UUID string of the uploading user

        Returns:
            str: blob_path in format 'documents/{user_id}/{uuid}.pdf'

        Raises:
            BlobStorageError: If upload fails
        """
        blob_path = self._generate_blob_path(user_id)

        if self._use_local:
            dest = self._local_path(blob_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(file_bytes)
            return blob_path

        try:
            client = self._get_blob_client()
            blob = client.get_blob_client(container=self._container, blob=blob_path)
            blob.upload_blob(
                file_bytes,
                overwrite=False,
                content_settings=ContentSettings(content_type="application/pdf"),
            )
            return blob_path
        except Exception as exc:
            raise BlobStorageError(f"Failed to upload PDF: {exc}") from exc

    def download_pdf(self, blob_path: str) -> bytes:
        """
        Download a PDF file by its blob_path.

        Args:
            blob_path: Path as stored in DocumentSession.blob_path

        Returns:
            bytes: Raw PDF bytes

        Raises:
            BlobStorageError: If download fails or file not found
        """
        if self._use_local:
            dest = self._local_path(blob_path)
            if not dest.exists():
                raise BlobStorageError(f"Local file not found: {blob_path}")
            return dest.read_bytes()

        try:
            client = self._get_blob_client()
            blob = client.get_blob_client(container=self._container, blob=blob_path)
            stream = blob.download_blob()
            return stream.readall()
        except Exception as exc:
            raise BlobStorageError(f"Failed to download PDF '{blob_path}': {exc}") from exc

    def delete_pdf(self, blob_path: str) -> None:
        """
        Delete a PDF file by its blob_path.

        Args:
            blob_path: Path as stored in DocumentSession.blob_path

        Raises:
            BlobStorageError: If deletion fails
        """
        if self._use_local:
            dest = self._local_path(blob_path)
            if dest.exists():
                dest.unlink()
            # Remove empty parent directories (up to local_root)
            try:
                dest.parent.rmdir()
                dest.parent.parent.rmdir()
            except OSError:
                pass  # Not empty – that's fine
            return

        try:
            client = self._get_blob_client()
            blob = client.get_blob_client(container=self._container, blob=blob_path)
            blob.delete_blob(delete_snapshots="include")
        except Exception as exc:
            raise BlobStorageError(f"Failed to delete PDF '{blob_path}': {exc}") from exc

    def blob_exists(self, blob_path: str) -> bool:
        """
        Check whether a blob exists.

        Args:
            blob_path: Path as stored in DocumentSession.blob_path

        Returns:
            bool: True if the blob exists, False otherwise
        """
        if self._use_local:
            return self._local_path(blob_path).exists()

        try:
            client = self._get_blob_client()
            blob = client.get_blob_client(container=self._container, blob=blob_path)
            return blob.exists()
        except Exception:
            return False

    def store_local_file(self, file_path: str, user_id: str) -> str:
        """
        Register an existing local file in blob storage (local mode only).

        Copies the file to the local storage root and returns the blob_path.
        Useful for the 'retrieved' document flow where the file already exists locally.

        Args:
            file_path: Absolute path to the source file
            user_id: UUID string of the requesting user

        Returns:
            str: blob_path
        """
        blob_path = self._generate_blob_path(user_id)
        dest = self._local_path(blob_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, dest)
        return blob_path


# Module-level singleton
blob_storage_service = BlobStorageService()
