from sqlalchemy.orm import Session
from typing import Optional
from app.models.hierarchy.country import Country
from app.models.hierarchy.state import State
from app.models.hierarchy.pc_district import PCDistrict
from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.block import Block
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.models.hierarchy.polling_booth import PollingBooth
from app.schemas.hierarchy.master import (
    BaseNode,
    CountryNode,
    StateNode,
    PCDistrictNode,
    AssemblyNode,
    BlockNode,
    PanchayatWardNode,
    PollingBoothNode,
    HierarchyMasterResponse,
    HierarchyFlatResponse
)


class MasterService:
    def __init__(self, db: Session):
        self.db = db

    def get_complete_hierarchy(self, country_id: Optional[str] = None, is_active: Optional[bool] = True) -> HierarchyMasterResponse:
        """Get complete hierarchical data with only id and name"""
        
        # Build query
        query = self.db.query(Country)
        if country_id:
            query = query.filter(Country.id == country_id)
        if is_active is not None:
            query = query.filter(Country.is_active == is_active)
        
        countries = query.all()
        
        result = []
        for country in countries:
            # Get states for this country
            states_query = self.db.query(State).filter(
                State.country_id == country.id
            )
            if is_active is not None:
                states_query = states_query.filter(State.is_active == is_active)
            states = states_query.all()
            
            state_nodes = []
            for state in states:
                # Get PC districts for this state
                pc_query = self.db.query(PCDistrict).filter(
                    PCDistrict.state_id == state.id
                )
                if is_active is not None:
                    pc_query = pc_query.filter(PCDistrict.is_active == is_active)
                pc_districts = pc_query.all()
                
                pc_nodes = []
                for pc in pc_districts:
                    # Get assemblies for this PC district
                    assembly_query = self.db.query(Assembly).filter(
                        Assembly.pc_district_id == pc.id
                    )
                    if is_active is not None:
                        assembly_query = assembly_query.filter(Assembly.is_active == is_active)
                    assemblies = assembly_query.all()
                    
                    assembly_nodes = []
                    for assembly in assemblies:
                        # Get blocks for this assembly
                        block_query = self.db.query(Block).filter(
                            Block.assembly_id == assembly.id
                        )
                        if is_active is not None:
                            block_query = block_query.filter(Block.is_active == is_active)
                        blocks = block_query.all()
                        
                        block_nodes = []
                        for block in blocks:
                            # Get panchayat wards for this block
                            ward_query = self.db.query(PanchayatWard).filter(
                                PanchayatWard.block_id == block.id
                            )
                            if is_active is not None:
                                ward_query = ward_query.filter(PanchayatWard.is_active == is_active)
                            wards = ward_query.all()
                            
                            ward_nodes = []
                            for ward in wards:
                                # Get polling booths for this ward
                                booth_query = self.db.query(PollingBooth).filter(
                                    PollingBooth.panchayat_ward_id == ward.id
                                )
                                if is_active is not None:
                                    booth_query = booth_query.filter(PollingBooth.is_active == is_active)
                                booths = booth_query.all()
                                
                                booth_nodes = [
                                    PollingBoothNode(
                                        id=booth.id,
                                        name=booth.name
                                    )
                                    for booth in booths
                                ]
                                
                                ward_nodes.append(
                                    PanchayatWardNode(
                                        id=ward.id,
                                        name=ward.name,
                                        polling_booths=booth_nodes
                                    )
                                )
                            
                            block_nodes.append(
                                BlockNode(
                                    id=block.id,
                                    name=block.name,
                                    panchayat_wards=ward_nodes
                                )
                            )
                        
                        assembly_nodes.append(
                            AssemblyNode(
                                id=assembly.id,
                                name=assembly.name,
                                blocks=block_nodes
                            )
                        )
                    
                    pc_nodes.append(
                        PCDistrictNode(
                            id=pc.id,
                            name=pc.name,
                            assemblies=assembly_nodes
                        )
                    )
                
                state_nodes.append(
                    StateNode(
                        id=state.id,
                        name=state.name,
                        pc_districts=pc_nodes
                    )
                )
            
            result.append(
                CountryNode(
                    id=country.id,
                    name=country.name,
                    states=state_nodes
                )
            )
        
        return HierarchyMasterResponse(
            total_countries=len(result),
            countries=result
        )

    def get_flat_hierarchy(self, is_active: Optional[bool] = True) -> HierarchyFlatResponse:
        """Get flat lists of all items with only id and name"""
        
        # Get all items from each level
        countries = self.db.query(Country)
        states = self.db.query(State)
        pc_districts = self.db.query(PCDistrict)
        assemblies = self.db.query(Assembly)
        blocks = self.db.query(Block)
        panchayat_wards = self.db.query(PanchayatWard)
        polling_booths = self.db.query(PollingBooth)
        
        if is_active is not None:
            countries = countries.filter(Country.is_active == is_active)
            states = states.filter(State.is_active == is_active)
            pc_districts = pc_districts.filter(PCDistrict.is_active == is_active)
            assemblies = assemblies.filter(Assembly.is_active == is_active)
            blocks = blocks.filter(Block.is_active == is_active)
            panchayat_wards = panchayat_wards.filter(PanchayatWard.is_active == is_active)
            polling_booths = polling_booths.filter(PollingBooth.is_active == is_active)
        
        return HierarchyFlatResponse(
            countries=[BaseNode(id=c.id, name=c.name) for c in countries.all()],
            states=[BaseNode(id=s.id, name=s.name) for s in states.all()],
            pc_districts=[BaseNode(id=p.id, name=p.name) for p in pc_districts.all()],
            assemblies=[BaseNode(id=a.id, name=a.name) for a in assemblies.all()],
            blocks=[BaseNode(id=b.id, name=b.name) for b in blocks.all()],
            panchayat_wards=[BaseNode(id=pw.id, name=pw.name) for pw in panchayat_wards.all()],
            polling_booths=[BaseNode(id=pb.id, name=pb.name) for pb in polling_booths.all()]
        )