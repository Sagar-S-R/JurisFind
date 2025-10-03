"""
Azure Data Management Utility

This utility script provides commands for managing data in Azure Blob Storage:
- Upload local PDFs to Azure
- Generate and upload FAISS index from Azure PDFs
- Download data from Azure for local development
- Sync local and Azure data
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add API directory to path
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from helpers.azure_blob_helper import (
    get_azure_blob_helper, 
    upload_pdf_files_to_azure, 
    generate_and_upload_faiss_index
)

# Load environment variables
load_dotenv()

def upload_pdfs_command(args):
    """Upload local PDF files to Azure Blob Storage"""
    print(f"🔄 Uploading PDFs from {args.pdf_dir} to Azure Blob Storage...")
    
    if not os.path.exists(args.pdf_dir):
        print(f"❌ Directory not found: {args.pdf_dir}")
        return False
    
    result = upload_pdf_files_to_azure(args.pdf_dir)
    
    if result["success"]:
        print(f"✅ Upload complete: {result['uploaded']}/{result['total_files']} files uploaded")
        if result["failed"] > 0:
            print(f"⚠️  {result['failed']} files failed:")
            for error in result["errors"]:
                print(f"   - {error}")
        return True
    else:
        print(f"❌ Upload failed: {result['error']}")
        return False

def generate_index_command(args):
    """Generate FAISS index from Azure PDFs"""
    print("🔄 Generating FAISS index from Azure PDFs...")
    
    result = generate_and_upload_faiss_index(max_files=args.max_files)
    
    if result["success"]:
        print(f"✅ Index generation complete:")
        print(f"   - Documents processed: {result['documents_processed']}")
        print(f"   - Index dimension: {result['index_dimension']}")
        print(f"   - Message: {result['message']}")
        return True
    else:
        print(f"❌ Index generation failed: {result['error']}")
        return False

def download_index_command(args):
    """Download FAISS index from Azure to local storage"""
    print("🔄 Downloading FAISS index from Azure to local storage...")
    
    try:
        azure_helper = get_azure_blob_helper()
        
        # Create local directory
        local_store_dir = os.path.join(_API_DIR, "data", "faiss_store")
        os.makedirs(local_store_dir, exist_ok=True)
        
        # Download files
        index_path = os.path.join(local_store_dir, "legal_cases.index")
        id2name_path = os.path.join(local_store_dir, "id2name.json")
        
        if azure_helper.download_file("faiss_store/legal_cases.index", index_path):
            print(f"✅ Downloaded FAISS index to {index_path}")
        else:
            print("❌ Failed to download FAISS index")
            return False
        
        if azure_helper.download_file("faiss_store/id2name.json", id2name_path):
            print(f"✅ Downloaded ID mapping to {id2name_path}")
        else:
            print("❌ Failed to download ID mapping")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def download_pdfs_command(args):
    """Download PDF files from Azure to local storage"""
    print(f"🔄 Downloading PDFs from Azure to {args.output_dir}...")
    
    try:
        azure_helper = get_azure_blob_helper()
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Get list of PDFs
        pdf_files = azure_helper.list_pdf_files()
        
        if not pdf_files:
            print("⚠️  No PDF files found in Azure Blob Storage")
            return False
        
        print(f"Found {len(pdf_files)} PDF files")
        
        # Limit files if specified
        if args.max_files:
            pdf_files = pdf_files[:args.max_files]
            print(f"Limiting to {len(pdf_files)} files")
        
        # Download files
        downloaded = 0
        failed = 0
        
        for pdf_file in pdf_files:
            local_path = os.path.join(args.output_dir, pdf_file)
            
            if azure_helper.download_file(f"pdfs/{pdf_file}", local_path):
                downloaded += 1
                if downloaded % 10 == 0:  # Progress update
                    print(f"   Downloaded {downloaded}/{len(pdf_files)} files...")
            else:
                failed += 1
                print(f"   ❌ Failed to download: {pdf_file}")
        
        print(f"✅ Download complete: {downloaded}/{len(pdf_files)} files downloaded")
        if failed > 0:
            print(f"⚠️  {failed} files failed to download")
        
        return downloaded > 0
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def list_files_command(args):
    """List files in Azure Blob Storage"""
    try:
        azure_helper = get_azure_blob_helper()
        
        if args.directory:
            print(f"🔄 Listing files in directory: {args.directory}")
            files = azure_helper.list_blobs_in_directory(args.directory)
        else:
            print("🔄 Listing PDF files...")
            files = azure_helper.list_pdf_files()
        
        if files:
            print(f"✅ Found {len(files)} files:")
            for i, file in enumerate(files, 1):
                print(f"   {i:3d}. {file}")
                if args.limit and i >= args.limit:
                    print(f"   ... and {len(files) - i} more files")
                    break
        else:
            print("⚠️  No files found")
        
        return len(files) > 0
        
    except Exception as e:
        print(f"❌ List failed: {e}")
        return False

def sync_command(args):
    """Sync data between local and Azure storage"""
    print("🔄 Syncing data between local and Azure storage...")
    
    success = True
    
    # Upload local PDFs if they exist
    local_pdf_dir = os.path.join(_API_DIR, "data", "pdfs")
    if os.path.exists(local_pdf_dir):
        print("\n📤 Uploading local PDFs to Azure...")
        result = upload_pdf_files_to_azure(local_pdf_dir)
        if not result["success"]:
            success = False
    
    # Generate index from Azure PDFs
    print("\n🔧 Generating FAISS index from Azure PDFs...")
    result = generate_and_upload_faiss_index()
    if not result["success"]:
        success = False
    
    # Download index back to local for development
    if args.download_local:
        print("\n📥 Downloading FAISS index to local storage...")
        if not download_index_command(args):
            success = False
    
    if success:
        print("\n✅ Sync completed successfully!")
    else:
        print("\n⚠️  Sync completed with some errors")
    
    return success

def main():
    """Main command line interface"""
    parser = argparse.ArgumentParser(
        description="Azure Data Management Utility for Legal Case Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload local PDFs to Azure
  python azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs

  # Generate FAISS index from Azure PDFs
  python azure_data_manager.py generate-index

  # Download FAISS index from Azure
  python azure_data_manager.py download-index

  # Download PDFs from Azure
  python azure_data_manager.py download-pdfs --output-dir ./downloaded_pdfs --max-files 50

  # List files in Azure
  python azure_data_manager.py list-files

  # Full sync (upload PDFs, generate index, download index)
  python azure_data_manager.py sync --download-local
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload PDFs command
    upload_parser = subparsers.add_parser('upload-pdfs', help='Upload local PDF files to Azure')
    upload_parser.add_argument('--pdf-dir', required=True, help='Local PDF directory')
    
    # Generate index command
    generate_parser = subparsers.add_parser('generate-index', help='Generate FAISS index from Azure PDFs')
    generate_parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    
    # Download index command
    download_index_parser = subparsers.add_parser('download-index', help='Download FAISS index from Azure')
    
    # Download PDFs command
    download_pdfs_parser = subparsers.add_parser('download-pdfs', help='Download PDF files from Azure')
    download_pdfs_parser.add_argument('--output-dir', required=True, help='Output directory for downloads')
    download_pdfs_parser.add_argument('--max-files', type=int, help='Maximum number of files to download')
    
    # List files command
    list_parser = subparsers.add_parser('list-files', help='List files in Azure Blob Storage')
    list_parser.add_argument('--directory', help='Directory to list (default: pdfs)')
    list_parser.add_argument('--limit', type=int, help='Limit number of files shown')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync data between local and Azure')
    sync_parser.add_argument('--download-local', action='store_true', help='Download index to local after sync')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check Azure connection
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        print("❌ AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        print("   Please set this variable in your .env file or environment")
        sys.exit(1)
    
    # Execute command
    commands = {
        'upload-pdfs': upload_pdfs_command,
        'generate-index': generate_index_command,
        'download-index': download_index_command,
        'download-pdfs': download_pdfs_command,
        'list-files': list_files_command,
        'sync': sync_command
    }
    
    try:
        success = commands[args.command](args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()