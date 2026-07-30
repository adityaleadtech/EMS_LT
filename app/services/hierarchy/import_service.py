import pandas as pd
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
import logging
from fastapi import HTTPException, status

from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.block import Block
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.models.hierarchy.polling_booth import PollingBooth
from app.models.hierarchy.pc_district import PCDistrict
from app.models.hierarchy.state import State
from app.models.hierarchy.country import Country
from app.core.exceptions import NotFoundException, DatabaseException, ValidationException

logger = logging.getLogger(__name__)


class ImportService:
    def __init__(self, db: Session):
        self.db = db
        self.stats = {
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0,
            'total_rows': 0,
            'error_messages': [],
            'assembly_created': 0,
            'assembly_updated': 0,
            'block_created': 0,
            'block_updated': 0,
            'panchayat_ward_created': 0,
            'panchayat_ward_updated': 0,
            'polling_booth_created': 0,
            'polling_booth_updated': 0
        }
        self.cache = {
            'assemblies': {},
            'blocks': {},
            'panchayat_wards': {},
            'polling_booths': {},
            'pc_districts': {},
            'states': {},
            'countries': {}
        }

    def load_existing_data(self):
        """Load existing data into cache"""
        # Load assemblies
        assemblies = self.db.query(Assembly).all()
        for a in assemblies:
            key = f"{a.pc_district_id}_{a.code}"
            self.cache['assemblies'][key] = a
        
        # Load blocks
        blocks = self.db.query(Block).all()
        for b in blocks:
            key = f"{b.assembly_id}_{b.code}"
            self.cache['blocks'][key] = b
        
        # Load panchayat wards
        wards = self.db.query(PanchayatWard).all()
        for w in wards:
            key = f"{w.block_id}_{w.code}"
            self.cache['panchayat_wards'][key] = w
        
        # Load polling booths
        booths = self.db.query(PollingBooth).all()
        for b in booths:
            key = f"{b.panchayat_ward_id}_{b.code}"
            self.cache['polling_booths'][key] = b

    def get_pc_district_id(self, code: str, state_code: str = None, country_code: str = None) -> Optional[str]:
        """Get PC District ID by code, with optional state and country filters"""
        query = self.db.query(PCDistrict)
        
        if code:
            query = query.filter(PCDistrict.code == code)
        
        if state_code:
            state = self.db.query(State).filter(State.code == state_code).first()
            if state:
                query = query.filter(PCDistrict.state_id == state.id)
        
        if country_code:
            country = self.db.query(Country).filter(Country.code == country_code).first()
            if country:
                states = self.db.query(State).filter(State.country_id == country.id).all()
                state_ids = [s.id for s in states]
                query = query.filter(PCDistrict.state_id.in_(state_ids))
        
        pc = query.first()
        if pc:
            return pc.id
        return None

    def process_assembly(self, row: dict, update_mode: bool = False) -> Tuple[bool, str]:
        """Process assembly import"""
        try:
            # Required fields
            pc_district_code = row.get('pc_district_code', '').strip()
            assembly_code = row.get('assembly_code', '').strip()
            assembly_name = row.get('assembly_name', '').strip()
            
            if not pc_district_code:
                return False, "Missing pc_district_code"
            if not assembly_code:
                return False, "Missing assembly_code"
            if not assembly_name:
                return False, "Missing assembly_name"
            
            # Get PC District ID
            state_code = row.get('state_code', '').strip()
            country_code = row.get('country_code', '').strip()
            pc_district_id = self.get_pc_district_id(pc_district_code, state_code, country_code)
            
            if not pc_district_id:
                return False, f"PC District not found: {pc_district_code}"
            
            # Check if assembly exists
            key = f"{pc_district_id}_{assembly_code}"
            existing = self.cache['assemblies'].get(key)
            
            if existing and update_mode:
                # UPDATE existing assembly
                assembly = existing
                if row.get('assembly_name'):
                    assembly.name = row.get('assembly_name', '').strip()
                if row.get('assembly_number'):
                    try:
                        assembly.assembly_number = int(row.get('assembly_number'))
                    except:
                        pass
                if row.get('constituency_type'):
                    assembly.constituency_type = row.get('constituency_type', '').strip()
                if row.get('assembly_population'):
                    assembly.population = row.get('assembly_population', '').strip()
                
                self.db.commit()
                self.stats['assembly_updated'] += 1
                self.stats['updated'] += 1
                return True, "Assembly updated"
                
            elif existing and not update_mode:
                self.stats['skipped'] += 1
                return True, "Assembly already exists (skipped)"
            
            # CREATE new assembly
            assembly_number = 0
            if row.get('assembly_number'):
                try:
                    assembly_number = int(row.get('assembly_number'))
                except:
                    assembly_number = 0
            
            assembly = Assembly(
                id=str(uuid4()),
                pc_district_id=pc_district_id,
                code=assembly_code,
                name=assembly_name,
                assembly_number=assembly_number,
                constituency_type=row.get('constituency_type', '').strip() or 'General',
                population=row.get('assembly_population', '').strip() or '',
                is_active=True
            )
            self.db.add(assembly)
            self.db.flush()
            self.cache['assemblies'][key] = assembly
            self.stats['assembly_created'] += 1
            self.stats['created'] += 1
            return True, "Assembly created"
            
        except Exception as e:
            return False, str(e)

    def process_block(self, row: dict, update_mode: bool = False) -> Tuple[bool, str]:
        """Process block import"""
        try:
            # Required fields
            assembly_code = row.get('assembly_code', '').strip()
            block_code = row.get('block_code', '').strip()
            block_name = row.get('block_name', '').strip()
            
            if not assembly_code:
                return False, "Missing assembly_code"
            if not block_code:
                return False, "Missing block_code"
            if not block_name:
                return False, "Missing block_name"
            
            # Get Assembly ID
            pc_district_code = row.get('pc_district_code', '').strip()
            assembly = None
            if pc_district_code:
                pc_district_id = self.get_pc_district_id(pc_district_code)
                if pc_district_id:
                    assembly = self.db.query(Assembly).filter(
                        Assembly.pc_district_id == pc_district_id,
                        Assembly.code == assembly_code
                    ).first()
            
            if not assembly:
                # Try to find by code only
                assembly = self.db.query(Assembly).filter(
                    Assembly.code == assembly_code
                ).first()
            
            if not assembly:
                return False, f"Assembly not found: {assembly_code}"
            
            # Check if block exists
            key = f"{assembly.id}_{block_code}"
            existing = self.cache['blocks'].get(key)
            
            if existing and update_mode:
                # UPDATE existing block
                block = existing
                if row.get('block_name'):
                    block.name = row.get('block_name', '').strip()
                if row.get('block_number'):
                    try:
                        block.block_number = int(row.get('block_number'))
                    except:
                        pass
                if row.get('block_type'):
                    block.block_type = row.get('block_type', '').strip()
                if row.get('block_area'):
                    block.area = row.get('block_area', '').strip()
                
                self.db.commit()
                self.stats['block_updated'] += 1
                self.stats['updated'] += 1
                return True, "Block updated"
                
            elif existing and not update_mode:
                self.stats['skipped'] += 1
                return True, "Block already exists (skipped)"
            
            # CREATE new block
            block = Block(
                id=str(uuid4()),
                assembly_id=assembly.id,
                code=block_code,
                name=block_name,
                block_number=int(row.get('block_number', 0)) if row.get('block_number') else 0,
                block_type=row.get('block_type', '').strip() or 'Urban',
                area=row.get('block_area', '').strip() or '',
                is_active=True
            )
            self.db.add(block)
            self.db.flush()
            self.cache['blocks'][key] = block
            self.stats['block_created'] += 1
            self.stats['created'] += 1
            return True, "Block created"
            
        except Exception as e:
            return False, str(e)

    def process_panchayat_ward(self, row: dict, update_mode: bool = False) -> Tuple[bool, str]:
        """Process panchayat ward import"""
        try:
            # Required fields
            block_code = row.get('block_code', '').strip()
            panchayat_ward_code = row.get('panchayat_ward_code', '').strip()
            panchayat_ward_name = row.get('panchayat_ward_name', '').strip()
            
            if not block_code:
                return False, "Missing block_code"
            if not panchayat_ward_code:
                return False, "Missing panchayat_ward_code"
            if not panchayat_ward_name:
                return False, "Missing panchayat_ward_name"
            
            # Get Block ID
            assembly_code = row.get('assembly_code', '').strip()
            block = self.db.query(Block).filter(Block.code == block_code).first()
            
            if not block and assembly_code:
                block = self.db.query(Block).join(Assembly).filter(
                    Assembly.code == assembly_code,
                    Block.code == block_code
                ).first()
            
            if not block:
                return False, f"Block not found: {block_code}"
            
            # Check if ward exists
            key = f"{block.id}_{panchayat_ward_code}"
            existing = self.cache['panchayat_wards'].get(key)
            
            if existing and update_mode:
                # UPDATE existing ward
                ward = existing
                if row.get('panchayat_ward_name'):
                    ward.name = row.get('panchayat_ward_name', '').strip()
                if row.get('ward_number'):
                    try:
                        ward.ward_number = int(row.get('ward_number'))
                    except:
                        pass
                if row.get('ward_type'):
                    ward.ward_type = row.get('ward_type', '').strip()
                if row.get('pincode'):
                    ward.pincode = row.get('pincode', '').strip()
                if row.get('ward_population'):
                    try:
                        ward.population = int(row.get('ward_population'))
                    except:
                        pass
                
                self.db.commit()
                self.stats['panchayat_ward_updated'] += 1
                self.stats['updated'] += 1
                return True, "Panchayat Ward updated"
                
            elif existing and not update_mode:
                self.stats['skipped'] += 1
                return True, "Panchayat Ward already exists (skipped)"
            
            # CREATE new ward
            ward = PanchayatWard(
                id=str(uuid4()),
                block_id=block.id,
                code=panchayat_ward_code,
                name=panchayat_ward_name,
                ward_number=int(row.get('ward_number', 0)) if row.get('ward_number') else 0,
                ward_type=row.get('ward_type', '').strip() or 'Urban',
                population=int(row.get('ward_population', 0)) if row.get('ward_population') else None,
                pincode=row.get('pincode', '').strip() or '',
                is_active=True
            )
            self.db.add(ward)
            self.db.flush()
            self.cache['panchayat_wards'][key] = ward
            self.stats['panchayat_ward_created'] += 1
            self.stats['created'] += 1
            return True, "Panchayat Ward created"
            
        except Exception as e:
            return False, str(e)

    def process_polling_booth(self, row: dict, update_mode: bool = False) -> Tuple[bool, str]:
        """Process polling booth import"""
        try:
            # Required fields
            panchayat_ward_code = row.get('panchayat_ward_code', '').strip()
            booth_code = row.get('booth_code', '').strip()
            booth_name = row.get('booth_name', '').strip()
            
            if not panchayat_ward_code:
                return False, "Missing panchayat_ward_code"
            if not booth_code:
                return False, "Missing booth_code"
            if not booth_name:
                return False, "Missing booth_name"
            
            # Get Panchayat Ward ID
            block_code = row.get('block_code', '').strip()
            ward = self.db.query(PanchayatWard).filter(
                PanchayatWard.code == panchayat_ward_code
            ).first()
            
            if not ward and block_code:
                ward = self.db.query(PanchayatWard).join(Block).filter(
                    Block.code == block_code,
                    PanchayatWard.code == panchayat_ward_code
                ).first()
            
            if not ward:
                return False, f"Panchayat Ward not found: {panchayat_ward_code}"
            
            # Check if booth exists
            key = f"{ward.id}_{booth_code}"
            existing = self.cache['polling_booths'].get(key)
            
            if existing and update_mode:
                # UPDATE existing booth
                booth = existing
                if row.get('booth_name'):
                    booth.name = row.get('booth_name', '').strip()
                if row.get('booth_number'):
                    try:
                        booth.booth_number = int(row.get('booth_number'))
                    except:
                        pass
                if row.get('address'):
                    booth.address = row.get('address', '').strip()
                if row.get('polling_station_type'):
                    polling_type = row.get('polling_station_type', '').strip().upper()
                    if polling_type in ['PERMANENT', 'TEMPORARY', 'MOBILE']:
                        booth.polling_station_type = polling_type
                if row.get('booth_capacity'):
                    try:
                        booth.capacity = int(row.get('booth_capacity'))
                    except:
                        pass
                if row.get('is_accessible') is not None:
                    booth.is_accessible = str(row.get('is_accessible')).lower() == 'true'
                
                self.db.commit()
                self.stats['polling_booth_updated'] += 1
                self.stats['updated'] += 1
                return True, "Polling Booth updated"
                
            elif existing and not update_mode:
                self.stats['skipped'] += 1
                return True, "Polling Booth already exists (skipped)"
            
            # CREATE new booth
            booth_number = 0
            if row.get('booth_number'):
                try:
                    booth_number = int(row.get('booth_number'))
                except:
                    booth_number = 0
            
            polling_type = row.get('polling_station_type', '').strip().upper()
            if polling_type not in ['PERMANENT', 'TEMPORARY', 'MOBILE']:
                polling_type = 'PERMANENT'
            
            booth = PollingBooth(
                id=str(uuid4()),
                panchayat_ward_id=ward.id,
                code=booth_code,
                name=booth_name,
                booth_number=booth_number,
                address=row.get('address', '').strip() or '',
                latitude=float(row.get('latitude', 0)) if row.get('latitude') else None,
                longitude=float(row.get('longitude', 0)) if row.get('longitude') else None,
                polling_station_type=polling_type,
                capacity=int(row.get('booth_capacity', 0)) if row.get('booth_capacity') else None,
                facilities=row.get('facilities', '').strip() or '',
                is_accessible=bool(str(row.get('is_accessible', 'true')).lower() == 'true'),
                is_active=True
            )
            self.db.add(booth)
            self.stats['polling_booth_created'] += 1
            self.stats['created'] += 1
            return True, "Polling Booth created"
            
        except Exception as e:
            return False, str(e)

    def process_row(self, row: dict, update_mode: bool = False) -> Tuple[bool, str]:
        """Process a single row - Assembly, Block, Ward, Booth"""
        try:
            # Check what data is present and process accordingly
            has_assembly = bool(row.get('assembly_code', '').strip())
            has_block = bool(row.get('block_code', '').strip())
            has_ward = bool(row.get('panchayat_ward_code', '').strip())
            has_booth = bool(row.get('booth_code', '').strip())
            
            # Process Assembly if present
            if has_assembly:
                success, msg = self.process_assembly(row, update_mode)
                if not success:
                    return False, msg
            
            # Process Block if present
            if has_block:
                success, msg = self.process_block(row, update_mode)
                if not success:
                    return False, msg
            
            # Process Panchayat Ward if present
            if has_ward:
                success, msg = self.process_panchayat_ward(row, update_mode)
                if not success:
                    return False, msg
            
            # Process Polling Booth if present
            if has_booth:
                success, msg = self.process_polling_booth(row, update_mode)
                if not success:
                    return False, msg
            
            return True, "Row processed successfully"
            
        except Exception as e:
            return False, str(e)

    def import_assembly_blocks(self, file_path: str, update_mode: bool = False) -> Dict:
        """Import Assembly and Blocks from Excel"""
        try:
            print(f"📂 Reading file: {file_path}")
            
            # Read Excel file
            df = pd.read_excel(file_path, dtype=str)
            
            # Clean column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            print(f"📊 Found {len(df)} rows")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Load existing data
            self.load_existing_data()
            
            # Process each row
            total_rows = len(df)
            self.stats['total_rows'] = total_rows
            
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                print(f"\n--- Processing row {index + 1} ---")
                success, message = self.process_row(row_dict, update_mode)
                
                if not success:
                    self.stats['errors'] += 1
                    self.stats['error_messages'].append(f"Row {index + 2}: {message}")
                
                # Commit every 50 rows
                if index % 50 == 0 and index > 0:
                    self.db.commit()
                    print(f"💾 Committed changes so far...")
            
            # Final commit
            self.db.commit()
            print("💾 Final commit completed!")
            
            # Generate summary
            summary = {
                'total_rows': self.stats['total_rows'],
                'created': self.stats['created'],
                'updated': self.stats['updated'],
                'skipped': self.stats['skipped'],
                'errors': self.stats['errors'],
                'error_messages': self.stats['error_messages'][:10],
                'assembly_created': self.stats['assembly_created'],
                'assembly_updated': self.stats['assembly_updated'],
                'block_created': self.stats['block_created'],
                'block_updated': self.stats['block_updated'],
                'panchayat_ward_created': self.stats['panchayat_ward_created'],
                'panchayat_ward_updated': self.stats['panchayat_ward_updated'],
                'polling_booth_created': self.stats['polling_booth_created'],
                'polling_booth_updated': self.stats['polling_booth_updated']
            }
            
            print(f"\n📊 Import Summary:")
            for key, value in summary.items():
                if key != 'error_messages':
                    print(f"  - {key}: {value}")
            
            return {
                'status': 'success',
                'mode': 'update' if update_mode else 'create',
                'summary': summary
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Import failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Import failed: {str(e)}"
            )

    def import_from_excel(self, file_path: str, update_mode: bool = False) -> Dict:
        """Main import function"""
        return self.import_assembly_blocks(file_path, update_mode)

    def import_from_dataframe(self, df: pd.DataFrame, update_mode: bool = False) -> Dict:
        """Import from pandas DataFrame"""
        try:
            # Clean column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            print(f"📊 Found {len(df)} rows")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Load existing data
            self.load_existing_data()
            
            # Process each row
            total_rows = len(df)
            self.stats['total_rows'] = total_rows
            
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                success, message = self.process_row(row_dict, update_mode)
                
                if not success:
                    self.stats['errors'] += 1
                    self.stats['error_messages'].append(f"Row {index + 2}: {message}")
                
                # Commit every 50 rows
                if index % 50 == 0 and index > 0:
                    self.db.commit()
                    print(f"💾 Committed changes so far...")
            
            # Final commit
            self.db.commit()
            
            summary = {
                'total_rows': self.stats['total_rows'],
                'created': self.stats['created'],
                'updated': self.stats['updated'],
                'skipped': self.stats['skipped'],
                'errors': self.stats['errors'],
                'error_messages': self.stats['error_messages'][:10],
                'assembly_created': self.stats['assembly_created'],
                'assembly_updated': self.stats['assembly_updated'],
                'block_created': self.stats['block_created'],
                'block_updated': self.stats['block_updated'],
                'panchayat_ward_created': self.stats['panchayat_ward_created'],
                'panchayat_ward_updated': self.stats['panchayat_ward_updated'],
                'polling_booth_created': self.stats['polling_booth_created'],
                'polling_booth_updated': self.stats['polling_booth_updated']
            }
            
            return {
                'status': 'success',
                'mode': 'update' if update_mode else 'create',
                'summary': summary
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Import failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Import failed: {str(e)}"
            )