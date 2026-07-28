from .country import router as country_router
from .state import router as state_router
from .pc_district import router as pc_district_router
from .assembly import router as assembly_router
from .block import router as block_router
from .panchayat_ward import router as panchayat_ward_router
from .polling_booth import router as polling_booth_router

__all__ = [
    'country_router',
    'state_router',
    'pc_district_router',
    'assembly_router',
    'block_router',
    'panchayat_ward_router',
    'polling_booth_router'
]