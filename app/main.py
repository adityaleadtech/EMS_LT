# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exception_handlers import setup_exception_handlers

# ========== HIERARCHY ROUTERS ==========
from app.routes.hierarchy import (
    country_router,
    state_router,
    pc_district_router,
    assembly_router,
    block_router,
    panchayat_ward_router,
    polling_booth_router,
    master_router,
    import_router
)

# ========== AUTH ROUTERS ==========
from app.routes.auth.auth import router as auth_router

# ========== CLIENT ROUTERS ==========
from app.routes.client.client import router as client_router
from app.routes.client_admin.client_admin import router as client_admin_router
from app.routes.client_user.client_user import router as client_user_router
from app.routes.client_service.client_service import router as client_services_router

# ========== PLATFORM ROUTERS ==========
from app.routes.platform_users.platform_users import router as platform_users_router
from app.routes.platform_admins.platform_admin import router as platform_admins_router

# ========== SERVICE ROUTERS ==========
from app.routes.service.service import router as service_router

# ========== OTHER ROUTERS ==========
from app.routes.social_media import router as social_media_router
from app.routes.news import router as news_router

# ========== VOTER ROUTER ==========
from app.routes.voter.voter import router as voter_router

app = FastAPI(
    title="Election Management System",
    description="EMS with Hierarchical Master Data Management",
    version="1.0.0"
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# INCLUDE ALL ROUTERS
# ============================================================

# Auth
app.include_router(auth_router)

# Platform
app.include_router(platform_admins_router)
app.include_router(platform_users_router)

# Client
app.include_router(client_router)
app.include_router(client_admin_router)
app.include_router(client_user_router)
app.include_router(client_services_router)

# Services
app.include_router(service_router)

# Hierarchy
app.include_router(country_router)
app.include_router(state_router)
app.include_router(pc_district_router)
app.include_router(assembly_router)
app.include_router(block_router)
app.include_router(panchayat_ward_router)
app.include_router(polling_booth_router)
app.include_router(master_router)
app.include_router(import_router)

# Social Media & News
app.include_router(social_media_router)
app.include_router(news_router)

# ========== VOTER ROUTER ==========
app.include_router(voter_router)


# ============================================================
# ROOT ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "EMS Backend Running",
        "version": "1.0.0",
        "endpoints": {
            "platform": {
                "admins": "/api/v1/platform-admins",
                "users": "/api/v1/platform-users"
            },
            "clients": {
                "base": "/api/v1/clients",
                "admins": "/api/v1/client-admins",
                "users": "/api/v1/client-users",
                "services": "/api/v1/client-services"
            },
            "services": {
                "base": "/api/v1/services"
            },
            "hierarchy": {
                "countries": "/api/v1/hierarchy/countries",
                "states": "/api/v1/hierarchy/states",
                "pc_districts": "/api/v1/hierarchy/pc-districts",
                "assemblies": "/api/v1/hierarchy/assemblies",
                "blocks": "/api/v1/hierarchy/blocks",
                "panchayat_wards": "/api/v1/hierarchy/panchayat-wards",
                "polling_booths": "/api/v1/hierarchy/polling-booths",
                "master": {
                    "tree": "/api/v1/hierarchy/master/tree",
                    "flat": "/api/v1/hierarchy/master/flat",
                    "country_tree": "/api/v1/hierarchy/master/country/{country_id}/tree"
                },
                "import": {
                    "assembly_blocks": "/api/v1/hierarchy/import/assembly-blocks",
                    "template": "/api/v1/hierarchy/import/assembly-blocks/template"
                }
            },
            "social_media": {
                "base": "/api/v1/social-media",
                "by_client": "/api/v1/social-media/client",
                "summary": "/api/v1/social-media/summary/stats"
            },
            "news": {
                "base": "/api/v1/news",
                "by_client": "/api/v1/news/client",
                "by_slug": "/api/v1/news/slug/{slug}",
                "summary": "/api/v1/news/summary/stats"
            },
            "voters": {
                "base": "/api/voters",
                "additional_info": "/api/voters/additional-info",
                "client": "/api/voters/client/{client_id}",
                "client_stats": "/api/voters/client/{client_id}/stats",
                "assign": "/api/voters/client/{client_id}/assign",
                "import_excel": "/api/voters/import/excel/{client_id}",
                "preview_excel": "/api/voters/import/excel/preview",
                "import_logs": "/api/voters/import/logs/{client_id}",
                "groups": "/api/voters/groups",
                "bulk_vote_status": "/api/voters/bulk/vote-status",
                "refresh_cache": "/api/voters/client/{client_id}/refresh-cache"
            }
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "code": 200,
        "timestamp": datetime.utcnow().isoformat()
    }