import zipfile
import os

# Path to ZIP file in the root directory
zip_path = os.path.join(os.path.dirname(__file__), "archive.zip")

# Extract to the root directory (same as script location)
extract_dir = os.path.dirname(__file__)

print(f"📦 Extracting ALL PDFs from archive.zip to: {extract_dir}")

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    pdf_files = [f for f in zip_ref.namelist() if f.endswith(".pdf")]
    # Remove the limit - extract ALL PDFs
    print(f"📄 Found {len(pdf_files)} PDF files in the archive")
    
    print("🚀 Starting extraction... This may take a while for large archives.")
    
    for i, file in enumerate(pdf_files, 1):
        zip_ref.extract(file, path=extract_dir)  # keep internal structure
        
        # Show progress every 1000 files
        if i % 1000 == 0:
            print(f"✅ Extracted {i}/{len(pdf_files)} PDFs...")

print(f"🎉 Successfully extracted ALL {len(pdf_files)} PDFs to: {extract_dir}")
