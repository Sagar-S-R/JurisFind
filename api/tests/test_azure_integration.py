"""
Azure Blob Storage Integration Test Script

This script tests the Azure Blob Storage integration for the Legal Case Search API.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add API directory to path
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from helpers.azure_blob_helper import get_azure_blob_helper
from services.search_service import get_searcher

# Load environment variables
load_dotenv()

def test_azure_connection():
    """Test basic Azure Blob Storage connection"""
    print("🔄 Testing Azure Blob Storage connection...")
    
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        print("❌ AZURE_STORAGE_CONNECTION_STRING not set")
        return False
    
    try:
        azure_helper = get_azure_blob_helper(connection_string)
        print("✅ Azure Blob Storage connection successful")
        return True
    except Exception as e:
        print(f"❌ Azure connection failed: {e}")
        return False

def test_list_pdfs():
    """Test listing PDF files from Azure"""
    print("\n🔄 Testing PDF file listing...")
    
    try:
        azure_helper = get_azure_blob_helper()
        pdf_files = azure_helper.list_pdf_files()
        
        print(f"✅ Found {len(pdf_files)} PDF files in Azure Blob Storage")
        if pdf_files:
            print("📁 Sample files:")
            for i, pdf in enumerate(pdf_files[:5]):  # Show first 5
                print(f"   {i+1}. {pdf}")
            if len(pdf_files) > 5:
                print(f"   ... and {len(pdf_files) - 5} more")
        
        return len(pdf_files) > 0
    except Exception as e:
        print(f"❌ Failed to list PDF files: {e}")
        return False

def test_download_pdf():
    """Test downloading a PDF file"""
    print("\n🔄 Testing PDF download...")
    
    try:
        azure_helper = get_azure_blob_helper()
        pdf_files = azure_helper.list_pdf_files()
        
        if not pdf_files:
            print("⚠️  No PDF files available for download test")
            return False
        
        # Test download of first PDF
        test_pdf = pdf_files[0]
        temp_path = azure_helper.download_pdf_to_temp_file(test_pdf)
        
        if temp_path and os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            print(f"✅ Successfully downloaded {test_pdf} ({file_size} bytes)")
            
            # Cleanup
            os.unlink(temp_path)
            return True
        else:
            print(f"❌ Failed to download {test_pdf}")
            return False
            
    except Exception as e:
        print(f"❌ PDF download test failed: {e}")
        return False

def test_faiss_index_download():
    """Test downloading FAISS index from Azure"""
    print("\n🔄 Testing FAISS index download...")
    
    try:
        azure_helper = get_azure_blob_helper()
        faiss_files = azure_helper.download_faiss_index()
        
        if faiss_files:
            index_path = faiss_files["index_path"]
            id2name_path = faiss_files["id2name_path"]
            
            # Check if files exist and have content
            index_size = os.path.getsize(index_path)
            id2name_size = os.path.getsize(id2name_path)
            
            print(f"✅ FAISS index downloaded: {index_size} bytes")
            print(f"✅ ID mapping downloaded: {id2name_size} bytes")
            
            # Load and check ID mapping
            import json
            with open(id2name_path, 'r') as f:
                id2name = json.load(f)
            
            print(f"✅ Index contains {len(id2name)} documents")
            
            # Cleanup
            try:
                os.unlink(index_path)
                os.unlink(id2name_path)
                os.rmdir(faiss_files["temp_dir"])
            except:
                pass
            
            return True
        else:
            print("❌ Failed to download FAISS index")
            return False
            
    except Exception as e:
        print(f"❌ FAISS index download test failed: {e}")
        return False

def test_search_service():
    """Test the search service with Azure integration"""
    print("\n🔄 Testing search service with Azure...")
    
    try:
        searcher = get_searcher()
        
        # Test search
        test_query = "contract law legal agreement"
        results = searcher.search(test_query, top_k=3)
        
        print(f"✅ Search successful: {len(results)} results for '{test_query}'")
        
        if results:
            print("🔍 Top results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['filename']} (score: {result['similarity_percentage']}%)")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Search service test failed: {e}")
        return False

def test_blob_metadata():
    """Test getting blob metadata"""
    print("\n🔄 Testing blob metadata...")
    
    try:
        azure_helper = get_azure_blob_helper()
        
        # Test FAISS index metadata
        index_metadata = azure_helper.get_blob_metadata("faiss_store/legal_cases.index")
        id2name_metadata = azure_helper.get_blob_metadata("faiss_store/id2name.json")
        
        if index_metadata and id2name_metadata:
            print(f"✅ FAISS index: {index_metadata['size']} bytes, modified: {index_metadata['last_modified']}")
            print(f"✅ ID mapping: {id2name_metadata['size']} bytes, modified: {id2name_metadata['last_modified']}")
            return True
        else:
            print("❌ Failed to get blob metadata")
            return False
            
    except Exception as e:
        print(f"❌ Blob metadata test failed: {e}")
        return False

def run_all_tests():
    """Run all Azure integration tests"""
    print("🧪 Starting Azure Blob Storage Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Azure Connection", test_azure_connection),
        ("List PDF Files", test_list_pdfs),
        ("Download PDF", test_download_pdf),
        ("FAISS Index Download", test_faiss_index_download),
        ("Search Service", test_search_service),
        ("Blob Metadata", test_blob_metadata)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("🧪 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Azure integration is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check your Azure configuration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)