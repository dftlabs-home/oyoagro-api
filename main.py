"""
FILE: main.py
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import settings
from src.core.database import init_db, close_db
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("=" * 60)
    logger.info("🚀 Oyo-Agro API")
    logger.info("=" * 60)
    
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        if settings.ENVIRONMENT == "development":
            raise
    logger.info("✅ Application ready!")
    yield
    
    logger.info("🛑 Shutting down")
    
    try:
        close_db()
        logger.info("✅ DB connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing connections: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Oyo State Ministry of Agriculture and Rural Development - Farmer Registry API",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


# ============================================================================
# CORE MODULES
# ============================================================================

try:
    from src.auth.router import router as auth_router
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
    logger.info("✅ Auth router registered")
except ImportError:
    logger.warning("⚠️  Auth router not found")


# ============================================================================
# REFERENCE DATA MODULES
# ============================================================================

try:
    from src.associations.router import router as associations_router
    app.include_router(associations_router, prefix=settings.API_V1_PREFIX, tags=["Associations"])
    logger.info("✅ Associations router registered")
except ImportError:
    logger.warning("⚠️  Associations router not found")

try:
    from src.regions.router import router as regions_router
    app.include_router(regions_router, prefix=settings.API_V1_PREFIX, tags=["Regions"])
    logger.info("✅ Regions router registered")
except ImportError:
    logger.warning("⚠️  Regions router not found")

try:
    from src.lgas.router import router as lgas_router
    app.include_router(lgas_router, prefix=settings.API_V1_PREFIX, tags=["LGAs"])
    logger.info("✅ LGAs router registered")
except ImportError:
    logger.warning("⚠️  LGAs router not found")

try:
    from src.seasons.router import router as seasons_router
    app.include_router(seasons_router, prefix=settings.API_V1_PREFIX, tags=["Seasons"])
    logger.info("✅ Seasons router registered")
except ImportError:
    logger.warning("⚠️  Seasons router not found")

try:
    from src.farmtypes.router import router as farmtypes_router
    app.include_router(farmtypes_router, prefix=settings.API_V1_PREFIX, tags=["Farm Types"])
    logger.info("✅ Farm Types router registered")
except ImportError:
    logger.warning("⚠️  Farm Types router not found")

try:
    from src.crops.router import router as crops_router
    app.include_router(crops_router, prefix=settings.API_V1_PREFIX, tags=["Crops"])
    logger.info("✅ Crops router registered")
except ImportError:
    logger.warning("⚠️  Crops router not found")

try:
    from src.livestock.router import router as livestock_router
    app.include_router(livestock_router, prefix=settings.API_V1_PREFIX, tags=["Livestock"])
    logger.info("✅ Livestock router registered")
except ImportError:
    logger.warning("⚠️  Livestock router not found")

try:
    from src.businesstypes.router import router as businesstypes_router
    app.include_router(businesstypes_router, prefix=settings.API_V1_PREFIX, tags=["Business Types"])
    logger.info("✅ Business Types router registered")
except ImportError:
    logger.warning("⚠️  Business Types router not found")

try:
    from src.primaryproducts.router import router as primaryproducts_router
    app.include_router(primaryproducts_router, prefix=settings.API_V1_PREFIX, tags=["Primary Products"])
    logger.info("✅ Primary Products router registered")
except ImportError:
    logger.warning("⚠️  Primary Products router not found")


# ============================================================================
# FARMER & FARM MODULES
# ============================================================================

try:
    from src.farmers.router import router as farmers_router
    app.include_router(farmers_router, prefix=settings.API_V1_PREFIX, tags=["Farmers"])
    logger.info("✅ Farmers router registered")
except ImportError:
    logger.warning("⚠️  Farmers router not found")

try:
    from src.farms.router import router as farms_router
    app.include_router(farms_router, prefix=settings.API_V1_PREFIX, tags=["Farms"])
    logger.info("✅ Farms router registered")
except ImportError:
    logger.warning("⚠️  Farms router not found")


# ============================================================================
# DATA COLLECTION MODULES
# ============================================================================

try:
    from src.cropregistry.router import router as cropregistry_router
    app.include_router(cropregistry_router, prefix=settings.API_V1_PREFIX, tags=["Crop Registry"])
    logger.info("✅ Crop Registry router registered")
except ImportError:
    logger.warning("⚠️  Crop Registry router not found")

try:
    from src.livestockregistry.router import router as livestockregistry_router
    app.include_router(livestockregistry_router, prefix=settings.API_V1_PREFIX, tags=["Livestock Registry"])
    logger.info("✅ Livestock Registry router registered")
except ImportError:
    logger.warning("⚠️  Livestock Registry router not found")

try:
    from src.agroalliedregistry.router import router as agroalliedregistry_router
    app.include_router(agroalliedregistry_router, prefix=settings.API_V1_PREFIX, tags=["Agro-Allied Registry"])
    logger.info("✅ Agro-Allied Registry router registered")
except ImportError:
    logger.warning("⚠️  Agro-Allied Registry router not found")

try:
    from src.notifications.router import router as notifications_router
    app.include_router(notifications_router, prefix=settings.API_V1_PREFIX, tags=["Notifications"])
    logger.info("✅ Notifications router registered")
except ImportError:
    logger.warning("⚠️  Notifications router not found")

try:
    from src.dashboard.router import router as dashboard_router
    app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX, tags=["Dashboard"])
    logger.info("✅ Dashboard router registered")
except ImportError:
    logger.warning("⚠️  Dashboard router not found")

try:
    from src.admin.router import router as admin_router
    app.include_router(admin_router, prefix=settings.API_V1_PREFIX, tags=["Admin"])
    logger.info("✅ Admin router registered")
except ImportError:
    logger.warning("⚠️  Admin router not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD
    )