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
            raise  # Re-raise in development
        # In production, you might want to continue with limited functionality
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

try:
    from src.auth.router import router as auth_router
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
except ImportError:
    logger.warning("⚠️  Auth router not found - create src/auth/router.py")

try:
    from src.associations.router import router as associations_router
    app.include_router(associations_router, prefix=settings.API_V1_PREFIX, tags=["Associations"])
except ImportError:
    logger.warning("⚠️  Farmers router not found - create src/associations/router.py")

try:
    from src.regions.router import router as regions_router
    app.include_router(regions_router, prefix=settings.API_V1_PREFIX, tags=["Regions"])
except ImportError:
    logger.warning("⚠️  Farmers router not found - create src/regions/router.py")

try:
    from src.lgas.router import router as lgas_router
    app.include_router(lgas_router, prefix=settings.API_V1_PREFIX, tags=["LGAS"])
except ImportError:
    logger.warning("⚠️  Farmers router not found - create src/lgas/router.py")

try:
    from src.seasons.router import router as seasons_router
    app.include_router(seasons_router, prefix=settings.API_V1_PREFIX, tags=["Seasons"])
except ImportError:
    logger.warning("⚠️  Farmers router not found - create src/seasons/router.py")

try:
    from src.farmtypes.router import router as farmtypes_router
    app.include_router(farmtypes_router, prefix=settings.API_V1_PREFIX, tags=["Farm Types"])
except ImportError:
    logger.warning("⚠️  Farmers router not found - create src/farmtypes/router.py")

try:
    from src.farmers.router import router as farmers_router
    app.include_router(farmers_router, prefix=settings.API_V1_PREFIX, tags=["Farmers"])
except ImportError:
    logger.warning("⚠️  Farmers router not found - create src/farmers/router.py")

try:
    from src.farms.router import router as farms_router
    app.include_router(farms_router, prefix=settings.API_V1_PREFIX, tags=["Farms"])
except ImportError:
    logger.warning("⚠️  Farms router not found - create src/farms/router.py")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD
    )