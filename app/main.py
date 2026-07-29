from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.platform_admins.platform_admin import router as platform_admin_router

# Import existing routes

# Import hierarchy routes
from app.routes.hierarchy import (
    country_router,
    state_router,
    pc_district_router,
    assembly_router,
    block_router,
    panchayat_ward_router,
    polling_booth_router
)

app = FastAPI(
    title="Election Management System",
    description="EMS with Hierarchical Master Data Management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include hierarchy routers
app.include_router(country_router)
app.include_router(state_router)
app.include_router(pc_district_router)
app.include_router(assembly_router)
app.include_router(block_router)
app.include_router(panchayat_ward_router)
app.include_router(polling_booth_router)

app.include_router(platform_admin_router)

@app.get("/")
def root():
    return {
        "message": "EMS Backend Running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "clients": "/api/v1/clients",
            "hierarchy": {
                "countries": "/api/v1/hierarchy/countries",
                "states": "/api/v1/hierarchy/states",
                "pc_districts": "/api/v1/hierarchy/pc-districts",
                "assemblies": "/api/v1/hierarchy/assemblies",
                "blocks": "/api/v1/hierarchy/blocks",
                "panchayat_wards": "/api/v1/hierarchy/panchayat-wards",
                "polling_booths": "/api/v1/hierarchy/polling-booths"
            }
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}