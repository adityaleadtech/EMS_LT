#!/usr/bin/env python
"""
Bulk import script for large files
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.hierarchy.import_service import ImportService
import pandas as pd


def bulk_import(file_path: str, chunk_size: int = 5000):
    """Import large files in chunks"""
    
    db = SessionLocal()
    service = ImportService(db)
    
    print(f"🚀 Starting import from {file_path}")
    print(f"📦 Using chunk size: {chunk_size}")
    start_time = time.time()
    
    try:
        # Check file type
        if file_path.endswith('.csv'):
            chunks = pd.read_csv(file_path, chunksize=chunk_size, dtype=str)
        else:
            chunks = pd.read_excel(file_path, chunksize=chunk_size, dtype=str)
        
        total_processed = 0
        chunk_num = 0
        
        for chunk in chunks:
            chunk_num += 1
            print(f"\n📊 Processing chunk {chunk_num}...")
            
            # Clean column names
            chunk.columns = chunk.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Process chunk
            result = service.import_from_dataframe(chunk)
            total_processed += result['summary']['total_processed']
            
            print(f"✅ Chunk {chunk_num} completed")
            print(f"   - Records: {result['summary']['total_processed']}")
            print(f"   - Success: {result['summary']['success_count']}")
            print(f"   - Errors: {result['summary']['errors']}")
            
            if result['summary'].get('error_messages'):
                print(f"   - First error: {result['summary']['error_messages'][0]}")
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Total records processed: {total_processed}")
        print(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
        print(f"📈 Average speed: {total_processed / elapsed_time:.2f} records/second")
        
        # Show summary
        print("\n📋 Import Summary:")
        print(f"   - Countries: {service.stats['countries']}")
        print(f"   - States: {service.stats['states']}")
        print(f"   - PC Districts: {service.stats['pc_districts']}")
        print(f"   - Assemblies: {service.stats['assemblies']}")
        print(f"   - Blocks: {service.stats['blocks']}")
        print(f"   - Panchayat Wards: {service.stats['panchayat_wards']}")
        print(f"   - Polling Booths: {service.stats['polling_booths']}")
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        db.rollback()
    finally:
        db.close()

def show_usage():
    print("""
    📖 USAGE
    ========
    python bulk_import.py <excel_or_csv_file> [chunk_size]
    
    Examples:
    ---------
    # Import with default chunk size (5000)
    python bulk_import.py data.xlsx
    
    # Import with custom chunk size (10000)
    python bulk_import.py data.xlsx 10000
    
    # Import CSV file
    python bulk_import.py data.csv
    
    # Import CSV with custom chunk size
    python bulk_import.py data.csv 20000
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    bulk_import(file_path, chunk_size)