from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from sqlalchemy.orm import Session
import tempfile
import os
import pandas as pd
from app.core.database import get_db
from app.services.hierarchy.import_service import ImportService
from app.core.exceptions import ValidationException, DatabaseException

router = APIRouter(prefix="/api/v1/hierarchy/import", tags=["Hierarchy - Import"])

@router.post(
    "/assembly-blocks",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Import successful"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def import_assembly_blocks(
    file: UploadFile = File(..., description="Excel file with assembly, block, ward, booth data"),
    update_mode: bool = Query(False, description="True: Update existing records, False: Skip existing"),
    db: Session = Depends(get_db)
):
    """
    Import Assembly, Blocks, Panchayat Wards, and Polling Booths from Excel.
    
    Required columns:
    - pc_district_code: PC District code
    - assembly_code: Assembly code
    - assembly_name: Assembly name
    - block_code: Block code
    - block_name: Block name
    - panchayat_ward_code: Panchayat Ward code
    - panchayat_ward_name: Panchayat Ward name
    - booth_code: Booth code
    - booth_name: Booth name
    - booth_number: Booth number
    
    Optional columns:
    - state_code, country_code (for PC District lookup)
    - assembly_number, constituency_type, assembly_population
    - block_number, block_type, block_area
    - ward_number, ward_type, pincode, ward_population
    - address, latitude, longitude, polling_station_type, booth_capacity, facilities, is_accessible
    """
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be Excel format (.xlsx or .xls)"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process import
        service = ImportService(db)
        result = service.import_from_excel(tmp_file_path, update_mode)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return result
        
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

@router.post(
    "/assembly-blocks/csv",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Import successful"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def import_assembly_blocks_csv(
    file: UploadFile = File(..., description="CSV file with assembly, block, ward, booth data"),
    update_mode: bool = Query(False, description="True: Update existing records, False: Skip existing"),
    db: Session = Depends(get_db)
):
    """
    Import Assembly, Blocks, Panchayat Wards, and Polling Booths from CSV.
    Same columns as Excel import.
    """
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV format"
        )
    
    try:
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content), dtype=str)
        
        # Process import
        service = ImportService(db)
        result = service.import_from_dataframe(df, update_mode)
        
        return result
        
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )

@router.get(
    "/assembly-blocks/template",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Template downloaded successfully"},
        500: {"description": "Internal server error"}
    }
)
async def download_assembly_blocks_template():
    """Download Excel template for Assembly/Blocks/Boards import"""
    from fastapi.responses import FileResponse
    
    try:
        # Create template
        template_data = {
            'country_code': ['IN'],
            'state_code': ['MH'],
            'pc_district_code': ['PUNE'],
            'assembly_code': ['PUNE_AC1'],
            'assembly_name': ['Pune Cantonment'],
            'assembly_number': [1],
            'constituency_type': ['General'],
            'assembly_population': ['100000'],
            'block_code': ['PUNE_B1'],
            'block_name': ['Pune City Block'],
            'block_number': [1],
            'block_type': ['Urban'],
            'block_area': ['100 sq km'],
            'panchayat_ward_code': ['KP_WARD'],
            'panchayat_ward_name': ['Koregaon Park'],
            'ward_number': [1],
            'ward_type': ['Urban'],
            'pincode': ['411001'],
            'ward_population': ['5000'],
            'booth_code': ['KP_B1'],
            'booth_name': ['Koregaon Park Booth 1'],
            'booth_number': [1],
            'address': ['KP School, Koregaon Park, Pune'],
            'latitude': ['18.5204'],
            'longitude': ['73.8567'],
            'polling_station_type': ['PERMANENT'],
            'booth_capacity': ['500'],
            'facilities': ['Wheelchair accessible, Parking'],
            'is_accessible': ['true']
        }
        
        df = pd.DataFrame(template_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='assembly_blocks_import_template.xlsx'
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )

@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Status retrieved successfully"}
    }
)
async def get_import_status():
    """Get import service status"""
    return {
        "status": "healthy",
        "supported_operations": [
            "Import Assembly, Blocks, Panchayat Wards, Polling Booths",
            "Bulk Update (update existing records)",
            "Excel and CSV support"
        ],
        "required_columns": [
            "pc_district_code",
            "assembly_code", 
            "assembly_name",
            "block_code",
            "block_name",
            "panchayat_ward_code",
            "panchayat_ward_name",
            "booth_code",
            "booth_name",
            "booth_number"
        ]
    }