# app/routes/voter/voter.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.enum import ServiceCode, Action
from app.core.auth import require_permission

from app.services.voter.voter import VoterService

# ========== SCHEMA IMPORTS ==========
from app.schemas.voter.voter import (
    VoterMasterCreate,
    VoterMasterResponse,
    VoterSearchParams,
    VoterListResponse,
    VoterAdditionalInfoCreate
)
from app.schemas.voter.client_voter import (
    ClientVoterDataResponse,
    ClientVoterStats,
    AssignVotersRequest,
    AssignVotersResponse,
    BulkDeleteRequest
)
from app.schemas.voter.import_schema import ImportResult

# ========== MODEL IMPORTS ==========
from app.models.voter.voter_master import VoterMaster
from app.models.voter.voter_additional_info import VoterAdditionalInfo
from app.models.voter.voter_import_log import VoterImportLog
from app.models.client.client import Client

router = APIRouter(prefix="/api/voters", tags=["Voters"])


# ============================================================
# 1. UPLOAD EXCEL - Everything goes in one Excel
# ============================================================

@router.post(
    "/import/excel/{client_id}", 
    response_model=ImportResult,
    summary="Upload Excel with ALL voter data",
    description="""
    Upload ONE Excel file that contains EVERYTHING:
    
    **Voter Master Fields:**
    - VoterId, Name_English, Name_Other, AC No & name, Booth No
    - Booth Name_English, Section No, SNo, Relation Type
    - Relation Name_English, Gender, House No_English, Age
    
    **Additional Info Fields (Client-Specific):**
    - Caste, Mobile, Voter Status, Designation, Vote Status
    
    **Client Info:**
    - Client Code
    
    Backend will automatically:
    1. Store core voter data → voter_master table
    2. Store additional info → voter_additional_info table
    3. Map with client_id and client_code
    4. Create JSON cache → client_voter_map table
    """
)
async def import_voters_from_excel(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.CREATE))
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Only Excel files allowed")
    
    content = await file.read()
    result = VoterService.process_excel_import(
        db=db,
        client_id=client_id,
        file_content=content,
        filename=file.filename,
        imported_by=current_user.id
    )
    return result


# ============================================================
# 2. SEARCH ALL VOTERS (Master Table) - With Filters & Pagination
# ============================================================

@router.get(
    "/search", 
    response_model=VoterListResponse,
    summary="Search all voters with filters and pagination",
    description="""
    Search across ALL voters in the master table with filters.
    
    **Filters Available:**
    - `search`: Search across name, voter_id, relation name
    - `ac_no`: Filter by assembly constituency
    - `booth_no`: Filter by booth number
    - `gender`: Filter by gender (M/F/O)
    - `age_min` / `age_max`: Age range filter
    - `voter_status`: Filter by voter status (Voted/Not Voted/Pending)
    - `vote_status`: Filter by vote status (Favor/Not Favor/Neutral)
    - `caste`: Filter by caste
    - `client_id`: Filter by client (shows voters assigned to this client)
    
    **Pagination:**
    - `skip`: Number of records to skip
    - `limit`: Number of records to return (max 1000)
    
    **Example:**
    - `GET /api/voters/search?search=singh&booth_no=1&age_min=25&age_max=60&skip=0&limit=20`
    """
)
def search_all_voters(
    # ========== SEARCH & TEXT FILTERS ==========
    search: Optional[str] = Query(None, description="Search across multiple text fields"),
    voter_id: Optional[str] = Query(None, description="Filter by voter ID"),
    name_english: Optional[str] = Query(None, description="Filter by English name"),
    name_other: Optional[str] = Query(None, description="Filter by other language name"),
    relation_name_english: Optional[str] = Query(None, description="Filter by relation name"),
    ac_no: Optional[str] = Query(None, description="Filter by assembly constituency number"),
    ac_name: Optional[str] = Query(None, description="Filter by assembly constituency name"),
    booth_no: Optional[str] = Query(None, description="Filter by booth number"),
    booth_name_english: Optional[str] = Query(None, description="Filter by booth name"),
    section_no: Optional[str] = Query(None, description="Filter by section number"),
    sno: Optional[str] = Query(None, description="Filter by serial number"),
    relation_type: Optional[str] = Query(None, description="Filter by relation type (H/F/M/S/D)"),
    gender: Optional[str] = Query(None, description="Filter by gender (M/F/O)"),
    house_no_english: Optional[str] = Query(None, description="Filter by house number"),
    
    # ========== ADDITIONAL INFO FILTERS ==========
    caste: Optional[str] = Query(None, description="Filter by caste"),
    mobile: Optional[str] = Query(None, description="Filter by mobile number"),
    voter_status: Optional[str] = Query(None, description="Filter by voter status (Voted/Not Voted/Pending)"),
    designation: Optional[str] = Query(None, description="Filter by designation"),
    vote_status: Optional[str] = Query(None, description="Filter by vote status (Favor/Not Favor/Neutral)"),
    client_code: Optional[str] = Query(None, description="Filter by client code"),
    
    # ========== RANGE FILTERS ==========
    age_min: Optional[int] = Query(None, description="Minimum age"),
    age_max: Optional[int] = Query(None, description="Maximum age"),
    created_at_from: Optional[datetime] = Query(None, description="Created from date"),
    created_at_to: Optional[datetime] = Query(None, description="Created to date"),
    
    # ========== CLIENT FILTER ==========
    client_id: Optional[str] = Query(None, description="Filter by client ID (shows voters assigned to this client)"),
    
    # ========== SORTING ==========
    sort_by: Optional[str] = Query("created_at", description="Sort field (name_english, voter_id, age, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    
    # ========== PAGINATION ==========
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.READ))
):
    try:
        params = VoterSearchParams(
            search=search,
            voter_id=voter_id,
            name_english=name_english,
            name_other=name_other,
            relation_name_english=relation_name_english,
            ac_no=ac_no,
            ac_name=ac_name,
            booth_no=booth_no,
            booth_name_english=booth_name_english,
            section_no=section_no,
            sno=sno,
            relation_type=relation_type,
            gender=gender,
            house_no_english=house_no_english,
            caste=caste,
            mobile=mobile,
            voter_status=voter_status,
            designation=designation,
            vote_status=vote_status,
            client_code=client_code,
            age_min=age_min,
            age_max=age_max,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            client_id=client_id,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        result = VoterService.search_voters_advanced(db, params)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error searching voters: {str(e)}")


# ============================================================
# 3. VIEW CLIENT VOTERS - See EVERYTHING combined
# ============================================================

@router.get(
    "/client/{client_id}", 
    response_model=ClientVoterDataResponse,
    summary="View complete voter list for a client",
    description="""
    Get COMPLETE voter data for a client with ALL fields combined.
    
    **Returns:**
    - Voter Master data (name, father, age, gender, AC, Booth, etc.)
    - Additional Info (caste, mobile, voter_status, designation)
    - Client-specific fields (vote_status, client_code)
    - Statistics (vote_status breakdown, voter_status breakdown, etc.)
    - All combined into one JSON response
    
    This is the SINGLE endpoint to see everything!
    """
)
def get_client_voters(
    client_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.READ))
):
    """
    Get all voters for a client with ALL fields combined from JSON cache.
    """
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(404, "Client not found")
        
        client_voter_map = VoterService.get_client_voter_map(db, client_id)
        
        if not client_voter_map or not client_voter_map.voter_data:
            return ClientVoterDataResponse(
                client_id=client_id,
                client_code=client.client_code,
                client_name=client.client_name,
                total_voters=0,
                last_updated=datetime.utcnow().isoformat(),
                voters={}
            )
        
        data = client_voter_map.voter_data
        stats = VoterService.get_client_voter_stats(db, client_id)
        
        return ClientVoterDataResponse(
            client_id=data.get("client_id", client_id),
            client_code=data.get("client_code", client.client_code),
            client_name=data.get("client_name", client.client_name),
            total_voters=data.get("total_voters", 0),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
            voters=data.get("voters", {}),
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error fetching client voters: {str(e)}")


# ============================================================
# 4. DELETE VOTER FROM CLIENT
# ============================================================

@router.delete(
    "/client/{client_id}/voter/{voter_id}",
    summary="Delete/Remove voter from client",
    description="""
    Remove a voter from a client.
    
    **What happens:**
    - Removes/soft deletes the voter from client's list
    - Deletes/soft deletes the additional info record
    - Removes voter from client's JSON cache
    - Voter remains in master table (can be assigned to other clients)
    
    **Permissions Required:**
    - `DELETE` permission on VOTERS service
    - Platform Admin, Client Admin, or User with DELETE permission
    """
)
def delete_voter_from_client(
    client_id: str,
    voter_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.DELETE))
):
    """
    Remove a voter from a client (soft delete additional info).
    """
    try:
        # Check if client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(404, "Client not found")
        
        # Check if voter exists
        voter = db.query(VoterMaster).filter(
            VoterMaster.voter_id == voter_id,
            VoterMaster.is_active == True
        ).first()
        if not voter:
            raise HTTPException(404, "Voter not found")
        
        # Check if voter is assigned to this client
        info = VoterService.get_additional_info(db, voter.id, client_id)
        if not info:
            raise HTTPException(404, "Voter not assigned to this client")
        
        # Delete/soft delete the additional info
        result = VoterService.delete_additional_info(db, voter.id, client_id)
        
        # Update client's JSON cache
        VoterService.update_client_voter_map(db, client_id)
        
        return {
            "success": True,
            "message": "Voter removed from client successfully",
            "voter_id": voter_id,
            "client_id": client_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error removing voter from client: {str(e)}")


# ============================================================
# 5. BULK DELETE VOTERS FROM CLIENT
# ============================================================

@router.delete(
    "/client/{client_id}/voters/bulk",
    summary="Bulk delete voters from client",
    description="""
    Remove multiple voters from a client.
    
    **Request Body:**
    ```json
    {
        "voter_ids": ["voter_id1", "voter_id2", "voter_id3"]
    }
    ```
    
    **Permissions Required:**
    - `DELETE` permission on VOTERS service
    """
)
def bulk_delete_voters_from_client(
    client_id: str,
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.DELETE))
):
    """
    Remove multiple voters from a client.
    """
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(404, "Client not found")
        
        deleted_count = 0
        not_found_count = 0
        errors = []
        
        for voter_id in request.voter_ids:
            try:
                voter = db.query(VoterMaster).filter(
                    VoterMaster.voter_id == voter_id,
                    VoterMaster.is_active == True
                ).first()
                
                if not voter:
                    not_found_count += 1
                    errors.append({"voter_id": voter_id, "error": "Voter not found"})
                    continue
                
                info = VoterService.get_additional_info(db, voter.id, client_id)
                if not info:
                    errors.append({"voter_id": voter_id, "error": "Voter not assigned to this client"})
                    continue
                
                VoterService.delete_additional_info(db, voter.id, client_id)
                deleted_count += 1
                
            except Exception as e:
                errors.append({"voter_id": voter_id, "error": str(e)})
        
        # Update client's JSON cache
        if deleted_count > 0:
            VoterService.update_client_voter_map(db, client_id)
        
        return {
            "success": True,
            "message": f"Removed {deleted_count} voters from client",
            "deleted_count": deleted_count,
            "not_found_count": not_found_count,
            "errors": errors if errors else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error removing voters: {str(e)}")


# ============================================================
# 6. (Optional) Get client voter statistics
# ============================================================

@router.get(
    "/client/{client_id}/stats", 
    response_model=ClientVoterStats,
    summary="Get client voter statistics",
    description="""
    Get detailed statistics for a client's voters.
    
    **Returns:**
    - Total voters
    - By vote status (Favor/Not Favor/Neutral)
    - By voter status (Voted/Not Voted/Pending)
    - By caste
    - By gender
    - By booth
    - By assembly constituency
    """
)
def get_client_voter_stats(
    client_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.READ))
):
    try:
        stats = VoterService.get_client_voter_stats(db, client_id)
        return stats
    except Exception as e:
        raise HTTPException(500, f"Error fetching stats: {str(e)}")


# ============================================================
# 7. ASSIGN VOTERS TO CLIENT
# ============================================================

@router.post(
    "/client/{client_id}/assign", 
    response_model=AssignVotersResponse,
    summary="Assign voters to a client"
)
def assign_voters_to_client(
    client_id: str,
    request: AssignVotersRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(ServiceCode.VOTERS, Action.CREATE))
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(404, "Client not found")
    
    assigned_count = 0
    skipped_count = 0
    errors = []
    
    for voter_id in request.voter_ids:
        voter = VoterService.get_voter_by_id(db, voter_id)
        if not voter:
            errors.append({"voter_id": voter_id, "error": "Voter not found"})
            continue
        
        existing = VoterService.get_additional_info(db, voter_id, client_id)
        if existing:
            skipped_count += 1
            continue
        
        info_data = VoterAdditionalInfoCreate(
            voter_id=voter_id,
            client_id=client_id,
            client_code=client.client_code,
            vote_status="Not Contacted",
            voter_status="Pending",
            is_active=True
        )
        VoterService.create_additional_info(db, info_data)
        assigned_count += 1
    
    if assigned_count > 0:
        VoterService.update_client_voter_map(db, client_id)
    
    return AssignVotersResponse(
        assigned_count=assigned_count,
        skipped_duplicates=skipped_count,
        failed_count=len(errors),
        errors=errors if errors else None
    )