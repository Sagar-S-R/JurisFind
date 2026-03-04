# Azure Blob Storage Integration

This document covers the Azure Blob Storage setup for JurisFind in production — how to create the storage account and container, how data is structured inside the container, how to upload the FAISS index and PDFs, how the API reads from Blob on startup, and how to configure the environment.

For Azure VM and Static Web Apps deployment, see [deployment.md](deployment.md).

---

## Table of Contents

- [Storage Account Setup](#storage-account-setup)
- [Container Structure](#container-structure)
- [Uploading Data to Blob](#uploading-data-to-blob)
- [How the API Uses Blob Storage](#how-the-api-uses-blob-storage)
- [Environment Configuration](#environment-configuration)
- [Switching Between Local and Blob Mode](#switching-between-local-and-blob-mode)
- [Troubleshooting](#troubleshooting)

---

## Storage Account Setup

### 1. Create a Storage Account

In the [Azure Portal](https://portal.azure.com):

1. Search for **Storage accounts** and click **+ Create**
2. Fill in the basics:
   - **Subscription**: your subscription
   - **Resource group**: same group as your VM (e.g. `jurisFind`)
   - **Storage account name**: lowercase alphanumeric only, e.g. `jurisfindstore`
   - **Region**: East US 2 (match your VM region to avoid egress costs)
   - **Redundancy**: Locally-redundant storage (LRS) is sufficient
3. Leave all other settings at defaults and click **Review + Create** then **Create**

### 2. Get the Connection String

Once the storage account is created:

1. Go to the storage account in the portal
2. In the left sidebar under **Security + networking**, click **Access keys**
3. Click **Show** next to **key1**
4. Copy the full **Connection string** — it looks like:
   ```
   DefaultEndpointsProtocol=https;AccountName=jurisfindstore;AccountKey=BASE64KEY==;EndpointSuffix=core.windows.net
   ```

Keep this string private — do not commit it to git. Store it in `api/.env` on the VM only.

### 3. Create the Container

1. In the storage account, click **Containers** in the left sidebar
2. Click **+ Container**
3. Name: `data`
4. Public access level: **Private (no anonymous access)**
5. Click **Create**

---

## Container Structure

All JurisFind data lives inside the `data` container with the following structure:

```
data/
├── faiss_store/
│   ├── legal_cases.index        # FAISS binary index (136 MB)
│   └── id2name.json             # Map from FAISS integer ID to PDF filename (2.2 MB)
└── pdfs/
    ├── case_001.pdf
    ├── case_002.pdf
    └── ...                      # 48,294 PDF files (5.3 GB total)
```

The `faiss_store/` prefix is hardcoded in `helpers/azure_blob_helper.py` in the `download_faiss_index` and `upload_faiss_index` methods. The `pdfs/` prefix is used in `routes/routes.py` when serving PDFs via `GET /api/pdf/{filename}`.

---

## Uploading Data to Blob

### Upload the FAISS Index

Use the provided `upload_to_blob.py` script in the `api/` directory. Before running, open the script and set your real connection string in the `CONNECTION_STRING` variable (do not commit it), then:

```bash
cd api
pip install azure-storage-blob
python upload_to_blob.py
```

This uploads `api/data/faiss_store/legal_cases.index` and `api/data/faiss_store/id2name.json` to `data/faiss_store/` in Blob Storage. After running, reset the connection string in the script back to the placeholder so it is not accidentally committed.

### Upload PDFs

For a large number of files (48K PDFs, 5.3 GB), use the Azure CLI with parallel connections:

```bash
az storage blob upload-batch \
  --connection-string "YOUR_CONNECTION_STRING" \
  --destination "data" \
  --destination-path "pdfs" \
  --source "api/data/pdfs" \
  --pattern "*.pdf" \
  --max-connections 10 \
  --no-progress
```

`--max-connections 10` uploads 10 files concurrently. This takes approximately 15–30 minutes on a typical home connection for 5.3 GB.

To verify the upload count after completion:

```bash
az storage blob list \
  --connection-string "YOUR_CONNECTION_STRING" \
  --container-name data \
  --prefix pdfs/ \
  --query "length(@)" \
  --output tsv
```

### Uploading New PDFs Later

To add new PDFs to the collection without re-uploading everything:

```bash
az storage blob upload \
  --connection-string "YOUR_CONNECTION_STRING" \
  --container-name data \
  --name "pdfs/new_case.pdf" \
  --file "path/to/new_case.pdf"
```

After uploading new PDFs, you must rebuild and re-upload the FAISS index for the new documents to appear in search results.

---

## How the API Uses Blob Storage

The entry point is `services/search_service.py` in the `LegalCaseSearcher.__init__` method. On every container startup:

1. It checks whether `AZURE_STORAGE_CONNECTION_STRING` is set in the environment
2. If set, it calls `helpers/azure_blob_helper.py` → `AzureBlobHelper.download_faiss_index()`, which downloads both `faiss_store/legal_cases.index` and `faiss_store/id2name.json` to a temporary directory inside the container
3. It then loads the FAISS index and ID-to-filename map from those temp files into memory
4. If the connection string is not set (local mode), it falls back to reading from `api/data/faiss_store/` on disk

When a user requests PDF analysis via `POST /api/unified/analyze`:

1. `routes/routes.py` checks whether `AZURE_STORAGE_CONNECTION_STRING` is set
2. If set, it downloads the specific PDF from `data/pdfs/{filename}` to a temporary file, passes the path to the agent, and deletes the temp file after analysis
3. If not set, it reads from `api/data/pdfs/{filename}` on disk directly

When a user requests a PDF via `GET /api/pdf/{filename}`:

1. If Azure is configured, the blob `data/pdfs/{filename}` is downloaded and streamed directly as a binary response
2. If local mode, `api/data/pdfs/{filename}` is served via `FileResponse`

---

## Environment Configuration

On the VM, edit `/opt/jurisfind/api/.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Azure Blob Storage — required for production blob mode
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=jurisfindstore;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
AZURE_DATA_CONTAINER=data

# Set to false to use Blob Storage, true to use local api/data/ files
USE_LOCAL_FILES=false
```

After editing `.env`, restart the container for changes to take effect:

```bash
cd /opt/jurisfind
sudo docker compose restart
sudo docker compose logs -f
```

You should see the following line in the logs confirming blob mode is active:

```
Downloading FAISS index from Azure Blob Storage...
Loaded FAISS index with 46456 documents from Azure Blob Storage.
```

---

## Switching Between Local and Blob Mode

| `USE_LOCAL_FILES` | `AZURE_STORAGE_CONNECTION_STRING` | Behavior |
|---|---|---|
| `true` | any | Reads FAISS index and PDFs from local `api/data/` |
| `false` | set | Downloads FAISS index from Blob on startup, streams PDFs from Blob on demand |
| `false` | not set | Falls back to local mode with a warning in logs |

Local mode is recommended for development. Blob mode is required for production since the VM does not have `api/data/pdfs/` mounted — only the FAISS store volume is mounted, and only if you explicitly configured the bind mount in `docker-compose.yml`.

---

## Troubleshooting

**Container starts but health check returns FAISS index not found**

The container cannot find the FAISS index. Either:
- `USE_LOCAL_FILES=true` but `api/data/faiss_store/` is not mounted into the container — check the volume mount in `docker-compose.yml`
- `USE_LOCAL_FILES=false` but `AZURE_STORAGE_CONNECTION_STRING` is wrong or not set — check `api/.env` on the VM and restart the container
- The FAISS index was never uploaded to Blob — run `upload_to_blob.py`

**PDF analysis returns "PDF not found"**

- In blob mode: the PDF filename from the search result does not match what was uploaded to `data/pdfs/`. Check the exact blob name with `az storage blob list --container-name data --prefix pdfs/`
- In local mode: the file does not exist at `api/data/pdfs/{filename}`

**Upload fails with authentication error**

The connection string or account key may have changed. Regenerate the key in the Azure Portal under **Access keys** and update `api/.env` on the VM.

**Slow PDF serving**

Each PDF is downloaded fresh from Blob on every request. For repeated access to the same document, consider adding a local cache in the container or using Azure CDN in front of the storage account.
