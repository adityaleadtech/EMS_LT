# app/services/voter/voter.py
import pandas as pd
import json
import uuid
import re
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from datetime import datetime

# ========== FIXED: Import from models/voter/ ==========
from app.models.voter.voter_master import VoterMaster
from app.models.voter.voter_additional_info import VoterAdditionalInfo
from app.models.voter.client_voter_map import ClientVoterMap
from app.models.voter.voter_import_log import VoterImportLog
from app.models.voter.voter_activity_log import VoterActivityLog
from app.models.voter.voter_group_master import VoterGroupMaster
from app.models.voter.voter_group_mapping import VoterGroupMapping

# ========== Existing model imports ==========
from app.models.client.client import Client
from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.polling_booth import PollingBooth
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.models.hierarchy.pc_district import PCDistrict
# ========== Schema imports ==========
from app.schemas.voter.voter import (
    VoterMasterCreate,
    VoterMasterUpdate,
    VoterAdditionalInfoCreate,
    VoterAdditionalInfoUpdate,
    VoterSearchParams
)


class VoterService:
    
    # ============================================================
    # VOTER MASTER OPERATIONS
    # ============================================================
    
    @staticmethod
    def get_voter_by_voter_id(db: Session, voter_id: str) -> Optional[VoterMaster]:
        """Get voter by voter_id"""
        return db.query(VoterMaster).filter(
            VoterMaster.voter_id == voter_id,
            VoterMaster.is_active == True
        ).first()
    
    @staticmethod
    def get_voter_by_id(db: Session, id: str) -> Optional[VoterMaster]:
        """Get voter by UUID"""
        return db.query(VoterMaster).filter(
            VoterMaster.id == id,
            VoterMaster.is_active == True
        ).first()
    
    @staticmethod
    def get_voter_with_details(db: Session, voter_id: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get voter with additional info and related data"""
        voter = VoterService.get_voter_by_voter_id(db, voter_id)
        if not voter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voter with ID {voter_id} not found"
            )
        
        result = {
            "id": voter.id,
            "voter_id": voter.voter_id,
            "ac_no": voter.ac_no,
            "ac_name": voter.ac_name,
            "assembly_id": voter.assembly_id,
            "booth_no": voter.booth_no,
            "booth_name_english": voter.booth_name_english,
            "booth_name_other": voter.booth_name_other,
            "booth_id": voter.booth_id,
            "panchayat_ward_id": voter.panchayat_ward_id,
            "pc_district_id": voter.pc_district_id,
            "section_no": voter.section_no,
            "section_name_english": voter.section_name_english,
            "section_name_other": voter.section_name_other,
            "sno": voter.sno,
            "name_english": voter.name_english,
            "name_other": voter.name_other,
            "relation_type": voter.relation_type,
            "relation_name_english": voter.relation_name_english,
            "relation_name_other": voter.relation_name_other,
            "gender": voter.gender,
            "house_no_english": voter.house_no_english,
            "house_no_other": voter.house_no_other,
            "age": voter.age,
            "created_at": voter.created_at,
            "updated_at": voter.updated_at
        }
        
        # Add related data
        if voter.assembly:
            result["assembly"] = {
                "id": voter.assembly.id,
                "code": voter.assembly.code,
                "name": voter.assembly.name
            }
        
        if voter.booth:
            result["booth"] = {
                "id": voter.booth.id,
                "code": voter.booth.code,
                "name": voter.booth.name,
                "booth_number": voter.booth.booth_number
            }
        
        if client_id:
            info = db.query(VoterAdditionalInfo).filter(
                and_(
                    VoterAdditionalInfo.voter_id == voter.id,
                    VoterAdditionalInfo.client_id == client_id,
                    VoterAdditionalInfo.is_active == True
                )
            ).first()
            if info:
                result["additional_info"] = {
                    "caste": info.caste,
                    "mobile": info.mobile,
                    "voter_status": info.voter_status,
                    "designation": info.designation,
                    "vote_status": info.vote_status,
                    "remarks": info.remarks,
                    "client_code": info.client_code
                }
        
        return result
    
    @staticmethod
    def create_voter(db: Session, voter_data: VoterMasterCreate) -> VoterMaster:
        """Create a new voter"""
        existing = VoterService.get_voter_by_voter_id(db, voter_data.voter_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Voter with ID {voter_data.voter_id} already exists"
            )
        
        voter = VoterMaster(
            id=str(uuid.uuid4()),
            **voter_data.dict(exclude_unset=True)
        )
        db.add(voter)
        db.commit()
        db.refresh(voter)
        return voter
    
    @staticmethod
    def create_or_update_voter(db: Session, voter_data: Dict[str, Any]) -> VoterMaster:
        """Create or update voter based on voter_id"""
        voter_id = voter_data.get("voter_id")
        if not voter_id:
            raise ValueError("voter_id is required")
        
        existing = VoterService.get_voter_by_voter_id(db, voter_id)
        
        if existing:
            for key, value in voter_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            voter = VoterMaster(
                id=str(uuid.uuid4()),
                **voter_data
            )
            db.add(voter)
            db.commit()
            db.refresh(voter)
            return voter
    
    @staticmethod
    def update_voter(db: Session, voter_id: str, update_data: VoterMasterUpdate) -> VoterMaster:
        """Update voter"""
        voter = VoterService.get_voter_by_voter_id(db, voter_id)
        if not voter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voter with ID {voter_id} not found"
            )
        
        for key, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(voter, key, value)
        
        db.commit()
        db.refresh(voter)
        return voter
    
    @staticmethod
    def delete_voter(db: Session, voter_id: str) -> bool:
        """Soft delete voter"""
        voter = VoterService.get_voter_by_voter_id(db, voter_id)
        if not voter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voter with ID {voter_id} not found"
            )
        
        voter.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def search_voters_advanced(
        db: Session, 
        params: VoterSearchParams,
    ) -> Dict[str, Any]:
        """
        Advanced search with extreme filtering capabilities.
        Supports filtering on ALL fields.
        """
        query = db.query(VoterMaster).filter(VoterMaster.is_active == True)
        
        # Track if we need to join additional_info
        need_additional_join = False
        
        # ============================================================
        # TEXT SEARCH - Primary search across multiple fields
        # ============================================================
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    VoterMaster.voter_id.ilike(search_term),
                    VoterMaster.name_english.ilike(search_term),
                    VoterMaster.name_other.ilike(search_term),
                    VoterMaster.relation_name_english.ilike(search_term),
                    VoterMaster.relation_name_other.ilike(search_term),
                    VoterMaster.ac_no.ilike(search_term),
                    VoterMaster.ac_name.ilike(search_term),
                    VoterMaster.booth_no.ilike(search_term),
                    VoterMaster.booth_name_english.ilike(search_term),
                    VoterMaster.booth_name_other.ilike(search_term),
                    VoterMaster.section_no.ilike(search_term),
                    VoterMaster.section_name_english.ilike(search_term),
                    VoterMaster.section_name_other.ilike(search_term),
                    VoterMaster.house_no_english.ilike(search_term),
                    VoterMaster.house_no_other.ilike(search_term),
                    VoterMaster.sno.ilike(search_term),
                    VoterMaster.relation_type.ilike(search_term),
                    VoterMaster.gender.ilike(search_term)
                )
            )
        
        # ============================================================
        # VOTER MASTER TEXT FILTERS
        # ============================================================
        if params.voter_id:
            query = query.filter(VoterMaster.voter_id.ilike(f"%{params.voter_id}%"))
        
        if params.name_english:
            query = query.filter(VoterMaster.name_english.ilike(f"%{params.name_english}%"))
        
        if params.name_other:
            query = query.filter(VoterMaster.name_other.ilike(f"%{params.name_other}%"))
        
        if params.relation_name_english:
            query = query.filter(VoterMaster.relation_name_english.ilike(f"%{params.relation_name_english}%"))
        
        if params.relation_name_other:
            query = query.filter(VoterMaster.relation_name_other.ilike(f"%{params.relation_name_other}%"))
        
        if params.ac_no:
            query = query.filter(VoterMaster.ac_no.ilike(f"%{params.ac_no}%"))
        
        if params.ac_name:
            query = query.filter(VoterMaster.ac_name.ilike(f"%{params.ac_name}%"))
        
        if params.booth_no:
            query = query.filter(VoterMaster.booth_no.ilike(f"%{params.booth_no}%"))
        
        if params.booth_name_english:
            query = query.filter(VoterMaster.booth_name_english.ilike(f"%{params.booth_name_english}%"))
        
        if params.booth_name_other:
            query = query.filter(VoterMaster.booth_name_other.ilike(f"%{params.booth_name_other}%"))
        
        if params.section_no:
            query = query.filter(VoterMaster.section_no.ilike(f"%{params.section_no}%"))
        
        if params.section_name_english:
            query = query.filter(VoterMaster.section_name_english.ilike(f"%{params.section_name_english}%"))
        
        if params.section_name_other:
            query = query.filter(VoterMaster.section_name_other.ilike(f"%{params.section_name_other}%"))
        
        if params.sno:
            query = query.filter(VoterMaster.sno.ilike(f"%{params.sno}%"))
        
        if params.house_no_english:
            query = query.filter(VoterMaster.house_no_english.ilike(f"%{params.house_no_english}%"))
        
        if params.house_no_other:
            query = query.filter(VoterMaster.house_no_other.ilike(f"%{params.house_no_other}%"))
        
        if params.relation_type:
            query = query.filter(VoterMaster.relation_type.ilike(f"%{params.relation_type}%"))
        
        if params.gender:
            query = query.filter(VoterMaster.gender == params.gender)
        
        # ============================================================
        # UUID / FOREIGN KEY FILTERS
        # ============================================================
        if params.assembly_id:
            query = query.filter(VoterMaster.assembly_id == params.assembly_id)
        
        if params.booth_id:
            query = query.filter(VoterMaster.booth_id == params.booth_id)
        
        if params.panchayat_ward_id:
            query = query.filter(VoterMaster.panchayat_ward_id == params.panchayat_ward_id)
        
        if params.pc_district_id:
            query = query.filter(VoterMaster.pc_district_id == params.pc_district_id)
        
        # ============================================================
        # ADDITIONAL INFO FILTERS
        # ============================================================
        if params.client_id:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(
                VoterAdditionalInfo.client_id == params.client_id,
                VoterAdditionalInfo.is_active == True
            )
        
        if params.caste:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(VoterAdditionalInfo.caste.ilike(f"%{params.caste}%"))
        
        if params.mobile:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(VoterAdditionalInfo.mobile.ilike(f"%{params.mobile}%"))
        
        if params.voter_status:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(VoterAdditionalInfo.voter_status == params.voter_status)
        
        if params.designation:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(VoterAdditionalInfo.designation.ilike(f"%{params.designation}%"))
        
        if params.vote_status:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(VoterAdditionalInfo.vote_status == params.vote_status)
        
        if params.client_code:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            ).filter(VoterAdditionalInfo.client_code.ilike(f"%{params.client_code}%"))
        
        # ============================================================
        # BOOLEAN FILTERS
        # ============================================================
        if params.has_additional_info is not None:
            if params.has_additional_info:
                query = query.join(
                    VoterAdditionalInfo,
                    VoterMaster.id == VoterAdditionalInfo.voter_id
                ).filter(VoterAdditionalInfo.is_active == True)
            else:
                query = query.outerjoin(
                    VoterAdditionalInfo,
                    and_(
                        VoterMaster.id == VoterAdditionalInfo.voter_id,
                        VoterAdditionalInfo.is_active == True
                    )
                ).filter(VoterAdditionalInfo.id.is_(None))
        
        if params.is_voted is not None:
            need_additional_join = True
            query = query.join(
                VoterAdditionalInfo,
                VoterMaster.id == VoterAdditionalInfo.voter_id
            )
            if params.is_voted:
                query = query.filter(VoterAdditionalInfo.voter_status == "Voted")
            else:
                query = query.filter(VoterAdditionalInfo.voter_status != "Voted")
        
        # ============================================================
        # RANGE FILTERS
        # ============================================================
        if params.age_min is not None:
            query = query.filter(VoterMaster.age >= params.age_min)
        
        if params.age_max is not None:
            query = query.filter(VoterMaster.age <= params.age_max)
        
        if params.created_at_from:
            query = query.filter(VoterMaster.created_at >= params.created_at_from)
        
        if params.created_at_to:
            query = query.filter(VoterMaster.created_at <= params.created_at_to)
        
        if params.updated_at_from:
            query = query.filter(VoterMaster.updated_at >= params.updated_at_from)
        
        if params.updated_at_to:
            query = query.filter(VoterMaster.updated_at <= params.updated_at_to)
        
        # ============================================================
        # IS ACTIVE FILTER
        # ============================================================
        if params.is_active is not None:
            query = query.filter(VoterMaster.is_active == params.is_active)
        
        # ============================================================
        # SORTING (Dynamic)
        # ============================================================
        sort_field = params.sort_by or "created_at"
        sort_order = params.sort_order or "desc"
        
        sort_mapping = {
            "voter_id": VoterMaster.voter_id,
            "name_english": VoterMaster.name_english,
            "name_other": VoterMaster.name_other,
            "ac_no": VoterMaster.ac_no,
            "ac_name": VoterMaster.ac_name,
            "booth_no": VoterMaster.booth_no,
            "booth_name_english": VoterMaster.booth_name_english,
            "gender": VoterMaster.gender,
            "age": VoterMaster.age,
            "relation_type": VoterMaster.relation_type,
            "sno": VoterMaster.sno,
            "created_at": VoterMaster.created_at,
            "updated_at": VoterMaster.updated_at,
            "is_active": VoterMaster.is_active
        }
        
        # For additional info sorting
        if sort_field in ["vote_status", "voter_status", "caste", "mobile", "designation"]:
            need_additional_join = True
            if not any([
                params.client_id, params.caste, params.mobile, 
                params.voter_status, params.designation, params.vote_status, 
                params.client_code
            ]):
                query = query.join(
                    VoterAdditionalInfo,
                    VoterMaster.id == VoterAdditionalInfo.voter_id
                )
            
            if sort_field == "vote_status":
                sort_column = VoterAdditionalInfo.vote_status
            elif sort_field == "voter_status":
                sort_column = VoterAdditionalInfo.voter_status
            elif sort_field == "caste":
                sort_column = VoterAdditionalInfo.caste
            elif sort_field == "mobile":
                sort_column = VoterAdditionalInfo.mobile
            elif sort_field == "designation":
                sort_column = VoterAdditionalInfo.designation
            else:
                sort_column = VoterMaster.created_at
        else:
            sort_column = sort_mapping.get(sort_field, VoterMaster.created_at)
        
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # ============================================================
        # DISTINCT
        # ============================================================
        if need_additional_join or params.has_additional_info is not None:
            query = query.distinct()
        
        # ============================================================
        # PAGINATION
        # ============================================================
        total = query.count()
        voters = query.offset(params.skip).limit(params.limit).all()
        
        return {
            "total": total,
            "skip": params.skip,
            "limit": params.limit,
            "voters": voters
        }
    
    # ============================================================
    # ADDITIONAL INFO OPERATIONS
    # ============================================================
    
    @staticmethod
    def get_additional_info(
        db: Session, 
        voter_id: str, 
        client_id: str
    ) -> Optional[VoterAdditionalInfo]:
        """Get additional info for a voter-client combination"""
        return db.query(VoterAdditionalInfo).filter(
            and_(
                VoterAdditionalInfo.voter_id == voter_id,
                VoterAdditionalInfo.client_id == client_id,
                VoterAdditionalInfo.is_active == True
            )
        ).first()
    
    @staticmethod
    def create_additional_info(
        db: Session, 
        info_data: VoterAdditionalInfoCreate
    ) -> VoterAdditionalInfo:
        """Create additional info for a voter"""
        voter = VoterService.get_voter_by_id(db, info_data.voter_id)
        if not voter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voter with id {info_data.voter_id} not found"
            )
        
        existing = VoterService.get_additional_info(db, info_data.voter_id, info_data.client_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Additional info already exists for this voter and client"
            )
        
        info = VoterAdditionalInfo(
            id=str(uuid.uuid4()),
            **info_data.dict()
        )
        db.add(info)
        db.commit()
        db.refresh(info)
        return info
    
    @staticmethod
    def update_additional_info(
        db: Session, 
        voter_id: str, 
        client_id: str, 
        update_data: VoterAdditionalInfoUpdate
    ) -> VoterAdditionalInfo:
        """Update additional info"""
        info = VoterService.get_additional_info(db, voter_id, client_id)
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Additional info not found for this voter and client"
            )
        
        for key, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(info, key, value)
        
        db.commit()
        db.refresh(info)
        return info
    
    @staticmethod
    def delete_additional_info(db: Session, voter_id: str, client_id: str) -> bool:
        """Soft delete additional info"""
        info = VoterService.get_additional_info(db, voter_id, client_id)
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Additional info not found"
            )
        
        info.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def bulk_update_vote_status(
        db: Session, 
        client_id: str, 
        voter_ids: List[str], 
        vote_status: str
    ) -> int:
        """Bulk update vote status for multiple voters"""
        updated = db.query(VoterAdditionalInfo).filter(
            and_(
                VoterAdditionalInfo.client_id == client_id,
                VoterAdditionalInfo.voter_id.in_(voter_ids),
                VoterAdditionalInfo.is_active == True
            )
        ).update(
            {"vote_status": vote_status},
            synchronize_session=False
        )
        db.commit()
        return updated

    # ============================================================
    # CLIENT VOTER MAP OPERATIONS
    # ============================================================
    
    @staticmethod
    def get_client_voter_map(db: Session, client_id: str) -> Optional[ClientVoterMap]:
        """Get client voter map by client_id"""
        return db.query(ClientVoterMap).filter(
            ClientVoterMap.client_id == client_id
        ).first()
    
    @staticmethod
    def update_client_voter_map(db: Session, client_id: str) -> ClientVoterMap:
        """Update or create client voter map"""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with id {client_id} not found"
            )
        
        voters = db.query(VoterMaster).join(
            VoterAdditionalInfo,
            VoterMaster.id == VoterAdditionalInfo.voter_id
        ).filter(
            VoterAdditionalInfo.client_id == client_id,
            VoterAdditionalInfo.is_active == True,
            VoterMaster.is_active == True
        ).all()
        
        voter_data = {
            "client_id": client_id,
            "client_code": client.client_code,
            "client_name": client.client_name,
            "total_voters": len(voters),
            "last_updated": datetime.utcnow().isoformat(),
            "voters": {}
        }
        
        for voter in voters:
            info = next(
                (i for i in voter.additional_info if i.client_id == client_id),
                None
            )
            
            voter_info = {
                "id": voter.id,
                "voter_id": voter.voter_id,
                "name_english": voter.name_english,
                "name_other": voter.name_other,
                "assembly_id": voter.assembly_id,
                "ac_no": voter.ac_no,
                "ac_name": voter.ac_name,
                "booth_id": voter.booth_id,
                "booth_no": voter.booth_no,
                "booth_name_english": voter.booth_name_english,
                "booth_name_other": voter.booth_name_other,
                "panchayat_ward_id": voter.panchayat_ward_id,
                "pc_district_id": voter.pc_district_id,
                "section_no": voter.section_no,
                "section_name_english": voter.section_name_english,
                "section_name_other": voter.section_name_other,
                "sno": voter.sno,
                "gender": voter.gender,
                "age": voter.age,
                "relation_type": voter.relation_type,
                "relation_name_english": voter.relation_name_english,
                "relation_name_other": voter.relation_name_other,
                "house_no_english": voter.house_no_english,
                "house_no_other": voter.house_no_other,
                "additional_info": {
                    "caste": info.caste if info else None,
                    "mobile": info.mobile if info else None,
                    "voter_status": info.voter_status if info else None,
                    "designation": info.designation if info else None,
                    "vote_status": info.vote_status if info else None,
                    "remarks": info.remarks if info else None,
                    "client_code": info.client_code if info else None
                } if info else {}
            }
            
            voter_data["voters"][voter.voter_id] = voter_info
        
        client_voter_map = VoterService.get_client_voter_map(db, client_id)
        
        if client_voter_map:
            client_voter_map.voter_data = voter_data
            client_voter_map.total_voters = len(voters)
            client_voter_map.updated_at = datetime.utcnow()
        else:
            client_voter_map = ClientVoterMap(
                id=str(uuid.uuid4()),
                client_id=client_id,
                voter_data=voter_data,
                total_voters=len(voters)
            )
            db.add(client_voter_map)
        
        db.commit()
        db.refresh(client_voter_map)
        return client_voter_map
    
    @staticmethod
    def get_client_voter_stats(db: Session, client_id: str) -> Dict[str, Any]:
        """Get statistics for client's voters"""
        client_voter_map = VoterService.get_client_voter_map(db, client_id)
        if not client_voter_map or not client_voter_map.voter_data:
            return {
                "total_voters": 0,
                "by_vote_status": {},
                "by_voter_status": {},
                "by_caste": {},
                "by_gender": {},
                "by_booth": {},
                "by_ac": {}
            }
        
        voters = client_voter_map.voter_data.get("voters", {})
        
        stats = {
            "total_voters": len(voters),
            "by_vote_status": {},
            "by_voter_status": {},
            "by_caste": {},
            "by_gender": {},
            "by_booth": {},
            "by_ac": {}
        }
        
        for voter_info in voters.values():
            vote_status = voter_info.get("additional_info", {}).get("vote_status", "Unknown")
            stats["by_vote_status"][vote_status] = stats["by_vote_status"].get(vote_status, 0) + 1
            
            voter_status = voter_info.get("additional_info", {}).get("voter_status", "Unknown")
            stats["by_voter_status"][voter_status] = stats["by_voter_status"].get(voter_status, 0) + 1
            
            caste = voter_info.get("additional_info", {}).get("caste", "Unknown")
            stats["by_caste"][caste] = stats["by_caste"].get(caste, 0) + 1
            
            gender = voter_info.get("gender", "Unknown")
            stats["by_gender"][gender] = stats["by_gender"].get(gender, 0) + 1
            
            booth = voter_info.get("booth_no", "Unknown")
            stats["by_booth"][booth] = stats["by_booth"].get(booth, 0) + 1
            
            ac = voter_info.get("ac_no", "Unknown")
            stats["by_ac"][ac] = stats["by_ac"].get(ac, 0) + 1
        
        return stats

    # ============================================================
    # EXCEL IMPORT OPERATIONS
    # ============================================================
    
    @staticmethod
    def process_excel_import(
        db: Session,
        client_id: str,
        file_content: bytes,
        filename: str,
        imported_by: str
    ) -> Dict[str, Any]:
        """Process Excel file and import voters"""
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with id {client_id} not found"
            )
        
        try:
            df = pd.read_excel(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Excel file: {str(e)}"
            )
        
        column_mapping = {
            'AC No & name': 'ac_no',
            'Booth No': 'booth_no',
            'Booth Name_Other_Langauge': 'booth_name_other',
            'Booth Name_English': 'booth_name_english',
            'Section No': 'section_no',
            'Section Name_Other_Langauge': 'section_name_other',
            'Section Name_English': 'section_name_english',
            'SNo': 'sno',
            'Name_Other_Langauge': 'name_other',
            'Name_English': 'name_english',
            'Relation Type': 'relation_type',
            'Relation Name_Other_Langauge': 'relation_name_other',
            'Relation Name_English': 'relation_name_english',
            'Gender': 'gender',
            'House No_Other_Langauge': 'house_no_other',
            'House No_English': 'house_no_english',
            'Age': 'age',
            'VoterId': 'voter_id'
        }
        
        additional_mapping = {
            'Caste': 'caste',
            'Mobile': 'mobile',
            'Voter Status': 'voter_status',
            'Designation': 'designation',
            'Vote Status': 'vote_status',
            'Client Code': 'client_code'
        }
        
        results = {
            "total_records": len(df),
            "inserted_records": 0,
            "updated_records": 0,
            "failed_records": 0,
            "errors": [],
            "mapping_stats": {
                "assembly_found": 0,
                "assembly_not_found": 0,
                "booth_found": 0,
                "booth_not_found": 0,
                "panchayat_ward_found": 0,
                "panchayat_ward_not_found": 0,
                "pc_district_found": 0,
                "pc_district_not_found": 0
            }
        }
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row.get('VoterId')) or str(row.get('VoterId')).strip() == '':
                    continue
                
                voter_data = {}
                for excel_col, db_col in column_mapping.items():
                    if excel_col in row and not pd.isna(row[excel_col]):
                        voter_data[db_col] = str(row[excel_col]).strip()
                    else:
                        voter_data[db_col] = None
                
                if 'age' in voter_data and voter_data['age']:
                    try:
                        voter_data['age'] = int(voter_data['age'])
                    except:
                        voter_data['age'] = None
                
                voter = VoterService.create_or_update_voter(db, voter_data)
                
                if voter:
                    if voter.created_at == voter.updated_at:
                        results["inserted_records"] += 1
                    else:
                        results["updated_records"] += 1
                    
                    additional_data = {
                        "voter_id": voter.id,
                        "client_id": client_id,
                        "client_code": client.client_code
                    }
                    
                    if 'Client Code' in row and not pd.isna(row['Client Code']):
                        additional_data['client_code'] = str(row['Client Code']).strip()
                    
                    for excel_col, db_col in additional_mapping.items():
                        if excel_col in row and not pd.isna(row[excel_col]):
                            if db_col != 'client_code':
                                additional_data[db_col] = str(row[excel_col]).strip()
                        else:
                            if db_col not in additional_data:
                                additional_data[db_col] = None
                    
                    if any(additional_data.get(k) for k in ['caste', 'mobile', 'voter_status', 'designation', 'vote_status']):
                        # Create additional info
                        info = VoterAdditionalInfo(
                            id=str(uuid.uuid4()),
                            **additional_data
                        )
                        db.add(info)
                    
                    # Log activity
                    activity = VoterActivityLog(
                        id=str(uuid.uuid4()),
                        voter_id=voter.id,
                        client_id=client_id,
                        user_id=imported_by,
                        activity_type="IMPORTED",
                        activity_description=f"Imported from file: {filename}",
                        activity_data={
                            "row": index + 2,
                            "filename": filename,
                            "assembly_id": voter.assembly_id,
                            "booth_id": voter.booth_id
                        }
                    )
                    db.add(activity)
                
            except Exception as e:
                results["failed_records"] += 1
                results["errors"].append({
                    "row": index + 2,
                    "voter_id": row.get('VoterId', 'Unknown'),
                    "error": str(e)
                })
                continue
        
        db.commit()
        VoterService.update_client_voter_map(db, client_id)
        
        log = VoterImportLog(
            id=str(uuid.uuid4()),
            client_id=client_id,
            filename=filename,
            total_records=results["total_records"],
            inserted_records=results["inserted_records"],
            updated_records=results["updated_records"],
            failed_records=results["failed_records"],
            errors=json.dumps(results["errors"][:100]),
            import_data={
                "imported_by": imported_by,
                "timestamp": datetime.utcnow().isoformat(),
                "mapping_stats": results["mapping_stats"]
            },
            imported_by=imported_by
        )
        db.add(log)
        db.commit()
        
        results["import_id"] = log.id
        return results

    @staticmethod
    def preview_excel(file_content: bytes, rows: int = 5) -> Dict[str, Any]:
        """Preview Excel file before import"""
        try:
            df = pd.read_excel(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Excel file: {str(e)}"
            )
        
        headers = df.columns.tolist()
        
        preview_data = []
        for i in range(min(rows, len(df))):
            row = df.iloc[i].to_dict()
            preview_data.append({
                "row_number": i + 1,
                "data": {str(k): str(v) if pd.notna(v) else None for k, v in row.items()}
            })
        
        return {
            "total_rows": len(df),
            "headers": headers,
            "preview_rows": preview_data
        }

    # ============================================================
    # GROUP OPERATIONS
    # ============================================================
    
    @staticmethod
    def create_group(
        db: Session,
        client_id: str,
        group_name: str,
        created_by: str,
        group_description: Optional[str] = None,
        group_type: str = "STATIC",
        criteria: Optional[Dict[str, Any]] = None
    ) -> VoterGroupMaster:
        """Create a new voter group"""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with id {client_id} not found"
            )
        
        group = VoterGroupMaster(
            id=str(uuid.uuid4()),
            client_id=client_id,
            group_name=group_name,
            group_description=group_description,
            group_type=group_type,
            criteria=criteria,
            created_by=created_by
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        return group
    
    @staticmethod
    def get_groups(
        db: Session,
        client_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get all groups for a client"""
        query = db.query(VoterGroupMaster).filter(
            VoterGroupMaster.client_id == client_id,
            VoterGroupMaster.is_active == True
        )
        
        total = query.count()
        groups = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "groups": groups
        }
    
    @staticmethod
    def add_voters_to_group(
        db: Session,
        group_id: str,
        voter_ids: List[str],
        added_by: str
    ) -> Dict[str, Any]:
        """Add voters to a group"""
        group = db.query(VoterGroupMaster).filter(
            VoterGroupMaster.id == group_id,
            VoterGroupMaster.is_active == True
        ).first()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        added_count = 0
        skipped_count = 0
        errors = []
        
        for voter_id in voter_ids:
            try:
                voter = VoterService.get_voter_by_id(db, voter_id)
                if not voter:
                    errors.append({"voter_id": voter_id, "error": "Voter not found"})
                    continue
                
                existing = db.query(VoterGroupMapping).filter(
                    and_(
                        VoterGroupMapping.group_id == group_id,
                        VoterGroupMapping.voter_id == voter_id
                    )
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                mapping = VoterGroupMapping(
                    id=str(uuid.uuid4()),
                    group_id=group_id,
                    voter_id=voter_id,
                    added_by=added_by
                )
                db.add(mapping)
                added_count += 1
                
            except Exception as e:
                errors.append({"voter_id": voter_id, "error": str(e)})
        
        # Update total voters count
        group.total_voters = db.query(VoterGroupMapping).filter(
            VoterGroupMapping.group_id == group_id
        ).count()
        
        db.commit()
        
        return {
            "added_count": added_count,
            "skipped_count": skipped_count,
            "failed_count": len(errors),
            "errors": errors if errors else None
        }
    
    @staticmethod
    def remove_voters_from_group(
        db: Session,
        group_id: str,
        voter_ids: List[str]
    ) -> Dict[str, Any]:
        """Remove voters from a group"""
        group = db.query(VoterGroupMaster).filter(
            VoterGroupMaster.id == group_id,
            VoterGroupMaster.is_active == True
        ).first()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        removed_count = db.query(VoterGroupMapping).filter(
            and_(
                VoterGroupMapping.group_id == group_id,
                VoterGroupMapping.voter_id.in_(voter_ids)
            )
        ).delete(synchronize_session=False)
        
        group.total_voters = db.query(VoterGroupMapping).filter(
            VoterGroupMapping.group_id == group_id
        ).count()
        
        db.commit()
        
        return {
            "removed_count": removed_count,
            "total_requested": len(voter_ids)
        }