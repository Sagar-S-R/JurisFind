#!/usr/bin/env python3
"""
Azure Setup Script for Legal Case Search API

This script helps you set up Azure Blob Storage integration for the first time.
"""

import os
import sys
from dotenv import load_dotenv

def check_requirements():
    """Check if required packages are installed"""
    try:
        import azure.storage.blob
        import sentence_transformers
        import faiss
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has Azure configuration"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    if not os.path.exists(env_path):
        print(f"⚠️  .env file not found at {env_path}")
        create_env = input("Would you like to create a .env file? (y/n): ").lower() == 'y'
        
        if create_env:
            return create_env_file(env_path)
        else:
            print("Please create a .env file with your Azure configuration")
            return False
    
    # Load and check existing .env file
    load_dotenv(env_path)
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    if not connection_string:
        print("⚠️  AZURE_STORAGE_CONNECTION_STRING not found in .env file")
        add_azure = input("Would you like to add Azure configuration? (y/n): ").lower() == 'y'
        
        if add_azure:
            return add_azure_config(env_path)
        else:
            print("Please add AZURE_STORAGE_CONNECTION_STRING to your .env file")
            return False
    
    print("✅ Azure configuration found in .env file")
    return True

def create_env_file(env_path):
    """Create a new .env file with Azure configuration"""
    print("\n📝 Creating .env file...")
    
    # Get Azure connection string
    connection_string = input("Enter your Azure Storage connection string: ").strip()
    if not connection_string:
        print("❌ Connection string is required")
        return False
    
    # Get Groq API key
    groq_key = input("Enter your Groq API key (optional): ").strip()
    
    # Create .env content
    env_content = f"""# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING="{connection_string}"
AZURE_DATA_CONTAINER="data"

# AI Model Configuration
GROQ_API_KEY="{groq_key if groq_key else 'your_groq_api_key_here'}"
GROQ_MODEL="llama3-70b-8192"

# API Configuration
API_HOST="localhost"
API_PORT="8000"
"""
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        
        print(f"✅ Created .env file at {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def add_azure_config(env_path):
    """Add Azure configuration to existing .env file"""
    print("\n📝 Adding Azure configuration to .env file...")
    
    # Get Azure connection string
    connection_string = input("Enter your Azure Storage connection string: ").strip()
    if not connection_string:
        print("❌ Connection string is required")
        return False
    
    # Read existing .env file
    try:
        with open(env_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read .env file: {e}")
        return False
    
    # Add Azure configuration
    azure_config = f"""
# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING="{connection_string}"
AZURE_DATA_CONTAINER="data"
"""
    
    try:
        with open(env_path, "a") as f:
            f.write(azure_config)
        
        print(f"✅ Added Azure configuration to {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def test_azure_connection():
    """Test Azure Blob Storage connection"""
    print("\n🔄 Testing Azure Blob Storage connection...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(__file__))
        
        from helpers.azure_blob_helper import get_azure_blob_helper
        
        azure_helper = get_azure_blob_helper()
        
        # Try to list containers (basic connectivity test)
        container_client = azure_helper.container_client
        container_client.get_container_properties()
        
        print("✅ Azure Blob Storage connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Azure connection failed: {e}")
        print("\nPlease check:")
        print("  1. Your connection string is correct")
        print("  2. The storage account exists")
        print("  3. The container 'data' exists")
        print("  4. You have proper permissions")
        return False

def setup_azure_container():
    """Set up the Azure container structure"""
    print("\n🔄 Setting up Azure container structure...")
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from helpers.azure_blob_helper import get_azure_blob_helper
        
        azure_helper = get_azure_blob_helper()
        
        # Create directory markers (optional, but helps with organization)
        directories = ["pdfs/", "faiss_store/", "confidential/"]
        
        for directory in directories:
            try:
                # Upload empty blob to create directory structure
                azure_helper.upload_file_data(b"", f"{directory}.keep")
                print(f"✅ Created directory: {directory}")
            except:
                # Directory might already exist
                pass
        
        print("✅ Azure container structure set up successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to set up container structure: {e}")
        return False

def show_next_steps():
    """Show next steps after successful setup"""
    print("\n" + "="*60)
    print("🎉 Azure Blob Storage setup completed successfully!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Upload your PDF files to Azure:")
    print("   python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs")
    
    print("\n2. Generate FAISS index from Azure PDFs:")
    print("   python helpers/azure_data_manager.py generate-index")
    
    print("\n3. Test the integration:")
    print("   python tests/test_azure_integration.py")
    
    print("\n4. Start the API server:")
    print("   python main.py")
    
    print("\n📚 Documentation:")
    print("   - Azure Integration Guide: docs/azure_integration.md")
    print("   - API Documentation: http://localhost:8000/docs")
    
    print("\n🔧 Management Commands:")
    print("   - List files: python helpers/azure_data_manager.py list-files")
    print("   - Sync data: python helpers/azure_data_manager.py sync")
    print("   - Download data: python helpers/azure_data_manager.py download-pdfs --output-dir ./downloads")

def main():
    """Main setup function"""
    print("🚀 Azure Blob Storage Setup for Legal Case Search API")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Check/create .env file
    if not check_env_file():
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Test Azure connection
    if not test_azure_connection():
        return False
    
    # Set up container structure
    if not setup_azure_container():
        return False
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)