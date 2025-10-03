# Azure Blob Storage Integration

This document explains how to configure and use Azure Blob Storage with the Legal Case Search API.

## Overview

The Legal Case Search API has been updated to support Azure Blob Storage as the primary data storage backend. This enables:

- **Cloud-native PDF storage**: Store thousands of legal documents in Azure Blob Storage
- **Scalable FAISS indexing**: Generate and store vector embeddings in the cloud
- **Distributed deployment**: Deploy the API without local file dependencies
- **Backup and sync**: Maintain data consistency across environments

## Configuration

### Azure Storage Account Setup

1. **Create an Azure Storage Account**:
   ```bash
   # Using Azure CLI
   az storage account create \
     --name yourstorageaccount \
     --resource-group your-resource-group \
     --location eastus \
     --sku Standard_LRS
   ```

2. **Get the connection string**:
   ```bash
   az storage account show-connection-string \
     --name yourstorageaccount \
     --resource-group your-resource-group
   ```

3. **Create the data container**:
   ```bash
   az storage container create \
     --name data \
     --connection-string "your-connection-string"
   ```

### Environment Variables

Add these variables to your `.env` file:

```env
# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
AZURE_DATA_CONTAINER="data"

# Existing configuration
GROQ_API_KEY="your_groq_api_key_here"
GROQ_MODEL=llama3-70b-8192
API_HOST=localhost
API_PORT=8000
```

## Container Structure

The Azure Blob Storage container uses this structure:

```
data/                          # Container name
├── pdfs/                      # PDF documents
│   ├── case_001.pdf
│   ├── case_002.pdf
│   └── ...
├── faiss_store/              # FAISS vector index
│   ├── legal_cases.index     # FAISS index file
│   └── id2name.json          # Document ID mapping
└── confidential/            # Temporary uploads
    ├── temp_doc_001.pdf
    └── ...
```

## Usage

### 1. Upload PDF Files

**Option A: Using the Azure Data Manager**
```bash
cd api
python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs
```

**Option B: Using the API endpoint**
```bash
curl -X POST "http://localhost:8000/api/upload-pdf-to-azure" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

**Option C: Using the helper functions**
```python
from helpers.azure_blob_helper import upload_pdf_files_to_azure

result = upload_pdf_files_to_azure("./data/pdfs")
print(f"Uploaded {result['uploaded']} files")
```

### 2. Generate FAISS Index

**Option A: Using the Azure Data Manager**
```bash
cd api
python helpers/azure_data_manager.py generate-index
```

**Option B: Using the API endpoint**
```bash
curl -X POST "http://localhost:8000/api/generate-embeddings-from-azure"
```

**Option C: Using the helper functions**
```python
from helpers.azure_blob_helper import generate_and_upload_faiss_index

result = generate_and_upload_faiss_index()
print(f"Processed {result['documents_processed']} documents")
```

### 3. Search Documents

The search functionality automatically works with Azure storage:

```python
import requests

# Search via API
response = requests.post("http://localhost:8000/api/search", json={
    "query": "contract law dispute resolution",
    "top_k": 5
})

results = response.json()
```

### 4. Serve PDF Files

PDFs are automatically served from Azure:

```bash
# Access PDF via browser or API
curl "http://localhost:8000/api/pdf/case_001.pdf"
```

## Management Commands

The Azure Data Manager provides comprehensive data management:

### List Files
```bash
# List all PDF files
python helpers/azure_data_manager.py list-files

# List files in specific directory
python helpers/azure_data_manager.py list-files --directory faiss_store
```

### Download Data
```bash
# Download FAISS index to local storage
python helpers/azure_data_manager.py download-index

# Download PDFs to local directory
python helpers/azure_data_manager.py download-pdfs --output-dir ./downloaded_pdfs --max-files 100
```

### Full Sync
```bash
# Upload local data, generate index, download for development
python helpers/azure_data_manager.py sync --download-local
```

## API Endpoints

### New Azure-Specific Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/list-pdfs` | GET | List all PDF files in Azure storage |
| `/api/upload-pdf-to-azure` | POST | Upload PDF file to Azure |
| `/api/generate-embeddings-from-azure` | POST | Generate FAISS index from Azure PDFs |

### Updated Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pdf/{filename}` | GET | Serve PDF from Azure (fallback to local) |
| `/api/search` | POST/GET | Search using Azure-based FAISS index |
| `/api/health` | GET | Health check with Azure status |

## Testing

Run the Azure integration tests:

```bash
cd api
python tests/test_azure_integration.py
```

This will test:
- Azure Blob Storage connection
- PDF file listing and download
- FAISS index operations
- Search functionality
- Blob metadata access

## Development Workflow

### Local Development with Azure
1. Set up Azure Storage Account and get connection string
2. Upload your PDF files to Azure
3. Generate FAISS index from Azure PDFs
4. Run the API locally - it will automatically use Azure storage

### Production Deployment
1. Configure Azure Storage connection string in production environment
2. Deploy the API - no local files needed
3. All data operations will use Azure Blob Storage

### Hybrid Development
1. Keep local files for quick development
2. Sync with Azure periodically
3. Switch between local and Azure by setting/unsetting `AZURE_STORAGE_CONNECTION_STRING`

## Performance Considerations

### Caching
- FAISS index is downloaded once at startup and cached in memory
- PDF files are streamed directly from Azure (no local caching)
- Consider implementing Redis for distributed caching in production

### Batch Operations
- Use the Azure Data Manager for batch uploads/downloads
- Generate embeddings in batches to avoid API timeouts
- Consider Azure Batch for large-scale processing

### Cost Optimization
- Use Azure Blob Storage tiers (Hot/Cool/Archive) based on access patterns
- Enable Azure CDN for frequently accessed PDFs
- Monitor storage and bandwidth costs

## Troubleshooting

### Common Issues

**Connection String Errors**
```bash
# Test connection
python -c "from helpers.azure_blob_helper import get_azure_blob_helper; print(get_azure_blob_helper())"
```

**Missing Files**
```bash
# Check what's in Azure
python helpers/azure_data_manager.py list-files
```

**Search Not Working**
```bash
# Test search service
python tests/test_azure_integration.py
```

**Upload Failures**
- Check Azure Storage account permissions
- Verify container exists and is accessible
- Check file size limits (Azure Blob Storage supports up to 4.75 TB per blob)

### Error Messages

| Error | Cause | Solution |
|-------|-------|---------|
| "AZURE_STORAGE_CONNECTION_STRING not set" | Missing environment variable | Set connection string in .env file |
| "Container not found" | Missing container | Create the "data" container in Azure |
| "Blob not found" | Missing files | Upload PDF files and generate index |
| "Failed to download FAISS index" | Index not generated | Run `generate-index` command |

## Security

### Access Control
- Use Azure Storage Account Access Keys or SAS tokens
- Implement Azure AD authentication for production
- Configure firewall rules to restrict access

### Data Protection
- Enable Azure Storage encryption at rest
- Use HTTPS for all API communications
- Implement proper authentication for the API endpoints

### Compliance
- Azure Blob Storage supports various compliance standards
- Enable audit logging for data access
- Implement data retention policies as needed

## Migration from Local Files

### Step-by-Step Migration

1. **Backup your local data**
2. **Set up Azure Storage**
3. **Upload existing PDFs**:
   ```bash
   python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs
   ```
4. **Generate new index**:
   ```bash
   python helpers/azure_data_manager.py generate-index
   ```
5. **Test the integration**:
   ```bash
   python tests/test_azure_integration.py
   ```
6. **Update environment variables**
7. **Deploy with Azure configuration**

### Rollback Plan
- Keep local files as backup
- Remove `AZURE_STORAGE_CONNECTION_STRING` to revert to local files
- Re-generate local FAISS index if needed

## Best Practices

1. **Use environment-specific storage accounts** (dev/staging/prod)
2. **Implement proper error handling** for network issues
3. **Monitor Azure costs** and usage patterns
4. **Backup critical data** across multiple regions
5. **Use Azure Private Endpoints** for secure access
6. **Implement retry logic** for transient failures
7. **Log all Azure operations** for debugging